import aiohttp
import structlog
from app.config import get_settings

logger = structlog.get_logger()


async def send_discord(message: str) -> bool:
    """Send a Discord webhook notification."""
    settings = get_settings()
    if not settings.discord_webhook_url:
        logger.warning("Discord not configured")
        return False

    payload = {"content": message}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(settings.discord_webhook_url, json=payload) as resp:
                if resp.status in (200, 204):
                    logger.info("Discord sent")
                    return True
                else:
                    logger.error("Discord error", status=resp.status)
                    return False
    except Exception as e:
        logger.error("Discord send error", error=str(e))
        return False
