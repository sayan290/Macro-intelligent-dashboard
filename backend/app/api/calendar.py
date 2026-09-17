from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from datetime import datetime, timedelta
from typing import Optional
import json

from app.database import get_db, get_redis
from app.models.events import EconomicEvent

router = APIRouter()


@router.get("/upcoming")
async def upcoming_events(
    days: int = Query(7, ge=1, le=30),
    impact: Optional[str] = Query(None, regex="^(high|medium|low)$"),
    country: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get upcoming economic events."""
    redis = await get_redis()
    cache_key = f"calendar:upcoming:{days}:{impact}:{country}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    now = datetime.utcnow()
    end = now + timedelta(days=days)

    query = select(EconomicEvent).where(
        and_(
            EconomicEvent.datetime_utc >= now,
            EconomicEvent.datetime_utc <= end,
        )
    ).order_by(EconomicEvent.datetime_utc)

    if impact:
        query = query.where(EconomicEvent.impact == impact)
    if country:
        query = query.where(EconomicEvent.country == country)

    result = await db.execute(query)
    events = result.scalars().all()

    data = [{
        "id": e.id,
        "event_name": e.event_name,
        "country": e.country,
        "datetime_utc": str(e.datetime_utc),
        "impact": e.impact,
        "category": e.category,
        "actual": e.actual,
        "forecast": e.forecast,
        "previous": e.previous,
    } for e in events]

    await redis.setex(cache_key, 1800, json.dumps(data, default=str))
    return data


@router.get("/past")
async def past_events(
    days: int = Query(7, ge=1, le=90),
    impact: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get past economic events with actual values."""
    now = datetime.utcnow()
    start = now - timedelta(days=days)

    query = select(EconomicEvent).where(
        and_(
            EconomicEvent.datetime_utc >= start,
            EconomicEvent.datetime_utc <= now,
        )
    ).order_by(desc(EconomicEvent.datetime_utc))

    if impact:
        query = query.where(EconomicEvent.impact == impact)

    result = await db.execute(query)
    events = result.scalars().all()

    return [{
        "id": e.id,
        "event_name": e.event_name,
        "country": e.country,
        "datetime_utc": str(e.datetime_utc),
        "impact": e.impact,
        "actual": e.actual,
        "forecast": e.forecast,
        "previous": e.previous,
        "surprise": _calc_surprise(e.actual, e.forecast),
    } for e in events]


@router.get("/today")
async def today_events(db: AsyncSession = Depends(get_db)):
    """Get today's economic events."""
    now = datetime.utcnow()
    start = now.replace(hour=0, minute=0, second=0)
    end = now.replace(hour=23, minute=59, second=59)

    result = await db.execute(
        select(EconomicEvent).where(
            and_(
                EconomicEvent.datetime_utc >= start,
                EconomicEvent.datetime_utc <= end,
            )
        ).order_by(EconomicEvent.datetime_utc)
    )
    events = result.scalars().all()

    return [{
        "id": e.id,
        "event_name": e.event_name,
        "country": e.country,
        "datetime_utc": str(e.datetime_utc),
        "impact": e.impact,
        "actual": e.actual,
        "forecast": e.forecast,
        "previous": e.previous,
    } for e in events]


def _calc_surprise(actual: Optional[str], forecast: Optional[str]) -> Optional[float]:
    """Calculate surprise factor from actual vs forecast."""
    if not actual or not forecast:
        return None
    try:
        a = float(actual.replace("%", "").replace("K", "").replace("M", "").replace("B", ""))
        f = float(forecast.replace("%", "").replace("K", "").replace("M", "").replace("B", ""))
        if f == 0:
            return None
        return round((a - f) / abs(f) * 100, 2)
    except (ValueError, TypeError):
        return None
