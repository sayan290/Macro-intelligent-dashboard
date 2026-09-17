from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.models.alerts import Alert, AlertTrigger
from app.database import AsyncSessionLocal

logger = structlog.get_logger()


class AlertEngine:
    """Central alert monitoring and delivery engine."""

    async def check_all_alerts(self):
        """Check all active alerts."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Alert).where(Alert.is_active == True)
            )
            alerts = result.scalars().all()

            for alert in alerts:
                try:
                    if self._should_check(alert):
                        triggered = await self._evaluate(alert)
                        if triggered:
                            await self._trigger(db, alert, triggered)
                except Exception as e:
                    logger.error("Alert check error", alert_id=alert.id, error=str(e))

            await db.commit()

    def _should_check(self, alert: Alert) -> bool:
        """Check if alert should be evaluated (respecting cooldown)."""
        if not alert.last_triggered:
            return True
        cooldown = timedelta(minutes=alert.cooldown_minutes or 60)
        return datetime.utcnow() - alert.last_triggered > cooldown

    async def _evaluate(self, alert: Alert) -> dict | None:
        """Evaluate alert condition."""
        condition = alert.condition
        alert_type = alert.alert_type

        if alert_type == "price_cross":
            return await self._check_price_cross(condition)
        elif alert_type == "regime_change":
            return await self._check_regime_change(condition)
        elif alert_type == "indicator_threshold":
            return await self._check_indicator(condition)
        return None

    async def _check_price_cross(self, condition: dict) -> dict | None:
        """Check if price crosses a threshold."""
        from app.ingestion.yahoo import YahooFinanceClient
        yahoo = YahooFinanceClient()

        symbol = condition.get("symbol", "SPY")
        threshold = condition.get("threshold", 0)
        direction = condition.get("direction", "above")

        try:
            quote = await yahoo.get_quote(symbol)
            if not quote:
                return None

            price = quote["price"]
            if direction == "above" and price > threshold:
                return {"message": f"{symbol} crossed above {threshold} (current: {price})", "data": quote}
            elif direction == "below" and price < threshold:
                return {"message": f"{symbol} crossed below {threshold} (current: {price})", "data": quote}
        except Exception:
            pass
        return None

    async def _check_regime_change(self, condition: dict) -> dict | None:
        """Check for regime transitions."""
        from app.analysis.regime_detector import RegimeDetector
        detector = RegimeDetector()
        try:
            regime = await detector.detect()
            target = condition.get("target_regime")
            if target and regime["regime"] == target:
                return {"message": f"Regime changed to: {regime['label']}", "data": regime}
        except Exception:
            pass
        return None

    async def _check_indicator(self, condition: dict) -> dict | None:
        """Check if macro indicator crosses threshold."""
        from app.ingestion.fred import FredClient
        fred = FredClient()

        series_id = condition.get("series_id", "VIXCLS")
        threshold = condition.get("threshold", 0)
        direction = condition.get("direction", "above")

        try:
            data = await fred.get_latest(series_id)
            value = data.get("value")
            if value is None:
                return None

            if direction == "above" and value > threshold:
                return {"message": f"{series_id} above {threshold} (current: {value})", "data": data}
            elif direction == "below" and value < threshold:
                return {"message": f"{series_id} below {threshold} (current: {value})", "data": data}
        except Exception:
            pass
        return None

    async def _trigger(self, db: AsyncSession, alert: Alert, trigger_data: dict):
        """Record trigger and deliver notifications."""
        trigger = AlertTrigger(
            alert_id=alert.id,
            triggered_at=datetime.utcnow(),
            message=trigger_data.get("message", "Alert triggered"),
            data=trigger_data.get("data"),
        )
        db.add(trigger)
        alert.last_triggered = datetime.utcnow()

        # Deliver to channels
        channels = alert.channels or ["telegram"]
        for channel in channels:
            try:
                await self._deliver(channel, alert.name, trigger_data["message"])
                trigger.delivered = True
            except Exception as e:
                logger.error("Delivery failed", channel=channel, error=str(e))

        logger.info("Alert triggered", alert_id=alert.id, message=trigger_data["message"])

    async def _deliver(self, channel: str, alert_name: str, message: str):
        """Deliver alert to a specific channel."""
        if channel == "telegram":
            from app.alerts.telegram import send_telegram
            await send_telegram(f"🔔 {alert_name}\n{message}")
        elif channel == "discord":
            from app.alerts.discord import send_discord
            await send_discord(f"🔔 {alert_name}\n{message}")
        elif channel == "email":
            from app.alerts.email_sender import send_email
            await send_email(f"Alert: {alert_name}", message)
