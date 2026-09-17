import aiohttp
from typing import Optional
import structlog

logger = structlog.get_logger()


class BinanceClient:
    """Binance public API client."""

    BASE_URL = "https://api.binance.com/api/v3"

    async def get_ticker(self, symbol: str = "BTCUSDT") -> Optional[dict]:
        """Get 24h ticker data."""
        try:
            url = f"{self.BASE_URL}/ticker/24hr"
            params = {"symbol": symbol}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "symbol": data["symbol"],
                            "price": float(data["lastPrice"]),
                            "change_pct": float(data["priceChangePercent"]),
                            "volume": float(data["volume"]),
                            "quote_volume": float(data["quoteVolume"]),
                            "high": float(data["highPrice"]),
                            "low": float(data["lowPrice"]),
                            "trades": int(data["count"]),
                        }
            return None
        except Exception as e:
            logger.error("Binance ticker error", symbol=symbol, error=str(e))
            return None

    async def get_order_book(self, symbol: str = "BTCUSDT", limit: int = 20) -> Optional[dict]:
        """Get order book depth."""
        try:
            url = f"{self.BASE_URL}/depth"
            params = {"symbol": symbol, "limit": limit}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "symbol": symbol,
                            "bids": [[float(p), float(q)] for p, q in data.get("bids", [])],
                            "asks": [[float(p), float(q)] for p, q in data.get("asks", [])],
                            "bid_depth": sum(float(q) for _, q in data.get("bids", [])),
                            "ask_depth": sum(float(q) for _, q in data.get("asks", [])),
                        }
            return None
        except Exception as e:
            logger.error("Binance depth error", error=str(e))
            return None

    async def get_funding_rate(self, symbol: str = "BTCUSDT") -> Optional[dict]:
        """Get funding rate for perpetual futures."""
        try:
            url = "https://fapi.binance.com/fapi/v1/fundingRate"
            params = {"symbol": symbol, "limit": 1}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data:
                            return {
                                "symbol": symbol,
                                "funding_rate": float(data[0]["fundingRate"]),
                                "funding_time": data[0]["fundingTime"],
                            }
            return None
        except Exception as e:
            logger.error("Binance funding error", error=str(e))
            return None
