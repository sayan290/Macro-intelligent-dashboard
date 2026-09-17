import numpy as np
import pandas as pd
from typing import Optional
import structlog

from app.ingestion.yahoo import YahooFinanceClient

logger = structlog.get_logger()


class CorrelationEngine:
    """Cross-asset correlation analysis engine."""

    def __init__(self):
        self.yahoo = YahooFinanceClient()

    async def compute_matrix(
        self,
        symbols: list[str],
        period: str = "6mo",
    ) -> dict:
        """Compute full correlation matrix."""
        prices = {}
        for sym in symbols:
            try:
                data = await self.yahoo.get_history(sym, period=period, interval="1d")
                if data.get("data"):
                    prices[sym] = {d["timestamp"]: d["close"] for d in data["data"]}
            except Exception:
                continue

        if len(prices) < 2:
            return {"error": "Insufficient data"}

        df = pd.DataFrame(prices).dropna()
        returns = df.pct_change().dropna()
        corr = returns.corr()

        return {
            "symbols": list(corr.columns),
            "matrix": corr.round(4).to_dict(),
            "stats": {
                "period": period,
                "observations": len(returns),
                "avg_correlation": round(corr.values[np.triu_indices_from(corr.values, 1)].mean(), 4),
            },
        }

    async def rolling_correlation(
        self,
        sym1: str,
        sym2: str,
        window: int = 30,
        period: str = "1y",
    ) -> dict:
        """Compute rolling correlation between two assets."""
        d1 = await self.yahoo.get_history(sym1, period=period, interval="1d")
        d2 = await self.yahoo.get_history(sym2, period=period, interval="1d")

        if not d1.get("data") or not d2.get("data"):
            return {"error": "Insufficient data"}

        s1 = pd.Series({d["timestamp"]: d["close"] for d in d1["data"]})
        s2 = pd.Series({d["timestamp"]: d["close"] for d in d2["data"]})

        df = pd.concat([s1.rename(sym1), s2.rename(sym2)], axis=1).dropna()
        ret = df.pct_change().dropna()
        rolling = ret[sym1].rolling(window).corr(ret[sym2])

        return {
            "data": [
                {"date": str(idx), "correlation": round(v, 4)}
                for idx, v in rolling.dropna().items()
            ],
        }

    async def macro_sensitivity(
        self,
        asset_symbols: list[str],
        macro_series: list[str],
    ) -> dict:
        """Compute sensitivity of assets to macro indicators."""
        from app.ingestion.fred import FredClient
        fred = FredClient()

        asset_data = {}
        for sym in asset_symbols:
            d = await self.yahoo.get_history(sym, period="5y", interval="1mo")
            if d.get("data"):
                asset_data[sym] = {dp["timestamp"][:7]: dp["close"] for dp in d["data"]}

        macro_data = {}
        for sid in macro_series:
            series = await fred.get_series(sid, limit=100)
            if series:
                macro_data[sid] = {dp["date"][:7]: dp["value"] for dp in series}

        if not asset_data or not macro_data:
            return {"error": "Insufficient data"}

        all_data = {**asset_data, **macro_data}
        df = pd.DataFrame(all_data).dropna()
        if df.empty:
            return {"error": "No overlapping data"}

        # Compute returns for assets, changes for macro
        returns = df[asset_symbols].pct_change().dropna()
        macro_changes = df[macro_series].diff().dropna()
        combined = pd.concat([returns, macro_changes], axis=1).dropna()

        if combined.empty:
            return {"error": "Insufficient overlapping data"}

        sensitivity = {}
        for asset in asset_symbols:
            sensitivity[asset] = {}
            for macro in macro_series:
                corr = combined[asset].corr(combined[macro])
                sensitivity[asset][macro] = round(corr, 4)

        return {"sensitivity": sensitivity}
