from fastapi import APIRouter, Query
from typing import Optional
import json

from app.database import get_redis
from app.ingestion.yahoo import YahooFinanceClient

router = APIRouter()


@router.get("/matrix")
async def correlation_matrix(
    symbols: str = Query("SPY,QQQ,TLT,GLD,BTC-USD,DX-Y.NYB"),
    period: str = Query("3mo"),
):
    """Compute correlation matrix for given symbols."""
    redis = await get_redis()
    cache_key = f"corr:matrix:{symbols}:{period}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    symbol_list = [s.strip() for s in symbols.split(",")]
    yahoo = YahooFinanceClient()

    import pandas as pd
    import numpy as np

    prices = {}
    for sym in symbol_list:
        try:
            data = await yahoo.get_history(sym, period=period, interval="1d")
            if data.get("data"):
                prices[sym] = {d["timestamp"]: d["close"] for d in data["data"]}
        except Exception:
            continue

    if len(prices) < 2:
        return {"error": "Not enough data", "matrix": {}, "symbols": symbol_list}

    df = pd.DataFrame(prices).dropna()
    returns = df.pct_change().dropna()
    corr = returns.corr()

    result = {
        "symbols": list(corr.columns),
        "matrix": corr.round(4).to_dict(),
        "period": period,
    }

    await redis.setex(cache_key, 3600, json.dumps(result, default=str))
    return result


@router.get("/rolling")
async def rolling_correlation(
    symbol1: str = Query("SPY"),
    symbol2: str = Query("TLT"),
    window: int = Query(30, ge=5, le=252),
    period: str = Query("1y"),
):
    """Compute rolling correlation between two symbols."""
    yahoo = YahooFinanceClient()
    import pandas as pd

    data1 = await yahoo.get_history(symbol1, period=period, interval="1d")
    data2 = await yahoo.get_history(symbol2, period=period, interval="1d")

    if not data1.get("data") or not data2.get("data"):
        return {"error": "Insufficient data"}

    s1 = pd.Series(
        {d["timestamp"]: d["close"] for d in data1["data"]}, name=symbol1
    )
    s2 = pd.Series(
        {d["timestamp"]: d["close"] for d in data2["data"]}, name=symbol2
    )

    df = pd.concat([s1, s2], axis=1).dropna()
    returns = df.pct_change().dropna()
    rolling = returns[symbol1].rolling(window).corr(returns[symbol2])

    return {
        "symbol1": symbol1,
        "symbol2": symbol2,
        "window": window,
        "data": [
            {"date": str(idx), "correlation": round(val, 4)}
            for idx, val in rolling.dropna().items()
        ],
    }


@router.get("/lead-lag")
async def lead_lag_analysis(
    symbol1: str = Query("TLT"),
    symbol2: str = Query("SPY"),
    max_lag: int = Query(20, ge=1, le=60),
):
    """Compute lead-lag relationship between two symbols."""
    yahoo = YahooFinanceClient()
    import pandas as pd
    import numpy as np

    data1 = await yahoo.get_history(symbol1, period="1y", interval="1d")
    data2 = await yahoo.get_history(symbol2, period="1y", interval="1d")

    if not data1.get("data") or not data2.get("data"):
        return {"error": "Insufficient data"}

    s1 = pd.Series({d["timestamp"]: d["close"] for d in data1["data"]})
    s2 = pd.Series({d["timestamp"]: d["close"] for d in data2["data"]})

    df = pd.concat([s1.rename(symbol1), s2.rename(symbol2)], axis=1).dropna()
    r1 = df[symbol1].pct_change().dropna()
    r2 = df[symbol2].pct_change().dropna()

    results = []
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            corr = r1.iloc[:lag].reset_index(drop=True).corr(r2.iloc[-lag:].reset_index(drop=True))
        elif lag > 0:
            corr = r1.iloc[lag:].reset_index(drop=True).corr(r2.iloc[:-lag].reset_index(drop=True))
        else:
            corr = r1.corr(r2)
        results.append({"lag": lag, "correlation": round(corr, 4) if not np.isnan(corr) else 0})

    return {
        "symbol1": symbol1,
        "symbol2": symbol2,
        "max_lag": max_lag,
        "data": results,
    }
