from typing import Optional
from datetime import datetime
import json
import structlog

from app.database import get_redis

logger = structlog.get_logger()


class ConversationMemory:
    """Manages AI conversation history in Redis."""

    MAX_HISTORY = 20

    async def add_message(self, session_id: str, role: str, content: str):
        """Add a message to conversation history."""
        redis = await get_redis()
        key = f"ai:conversation:{session_id}"

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        }

        await redis.rpush(key, json.dumps(message))
        await redis.ltrim(key, -self.MAX_HISTORY, -1)
        await redis.expire(key, 3600 * 24)

    async def get_history(self, session_id: str) -> list[dict]:
        """Get conversation history."""
        redis = await get_redis()
        key = f"ai:conversation:{session_id}"
        messages = await redis.lrange(key, 0, -1)
        return [json.loads(m) for m in messages]

    async def clear(self, session_id: str):
        """Clear conversation history."""
        redis = await get_redis()
        await redis.delete(f"ai:conversation:{session_id}")
