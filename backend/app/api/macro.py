from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime, timedelta
from typing import Optional
import json

from app.database import get_db, get_redis
from app.models.macro_data import MacroSeries, MacroDataPoint
from app.ingestion.fred import FredClient

router = APIRouter()

CORE_INDICATORS = {
    "growth": [
        {"id": "GDP", "name": "GDP", "units": "Billions $"},
        {"id": "INDPRO", "name": "Industrial Production", "units": "Index"},
        {"id": "PAYEMS", "name": "Nonfarm Payrolls", "units": "Thousands"},
        {"id": "UNRATE", "name": "Unemployment Rate", "units": "%"},
    ],
    "inflation": [
        {"id": "CPIAUCSL", "name": "CPI All Urban", "units": "Index"},
        {"id": "CPILFESL", "name": "Core CPI", "units": "Index"},
        {"id": "PCEPI", "name": "PCE Price Index", "units": "Index"},
        {"id": "T10YIE", "name": "10Y Breakeven Inflation", "units": "%"},
    ],
    "rates": [
        {"id": "FEDFUNDS", "name": "Fed Funds Rate", "units": "%"},
        {"id": "DGS2", "name": "2Y Treasury", "units": "%"},
        {"id": "DGS10", "name": "10Y Treasury", "units": "%"},
        {"id": "T10Y2Y", "name": "10Y-2Y Spread", "units": "%"},
    ],
    "money": [
        {"id": "M2SL", "name": "M2 Money Supply", "units": "Billions $"},
        {"id": "WALCL", "name": "Fed Balance Sheet", "units": "Millions $"},
        {"id": "RRPONTSYD", "name": "Reverse Repo", "units": "Billions $"},
    ],
    "sentiment": [
        {"id": "UMCSENT", "name": "UMich Consumer Sentiment", "units": "Index"},
        {"id": "VIXCLS", "name": "VIX", "units": "Index"},
    ],
}


@router.get("/dashboard")
async def macro_dashboard():
    """Get comprehensive macro dashboard data."""
    redis = await get_redis()
    cached = await redis.get("macro:dashboard")
    if cached:
        return json.loads(cached)

    fred = FredClient()
    dashboard = {}

    for category, indicators in CORE_INDICATORS.items():
        dashboard[category] = []
        for ind in indicators:
            try:
                data = await fred.get_latest(ind["id"])
                dashboard[category].append({
                    "series_id": ind["id"],
                    "name": ind["name"],
                    "units": ind["units"],
                    "value": data.get("value"),
                    "date": data.get("date"),
                    "change": data.get("change"),
                    "change_pct": data.get("change_pct"),
                })
            except Exception:
                dashboard[category].append({
                    "series_id": ind["id"],
                    "name": ind["name"],
                    "units": ind["units"],
                    "value": None,
                    "date": None,
                    "change": None,
                    "change_pct": None,
                })

    await redis.setex("macro:dashboard", 3600, json.dumps(dashboard, default=str))
    return dashboard


@router.get("/series/{series_id}")
async def get_series(
    series_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(500, le=5000),
    db: AsyncSession = Depends(get_db),
):
    """Get time series data for a specific macro indicator."""
    # Try cache first
    redis = await get_redis()
    cache_key = f"macro:series:{series_id}"
    cached = await redis.get(cache_key)
    if cached and not start_date:
        return json.loads(cached)

    # Try database
    query = select(MacroDataPoint).where(
        MacroDataPoint.series_id == series_id
    ).order_by(desc(MacroDataPoint.date)).limit(limit)

    if start_date:
        query = query.where(MacroDataPoint.date >= start_date)
    if end_date:
        query = query.where(MacroDataPoint.date <= end_date)

    result = await db.execute(query)
    points = result.scalars().all()

    if points:
        data = [{
            "date": str(p.date),
            "value": p.value,
            "change": p.change,
            "change_pct": p.change_pct,
        } for p in reversed(points)]
    else:
        # Fetch from FRED API
        fred = FredClient()
        data = await fred.get_series(series_id, limit=limit)

    result_data = {"series_id": series_id, "data": data}
    if not start_date:
        await redis.setex(cache_key, 3600, json.dumps(result_data, default=str))
    return result_data


@router.get("/indicators")
async def list_indicators():
    """List all available macro indicators organized by category."""
    return CORE_INDICATORS


@router.get("/heatmap")
async def macro_heatmap():
    """Get macro indicator heatmap data for visualization."""
    fred = FredClient()
    heatmap = []
    for category, indicators in CORE_INDICATORS.items():
        for ind in indicators:
            try:
                data = await fred.get_latest(ind["id"])
                heatmap.append({
                    "category": category,
                    "series_id": ind["id"],
                    "name": ind["name"],
                    "value": data.get("value"),
                    "change_pct": data.get("change_pct"),
                    "trend": "up" if (data.get("change_pct") or 0) > 0 else "down",
                })
            except Exception:
                heatmap.append({
                    "category": category,
                    "series_id": ind["id"],
                    "name": ind["name"],
                    "value": None,
                    "change_pct": None,
                    "trend": "neutral",
                })
    return heatmap


@router.post("/ingest/{series_id}")
async def ingest_series(series_id: str, db: AsyncSession = Depends(get_db)):
    """Ingest macro data from FRED."""
    fred = FredClient()
    data = await fred.get_series(series_id, limit=1000)
    ingested = 0
    for point in data:
        record = MacroDataPoint(
            series_id=series_id,
            date=point["date"],
            value=point["value"],
            change=point.get("change"),
            change_pct=point.get("change_pct"),
        )
        db.add(record)
        ingested += 1
    try:
        await db.commit()
    except Exception:
        await db.rollback()
    return {"series_id": series_id, "ingested": ingested}
