import numpy as np
from typing import Optional
import structlog

from app.ingestion.yahoo import YahooFinanceClient

logger = structlog.get_logger()


class VolatilityAnalyzer:
    """Realized volatility and drawdown analysis."""

    def __init__(self):
        self.yahoo = YahooFinanceClient()

    async def realized_vol(
        self,
        symbol: str,
        window: int = 21,
        period: str = "1y",
    ) -> dict:
        """Calculate realized volatility."""
        data = await self.yahoo.get_history(symbol, period=period, interval="1d")
        if not data.get("data"):
            return {"error": "No data"}

        closes = np.array([d["close"] for d in data["data"]])
        returns = np.diff(np.log(closes))

        realized = []
        for i in range(window, len(returns)):
            vol = np.std(returns[i - window:i]) * np.sqrt(252) * 100
            realized.append({
                "date": data["data"][i + 1]["timestamp"],
                "volatility": round(vol, 2),
            })

        current_vol = realized[-1]["volatility"] if realized else None

        return {
            "symbol": symbol,
            "window": window,
            "current": current_vol,
            "data": realized,
        }

    async def drawdown_analysis(
        self,
        symbol: str,
        period: str = "1y",
    ) -> dict:
        """Calculate drawdown from all-time-high."""
        data = await self.yahoo.get_history(symbol, period=period, interval="1d")
        if not data.get("data"):
            return {"error": "No data"}

        closes = np.array([d["close"] for d in data["data"]])
        running_max = np.maximum.accumulate(closes)
        drawdowns = (closes - running_max) / running_max * 100

        current_dd = round(drawdowns[-1], 2)
        max_dd = round(np.min(drawdowns), 2)

        return {
            "symbol": symbol,
            "current_drawdown": current_dd,
            "max_drawdown": max_dd,
            "data": [
                {"date": data["data"][i]["timestamp"], "drawdown": round(dd, 2)}
                for i, dd in enumerate(drawdowns)
            ],
        }
