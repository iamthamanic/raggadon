import os
import logging
from typing import List, Dict, Any
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class SupabaseClient:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_API_KEY")
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL und SUPABASE_API_KEY müssen gesetzt sein")
        
        self.client: Client = create_client(self.url, self.key)
        logger.info("✅ Supabase Client initialisiert")

    async def save_memory(
        self, 
        project: str, 
        role: str, 
        content: str, 
        embedding: List[float]
    ) -> Dict[str, Any]:
        """Speichert Projektinhalt mit Embedding in project_memory Tabelle"""
        try:
            data = {
                "project": project,
                "role": role,
                "content": content,
                "embedding": embedding,
            }
            
            result = self.client.table("project_memory").insert(data).execute()
            
            if result.data:
                logger.info(f"💾 Erfolgreich gespeichert: {len(content)} Zeichen für Projekt '{project}'")
                return result.data[0]
            else:
                raise Exception("Keine Daten zurückgegeben")
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Speichern in Supabase: {str(e)}")
            raise

    async def search_memory(
        self, 
        project: str, 
        query_embedding: List[float], 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Sucht ähnliche Inhalte basierend auf Cosine Similarity"""
        try:
            # Verwende RPC (Remote Procedure Call) für Vektor-Ähnlichkeitssuche
            result = self.client.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": 0.78,
                    "match_count": limit,
                    "project_filter": project,
                }
            ).execute()
            
            if result.data:
                logger.info(f"🔍 {len(result.data)} ähnliche Einträge für Projekt '{project}' gefunden")
                return result.data
            else:
                logger.info(f"🔍 Keine ähnlichen Einträge für Projekt '{project}' gefunden")
                return []
                
        except Exception as e:
            logger.error(f"❌ Fehler bei der Suche in Supabase: {str(e)}")
            raise

    async def create_tables_if_not_exist(self):
        """Erstellt notwendige Tabellen falls sie nicht existieren"""
        try:
            # Prüfe ob project_memory Tabelle existiert
            result = self.client.table("project_memory").select("id").limit(1).execute()
            logger.info("✅ project_memory Tabelle existiert bereits")
        except Exception:
            logger.warning("⚠️ project_memory Tabelle nicht gefunden - bitte manuell erstellen")
            
        try:
            # Prüfe ob embedding_usage Tabelle existiert
            result = self.client.table("embedding_usage").select("id").limit(1).execute()
            logger.info("✅ embedding_usage Tabelle existiert bereits")
        except Exception:
            logger.warning("⚠️ embedding_usage Tabelle nicht gefunden - bitte manuell erstellen")