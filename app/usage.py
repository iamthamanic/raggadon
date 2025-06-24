import logging
from datetime import datetime, timezone
from typing import Dict, Any
from app.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)


class UsageTracker:
    def __init__(self, supabase_client: SupabaseClient):
        self.supabase = supabase_client
        logger.info("✅ Usage Tracker initialisiert")

    async def track_usage(
        self, 
        project: str, 
        usage_type: str, 
        tokens: int
    ) -> Dict[str, Any]:
        """Speichert Token-Verbrauch in embedding_usage Tabelle"""
        try:
            data = {
                "project": project,
                "usage_type": usage_type,
                "tokens": tokens,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            
            result = self.supabase.client.table("embedding_usage").insert(data).execute()
            
            if result.data:
                logger.info(f"📊 Usage getrackt: {tokens} Tokens ({usage_type}) für Projekt '{project}'")
                return result.data[0]
            else:
                raise Exception("Keine Daten zurückgegeben")
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Tracking der Usage: {str(e)}")
            raise

    async def get_monthly_usage(self, project: str) -> int:
        """Ermittelt den monatlichen Token-Verbrauch für ein Projekt"""
        try:
            # Aktueller Monat - Anfang und Ende
            now = datetime.now(timezone.utc)
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Query für aktuellen Monat
            result = self.supabase.client.table("embedding_usage").select("tokens").eq(
                "project", project
            ).gte("created_at", month_start.isoformat()).execute()
            
            if result.data:
                total_tokens = sum(entry["tokens"] for entry in result.data)
                logger.info(f"📈 Monatlicher Verbrauch für '{project}': {total_tokens:,} Tokens")
                return total_tokens
            else:
                return 0
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Abrufen der monatlichen Usage: {str(e)}")
            return 0

    async def get_project_stats(self, project: str) -> Dict[str, Any]:
        """Liefert detaillierte Statistiken für ein Projekt"""
        try:
            # Alle Usage-Einträge für das Projekt
            result = self.supabase.client.table("embedding_usage").select("*").eq(
                "project", project
            ).order("created_at", desc=True).execute()
            
            if not result.data:
                return {
                    "project": project,
                    "total_tokens": 0,
                    "monthly_tokens": 0,
                    "save_operations": 0,
                    "search_operations": 0,
                    "estimated_cost_usd": 0.0,
                    "first_usage": None,
                    "last_usage": None,
                }
            
            entries = result.data
            
            # Gesamtstatistiken
            total_tokens = sum(entry["tokens"] for entry in entries)
            save_ops = len([e for e in entries if e["usage_type"] == "save"])
            search_ops = len([e for e in entries if e["usage_type"] == "search"])
            
            # Monatliche Tokens
            monthly_tokens = await self.get_monthly_usage(project)
            
            # Kosten berechnen (text-embedding-3-small: $0.00002 per 1K tokens)
            estimated_cost = (total_tokens / 1000) * 0.00002
            
            stats = {
                "project": project,
                "total_tokens": total_tokens,
                "monthly_tokens": monthly_tokens,
                "save_operations": save_ops,
                "search_operations": search_ops,
                "estimated_cost_usd": round(estimated_cost, 6),
                "first_usage": entries[-1]["created_at"] if entries else None,
                "last_usage": entries[0]["created_at"] if entries else None,
                "total_operations": len(entries),
            }
            
            logger.info(f"📊 Projekt-Stats für '{project}': {total_tokens:,} Tokens, ${estimated_cost:.6f}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Abrufen der Projekt-Statistiken: {str(e)}")
            raise

    async def get_all_projects_usage(self) -> Dict[str, Any]:
        """Liefert Usage-Übersicht für alle Projekte"""
        try:
            # Alle Projekte ermitteln
            result = self.supabase.client.table("embedding_usage").select("project").execute()
            
            if not result.data:
                return {"projects": [], "total_tokens": 0, "estimated_cost_usd": 0.0}
            
            # Einzigartige Projekte
            projects = list(set(entry["project"] for entry in result.data))
            
            project_stats = []
            total_tokens = 0
            
            for project in projects:
                stats = await self.get_project_stats(project)
                project_stats.append(stats)
                total_tokens += stats["total_tokens"]
            
            # Nach Tokens sortieren
            project_stats.sort(key=lambda x: x["total_tokens"], reverse=True)
            
            total_cost = (total_tokens / 1000) * 0.00002
            
            overview = {
                "projects": project_stats,
                "total_projects": len(projects),
                "total_tokens": total_tokens,
                "estimated_cost_usd": round(total_cost, 6),
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
            
            logger.info(f"📊 Gesamt-Usage: {len(projects)} Projekte, {total_tokens:,} Tokens, ${total_cost:.6f}")
            return overview
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Abrufen der Gesamt-Usage: {str(e)}")
            raise