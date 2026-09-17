from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.alerts import Alert, AlertTrigger

router = APIRouter()


class AlertCreate(BaseModel):
    name: str
    alert_type: str  # price_cross, regime_change, indicator_threshold, event_upcoming
    condition: dict
    channels: list[str] = ["telegram"]
    cooldown_minutes: int = 60


class AlertUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    condition: Optional[dict] = None
    channels: Optional[list[str]] = None
    cooldown_minutes: Optional[int] = None


@router.get("/")
async def list_alerts(db: AsyncSession = Depends(get_db)):
    """List all alert configurations."""
    result = await db.execute(select(Alert).order_by(desc(Alert.created_at)))
    alerts = result.scalars().all()
    return [{
        "id": a.id,
        "name": a.name,
        "alert_type": a.alert_type,
        "condition": a.condition,
        "is_active": a.is_active,
        "channels": a.channels,
        "cooldown_minutes": a.cooldown_minutes,
        "last_triggered": str(a.last_triggered) if a.last_triggered else None,
    } for a in alerts]


@router.post("/")
async def create_alert(alert: AlertCreate, db: AsyncSession = Depends(get_db)):
    """Create a new alert."""
    new_alert = Alert(
        name=alert.name,
        alert_type=alert.alert_type,
        condition=alert.condition,
        channels=alert.channels,
        cooldown_minutes=alert.cooldown_minutes,
        created_at=datetime.utcnow(),
    )
    db.add(new_alert)
    await db.commit()
    await db.refresh(new_alert)
    return {"id": new_alert.id, "message": f"Alert '{alert.name}' created"}


@router.put("/{alert_id}")
async def update_alert(alert_id: int, update: AlertUpdate, db: AsyncSession = Depends(get_db)):
    """Update an alert configuration."""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    for field, value in update.model_dump(exclude_none=True).items():
        setattr(alert, field, value)

    await db.commit()
    return {"id": alert_id, "message": "Alert updated"}


@router.delete("/{alert_id}")
async def delete_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an alert."""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    await db.delete(alert)
    await db.commit()
    return {"message": "Alert deleted"}


@router.get("/triggers")
async def list_triggers(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Get recent alert triggers/history."""
    result = await db.execute(
        select(AlertTrigger).order_by(desc(AlertTrigger.triggered_at)).limit(limit)
    )
    triggers = result.scalars().all()
    return [{
        "id": t.id,
        "alert_id": t.alert_id,
        "triggered_at": str(t.triggered_at),
        "message": t.message,
        "data": t.data,
        "delivered": t.delivered,
    } for t in triggers]
