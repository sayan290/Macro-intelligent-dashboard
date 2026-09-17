import aiohttp
import structlog
from app.config import get_settings

logger = structlog.get_logger()


async def send_telegram(message: str) -> bool:
    """Send a Telegram notification."""
    settings = get_settings()
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        logger.warning("Telegram not configured")
        return False

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    logger.info("Telegram sent")
                    return True
                else:
                    logger.error("Telegram error", status=resp.status)
                    return False
    except Exception as e:
        logger.error("Telegram send error", error=str(e))
        return False
