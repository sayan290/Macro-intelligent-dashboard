import aiosmtplib
from email.message import EmailMessage
import structlog
from app.config import get_settings

logger = structlog.get_logger()


async def send_email(subject: str, body: str, to: str = None) -> bool:
    """Send an email notification."""
    settings = get_settings()
    if not settings.smtp_host or not settings.smtp_user:
        logger.warning("Email not configured")
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_user
    msg["To"] = to or settings.smtp_user
    msg.set_content(body)

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_pass,
            use_tls=True,
        )
        logger.info("Email sent", to=to)
        return True
    except Exception as e:
        logger.error("Email send error", error=str(e))
        return False
