import os
from pathlib import Path
from dotenv import load_dotenv

# Lade globale Config zuerst, dann lokale (falls vorhanden)
global_env = Path.home() / '.raggadon.env'
if global_env.exists():
    load_dotenv(global_env)
else:
    load_dotenv()  # Fallback auf lokale .env

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.supabase_client import SupabaseClient
from app.embedding import EmbeddingService
from app.usage import UsageTracker

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
        logger.info(f"💾 Content: {request.content[:100]}...")
        
        # Test embedding service first
        logger.info("🧠 Creating embedding...")
        embedding_result = await embedding_service.create_embedding(request.content)
        embedding_vector = embedding_result["embedding"]
        tokens_used = embedding_result["tokens"]
        logger.info(f"🧠 Embedding created: {tokens_used} tokens")
        
        # Test supabase save
        logger.info("💾 Saving to Supabase...")
        await supabase_client.save_memory(
            project=request.project,
            role=request.role,
            content=request.content,
            embedding=embedding_vector,
        )
        logger.info("💾 Saved to Supabase successfully")
        
        # Test usage tracking (optional - table might not exist)
        logger.info("📊 Tracking usage...")
        monthly_usage = 0
        estimated_cost = 0.0
        try:
            await usage_tracker.track_usage(
                project=request.project,
                usage_type="save",
                tokens=tokens_used,
            )
            monthly_usage = await usage_tracker.get_monthly_usage(request.project)
            estimated_cost = monthly_usage * 0.00002
        except Exception as usage_error:
            logger.warning(f"⚠️ Usage tracking failed (table might not exist): {str(usage_error)}")
            # Continue without usage tracking
            monthly_usage = tokens_used  # Just use current tokens
            estimated_cost = (tokens_used / 1000) * 0.00002
        
        logger.info(f"🧾 Tokenverbrauch: {monthly_usage:,} Tokens (~${estimated_cost:.4f}) für Projekt '{request.project}'")
        
        return SaveResponse(
            success=True,
            message=f"Inhalt für Projekt '{request.project}' gespeichert",
            tokens_used=tokens_used,
            monthly_project_usage=monthly_usage,
            estimated_cost_usd=estimated_cost,
        )
        
    except Exception as e:
        error_msg = f"Fehler beim Speichern: {str(e)} | Type: {type(e).__name__}"
        logger.error(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


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
        
        # Track usage (optional - table might not exist)
        monthly_usage = 0
        estimated_cost = 0.0
        try:
            await usage_tracker.track_usage(
                project=project,
                usage_type="search",
                tokens=tokens_used,
            )
            monthly_usage = await usage_tracker.get_monthly_usage(project)
            estimated_cost = monthly_usage * 0.00002
        except Exception as usage_error:
            logger.warning(f"⚠️ Usage tracking failed: {str(usage_error)}")
            monthly_usage = tokens_used
            estimated_cost = (tokens_used / 1000) * 0.00002
        
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
        # Hole Projekt-Informationen
        memories = await supabase_client.count_project_memories(project)
        first_activity = await supabase_client.get_first_activity(project)
        last_activity = await supabase_client.get_last_activity(project)
        
        # Optional: Token-Usage (falls Tabelle existiert)
        monthly_usage = 0
        estimated_cost = 0.0
        recent_activities = []
        try:
            monthly_usage = await usage_tracker.get_monthly_usage(project)
            estimated_cost = monthly_usage * 0.00002
            recent_activities = await usage_tracker.get_recent_activities(project, limit=5)
        except Exception as usage_error:
            logger.warning(f"⚠️ Usage tracking nicht verfügbar: {str(usage_error)}")
            # Fallback values
            monthly_usage = 0
            estimated_cost = 0.0
            recent_activities = []
        
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