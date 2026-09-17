import aiohttp
from typing import Optional
import structlog

from app.config import get_settings

logger = structlog.get_logger()


class EmbeddingService:
    """Embedding generation using Ollama."""

    def __init__(self):
        settings = get_settings()
        self.base_url = settings.ollama_url
        self.model = settings.embedding_model

    async def embed(self, text: str) -> Optional[list[float]]:
        """Generate embeddings for a text."""
        try:
            url = f"{self.base_url}/api/embeddings"
            payload = {"model": self.model, "prompt": text}
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("embedding")
            return None
        except Exception as e:
            logger.error("Embedding error", error=str(e))
            return None

    async def embed_batch(self, texts: list[str]) -> list[Optional[list[float]]]:
        """Generate embeddings for multiple texts."""
        results = []
        for text in texts:
            emb = await self.embed(text)
            results.append(emb)
        return results
