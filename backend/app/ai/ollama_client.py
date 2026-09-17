import aiohttp
import json
from typing import AsyncGenerator, Optional
import structlog

from app.config import get_settings

logger = structlog.get_logger()


class OllamaClient:
    """Ollama LLM client for AI chat and analysis."""

    def __init__(self):
        settings = get_settings()
        self.base_url = settings.ollama_url
        self.model = settings.ollama_model

    async def chat(self, message: str, system_prompt: str = None) -> str:
        """Send a chat message and get a response."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": message,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("response", "No response generated")
                    else:
                        error = await resp.text()
                        logger.error("Ollama error", status=resp.status, error=error)
                        return f"AI service error: {resp.status}"
        except aiohttp.ClientError as e:
            logger.error("Ollama connection error", error=str(e))
            return "AI service is not available. Please ensure Ollama is running."

    async def stream_chat(self, message: str) -> AsyncGenerator[str, None]:
        """Stream chat response."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": message,
            "stream": True,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as resp:
                    async for line in resp.content:
                        if line:
                            try:
                                data = json.loads(line)
                                token = data.get("response", "")
                                if token:
                                    yield f"data: {json.dumps({'token': token})}\n\n"
                                if data.get("done"):
                                    yield "data: [DONE]\n\n"
                                    break
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    async def list_models(self) -> list[str]:
        """List available models."""
        try:
            url = f"{self.base_url}/api/tags"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return [m["name"] for m in data.get("models", [])]
            return []
        except Exception:
            return []

    async def health_check(self) -> bool:
        """Check if Ollama is running."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.base_url,
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    return resp.status == 200
        except Exception:
            return False
