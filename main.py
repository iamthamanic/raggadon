import os
from dotenv import load_dotenv
load_dotenv()
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from app.supabase_client import SupabaseClient
from app.embedding import EmbeddingService
from app.usage import UsageTracker

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SaveRequest(BaseModel):
    project: str
    role: str
    content: str


class SearchRequest(BaseModel):
    project: str
    query: str


class SaveResponse(BaseModel):
    success: bool
    message: str
    tokens_used: int
    monthly_project_usage: int
    estimated_cost_usd: float


class SearchResponse(BaseModel):
    results: list[Dict[str, Any]]
    tokens_used: int
    monthly_project_usage: int
    estimated_cost_usd: float


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Raggadon RAG-Middleware startet...")
    yield
    logger.info("🛑 Raggadon RAG-Middleware beendet.")


app = FastAPI(
    title="Raggadon RAG-Middleware",
    description="RAG-System für projektbasiertes Gedächtnis mit Claude",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase_client = SupabaseClient()
embedding_service = EmbeddingService()
usage_tracker = UsageTracker(supabase_client)


@app.post("/save", response_model=SaveResponse)
async def save_memory(request: SaveRequest):
    """Speichert Projektinhalt mit Embedding in Supabase"""
    try:
        logger.info(f"💾 Speichere Inhalt für Projekt: {request.project}")
        
        embedding_result = await embedding_service.create_embedding(request.content)
        embedding_vector = embedding_result["embedding"]
        tokens_used = embedding_result["tokens"]
        
        await supabase_client.save_memory(
            project=request.project,
            role=request.role,
            content=request.content,
            embedding=embedding_vector,
        )
        
        await usage_tracker.track_usage(
            project=request.project,
            usage_type="save",
            tokens=tokens_used,
        )
        
        monthly_usage = await usage_tracker.get_monthly_usage(request.project)
        estimated_cost = monthly_usage * 0.00002
        
        logger.info(f"🧾 Tokenverbrauch: {monthly_usage:,} Tokens (~${estimated_cost:.4f}) für Projekt '{request.project}'")
        
        return SaveResponse(
            success=True,
            message=f"Inhalt für Projekt '{request.project}' gespeichert",
            tokens_used=tokens_used,
            monthly_project_usage=monthly_usage,
            estimated_cost_usd=estimated_cost,
        )
        
    except Exception as e:
        logger.error(f"❌ Fehler beim Speichern: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search", response_model=SearchResponse)
async def search_memory(project: str, query: str):
    """Sucht ähnliche Inhalte im Projektgedächtnis"""
    try:
        logger.info(f"🔍 Suche in Projekt: {project}")
        
        embedding_result = await embedding_service.create_embedding(query)
        query_embedding = embedding_result["embedding"]
        tokens_used = embedding_result["tokens"]
        
        results = await supabase_client.search_memory(
            project=project,
            query_embedding=query_embedding,
            limit=5,
        )
        
        await usage_tracker.track_usage(
            project=project,
            usage_type="search",
            tokens=tokens_used,
        )
        
        monthly_usage = await usage_tracker.get_monthly_usage(project)
        estimated_cost = monthly_usage * 0.00002
        
        logger.info(f"🧾 Tokenverbrauch: {monthly_usage:,} Tokens (~${estimated_cost:.4f}) für Projekt '{project}'")
        logger.info(f"✅ {len(results)} Ergebnisse gefunden")
        
        return SearchResponse(
            results=results,
            tokens_used=tokens_used,
            monthly_project_usage=monthly_usage,
            estimated_cost_usd=estimated_cost,
        )
        
    except Exception as e:
        logger.error(f"❌ Fehler bei der Suche: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health Check Endpoint"""
    return {"status": "healthy", "service": "Raggadon RAG-Middleware"}


@app.get("/project/{project}/stats")
async def get_project_stats(project: str):
    """Gibt Statistiken für ein Projekt zurück"""
    try:
        # Hole monatliche Token-Usage
        monthly_usage = await usage_tracker.get_monthly_usage(project)
        estimated_cost = monthly_usage * 0.00002
        
        # Zähle Einträge im Projekt
        memories = await supabase_client.count_project_memories(project)
        
        # Hole die letzten Aktivitäten
        recent_activities = await usage_tracker.get_recent_activities(project, limit=5)
        
        # Hole erste und letzte Aktivität
        first_activity = await supabase_client.get_first_activity(project)
        last_activity = await supabase_client.get_last_activity(project)
        
        return {
            "project": project,
            "total_memories": memories,
            "monthly_tokens": monthly_usage,
            "estimated_monthly_cost_usd": estimated_cost,
            "recent_activities": recent_activities,
            "cost_per_1k_tokens": 0.02,  # $0.02 per 1K tokens
            "model": "text-embedding-3-small",
            "first_activity": first_activity,
            "last_activity": last_activity
        }
        
    except Exception as e:
        logger.error(f"❌ Fehler beim Abrufen der Projekt-Statistiken: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)