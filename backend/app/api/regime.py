from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional
import json

from app.database import get_db, get_redis
from app.models.regime import RegimeState, RegimeTransition

router = APIRouter()


@router.get("/current")
async def current_regime(db: AsyncSession = Depends(get_db)):
    """Get the current market regime assessment."""
    redis = await get_redis()
    cached = await redis.get("regime:current")
    if cached:
        return json.loads(cached)

    result = await db.execute(
        select(RegimeState).order_by(desc(RegimeState.timestamp)).limit(1)
    )
    state = result.scalar_one_or_none()

    if state:
        data = {
            "regime": state.regime,
            "confidence": state.confidence,
            "sub_regimes": state.sub_regimes,
            "indicators": state.indicators,
            "description": state.description,
            "timestamp": str(state.timestamp),
        }
    else:
        # Return default when no data exists
        data = {
            "regime": "unknown",
            "confidence": 0.0,
            "sub_regimes": {},
            "indicators": {},
            "description": "No regime data available. Run regime detection first.",
            "timestamp": None,
        }

    await redis.setex("regime:current", 300, json.dumps(data, default=str))
    return data


@router.get("/history")
async def regime_history(
    limit: int = Query(50, le=500),
    db: AsyncSession = Depends(get_db),
):
    """Get regime state history."""
    result = await db.execute(
        select(RegimeState).order_by(desc(RegimeState.timestamp)).limit(limit)
    )
    states = result.scalars().all()
    return [{
        "id": s.id,
        "regime": s.regime,
        "confidence": s.confidence,
        "sub_regimes": s.sub_regimes,
        "indicators": s.indicators,
        "timestamp": str(s.timestamp),
    } for s in states]


@router.get("/transitions")
async def regime_transitions(
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get regime transition history."""
    result = await db.execute(
        select(RegimeTransition).order_by(desc(RegimeTransition.transition_date)).limit(limit)
    )
    transitions = result.scalars().all()
    return [{
        "from_regime": t.from_regime,
        "to_regime": t.to_regime,
        "transition_date": str(t.transition_date),
        "confidence": t.confidence,
        "trigger_factors": t.trigger_factors,
    } for t in transitions]
