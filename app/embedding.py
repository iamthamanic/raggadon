import os
import logging
from typing import Dict, Any, List
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY muss gesetzt sein")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = "text-embedding-3-small"
        logger.info("✅ OpenAI Embedding Service initialisiert")

    async def create_embedding(self, text: str) -> Dict[str, Any]:
        """Erstellt ein Embedding für den gegebenen Text"""
        try:
            if not text or not text.strip():
                raise ValueError("Text darf nicht leer sein")
            
            # Bereinige den Text
            clean_text = text.strip().replace("\n", " ").replace("\r", " ")
            
            response = await self.client.embeddings.create(
                model=self.model,
                input=clean_text,
                encoding_format="float"
            )
            
            embedding = response.data[0].embedding
            tokens_used = response.usage.total_tokens
            
            logger.info(f"🧠 Embedding erstellt: {tokens_used} Tokens für {len(clean_text)} Zeichen")
            
            return {
                "embedding": embedding,
                "tokens": tokens_used,
                "model": self.model,
                "text_length": len(clean_text)
            }
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Erstellen des Embeddings: {str(e)}")
            raise

    async def create_batch_embeddings(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Erstellt Embeddings für mehrere Texte gleichzeitig"""
        try:
            if not texts:
                return []
            
            # Bereinige alle Texte
            clean_texts = [text.strip().replace("\n", " ").replace("\r", " ") for text in texts if text.strip()]
            
            if not clean_texts:
                return []
            
            response = await self.client.embeddings.create(
                model=self.model,
                input=clean_texts,
                encoding_format="float"
            )
            
            results = []
            for i, embedding_data in enumerate(response.data):
                results.append({
                    "embedding": embedding_data.embedding,
                    "text": clean_texts[i],
                    "text_length": len(clean_texts[i]),
                    "index": i
                })
            
            total_tokens = response.usage.total_tokens
            logger.info(f"🧠 Batch Embeddings erstellt: {total_tokens} Tokens für {len(clean_texts)} Texte")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Erstellen der Batch Embeddings: {str(e)}")
            raise

    def get_embedding_dimensions(self) -> int:
        """Gibt die Dimensionen des verwendeten Embedding-Modells zurück"""
        # text-embedding-3-small hat 1536 Dimensionen
        return 1536

    def calculate_cost(self, tokens: int) -> float:
        """Berechnet die Kosten für die verwendeten Tokens"""
        # text-embedding-3-small kostet $0.00002 per 1K tokens
        return (tokens / 1000) * 0.00002