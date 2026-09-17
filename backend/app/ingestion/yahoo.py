import yfinance as yf
from datetime import datetime
from typing import Optional
import structlog
import asyncio

logger = structlog.get_logger()


class YahooFinanceClient:
    """Yahoo Finance data client using yfinance."""

    async def get_quote(self, symbol: str) -> Optional[dict]:
        """Get current quote for a symbol."""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, self._fetch_quote, symbol)
            return data
        except Exception as e:
            logger.error("Yahoo quote error", symbol=symbol, error=str(e))
            return None

    def _fetch_quote(self, symbol: str) -> Optional[dict]:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        hist = ticker.history(period="2d")

        if hist.empty:
            return None

        current = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) > 1 else hist.iloc[-1]

        change = current["Close"] - prev["Close"]
        change_pct = (change / prev["Close"]) * 100 if prev["Close"] else 0

        return {
            "symbol": symbol,
            "price": round(current["Close"], 4),
            "change": round(change, 4),
            "change_pct": round(change_pct, 2),
            "volume": int(current.get("Volume", 0)),
            "high": round(current["High"], 4),
            "low": round(current["Low"], 4),
            "open": round(current["Open"], 4),
            "timestamp": str(current.name),
        }

    async def get_history(
        self,
        symbol: str,
        period: str = "1mo",
        interval: str = "1d",
    ) -> dict:
        """Get historical OHLCV data."""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None, self._fetch_history, symbol, period, interval
            )
            return data
        except Exception as e:
            logger.error("Yahoo history error", symbol=symbol, error=str(e))
            return {"symbol": symbol, "data": [], "error": str(e)}

    def _fetch_history(self, symbol: str, period: str, interval: str) -> dict:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)

        if hist.empty:
            return {"symbol": symbol, "data": []}

        data = []
        prev_close = None
        for idx, row in hist.iterrows():
            change_pct = None
            if prev_close and prev_close > 0:
                change_pct = round(((row["Close"] - prev_close) / prev_close) * 100, 4)

            data.append({
                "timestamp": str(idx),
                "open": round(row["Open"], 4),
                "high": round(row["High"], 4),
                "low": round(row["Low"], 4),
                "close": round(row["Close"], 4),
                "volume": int(row.get("Volume", 0)),
                "change_pct": change_pct,
            })
            prev_close = row["Close"]

        return {"symbol": symbol, "data": data}
