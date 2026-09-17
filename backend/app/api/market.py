from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from datetime import datetime, timedelta
from typing import Optional
import json

from app.database import get_db, get_redis
from app.models.market_data import MarketData, MarketDataDaily
from app.ingestion.yahoo import YahooFinanceClient
from app.ingestion.coingecko import CoinGeckoClient

router = APIRouter()

DEFAULT_SYMBOLS = {
    "equity": ["SPY", "QQQ", "IWM", "DIA", "VGK", "EEM"],
    "commodity": ["GLD", "SLV", "USO", "UNG"],
    "crypto": ["bitcoin", "ethereum", "solana"],
    "bond": ["TLT", "IEF", "HYG", "LQD"],
    "currency": ["DX-Y.NYB", "EURUSD=X", "GBPUSD=X", "USDJPY=X"],
}


@router.get("/overview")
async def market_overview(db: AsyncSession = Depends(get_db)):
    """Get current market overview with prices for major assets."""
    redis = await get_redis()
    cached = await redis.get("market:overview")
    if cached:
        return json.loads(cached)

    yahoo = YahooFinanceClient()
    overview = {"equity": [], "commodity": [], "bond": [], "currency": [], "crypto": []}

    for cls, symbols in DEFAULT_SYMBOLS.items():
        if cls == "crypto":
            cg = CoinGeckoClient()
            for sym in symbols:
                try:
                    data = await cg.get_price(sym)
                    if data:
                        overview["crypto"].append(data)
                except Exception:
                    continue
        else:
            for sym in symbols:
                try:
                    data = await yahoo.get_quote(sym)
                    if data:
                        overview[cls].append(data)
                except Exception:
                    continue

    await redis.setex("market:overview", 120, json.dumps(overview, default=str))
    return overview


@router.get("/prices/{symbol}")
async def get_prices(
    symbol: str,
    period: str = Query("1mo", regex="^(1d|5d|1mo|3mo|6mo|1y|5y|max)$"),
    interval: str = Query("1d", regex="^(1m|5m|15m|1h|1d|1wk|1mo)$"),
):
    """Get historical price data for a symbol."""
    yahoo = YahooFinanceClient()
    return await yahoo.get_history(symbol, period=period, interval=interval)


@router.get("/intraday/{symbol}")
async def get_intraday(symbol: str):
    """Get intraday price data."""
    yahoo = YahooFinanceClient()
    return await yahoo.get_history(symbol, period="1d", interval="5m")


@router.get("/crypto")
async def crypto_overview():
    """Get crypto market overview."""
    cg = CoinGeckoClient()
    return await cg.get_market_overview()


@router.get("/crypto/{coin_id}")
async def crypto_detail(coin_id: str):
    """Get detailed crypto data."""
    cg = CoinGeckoClient()
    return await cg.get_coin_detail(coin_id)


@router.get("/heatmap")
async def market_heatmap(db: AsyncSession = Depends(get_db)):
    """Get sector performance heatmap data."""
    sectors = {
        "Technology": "XLK", "Healthcare": "XLV", "Financial": "XLF",
        "Energy": "XLE", "Consumer Disc": "XLY", "Consumer Staples": "XLP",
        "Industrials": "XLI", "Materials": "XLB", "Real Estate": "XLRE",
        "Utilities": "XLU", "Communication": "XLC",
    }
    yahoo = YahooFinanceClient()
    results = []
    for name, sym in sectors.items():
        try:
            data = await yahoo.get_quote(sym)
            if data:
                results.append({"sector": name, "symbol": sym, **data})
        except Exception:
            continue
    return results


@router.post("/ingest")
async def ingest_market_data(
    symbols: list[str],
    asset_class: str = "equity",
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger market data ingestion."""
    yahoo = YahooFinanceClient()
    ingested = 0
    for symbol in symbols:
        try:
            history = await yahoo.get_history(symbol, period="1mo", interval="1d")
            for point in history.get("data", []):
                record = MarketDataDaily(
                    symbol=symbol,
                    asset_class=asset_class,
                    date=point["timestamp"],
                    open=point.get("open"),
                    high=point.get("high"),
                    low=point.get("low"),
                    close=point["close"],
                    volume=point.get("volume"),
                    change_pct=point.get("change_pct"),
                )
                db.add(record)
                ingested += 1
            await db.commit()
        except Exception as e:
            await db.rollback()
            continue
    return {"ingested": ingested, "symbols": symbols}
