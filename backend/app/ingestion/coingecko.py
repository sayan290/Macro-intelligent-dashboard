import aiohttp
from typing import Optional
import structlog

logger = structlog.get_logger()


class CoinGeckoClient:
    """CoinGecko API client for crypto market data."""

    BASE_URL = "https://api.coingecko.com/api/v3"

    async def get_price(self, coin_id: str) -> Optional[dict]:
        """Get current price for a coin."""
        try:
            url = f"{self.BASE_URL}/simple/price"
            params = {
                "ids": coin_id,
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_24hr_vol": "true",
                "include_market_cap": "true",
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if coin_id in data:
                            coin = data[coin_id]
                            return {
                                "symbol": coin_id,
                                "price": coin.get("usd", 0),
                                "change_pct": round(coin.get("usd_24h_change", 0), 2),
                                "volume": coin.get("usd_24h_vol", 0),
                                "market_cap": coin.get("usd_market_cap", 0),
                            }
            return None
        except Exception as e:
            logger.error("CoinGecko price error", coin=coin_id, error=str(e))
            return None

    async def get_market_overview(self) -> list[dict]:
        """Get top crypto market overview."""
        try:
            url = f"{self.BASE_URL}/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 20,
                "page": 1,
                "sparkline": "false",
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return [{
                            "id": coin["id"],
                            "symbol": coin["symbol"],
                            "name": coin["name"],
                            "price": coin.get("current_price"),
                            "market_cap": coin.get("market_cap"),
                            "volume": coin.get("total_volume"),
                            "change_pct_24h": coin.get("price_change_percentage_24h"),
                            "change_pct_7d": coin.get("price_change_percentage_7d_in_currency"),
                        } for coin in data]
            return []
        except Exception as e:
            logger.error("CoinGecko market error", error=str(e))
            return []

    async def get_coin_detail(self, coin_id: str) -> Optional[dict]:
        """Get detailed coin data."""
        try:
            url = f"{self.BASE_URL}/coins/{coin_id}"
            params = {"localization": "false", "tickers": "false", "community_data": "false"}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        md = data.get("market_data", {})
                        return {
                            "id": data["id"],
                            "name": data["name"],
                            "symbol": data["symbol"],
                            "price": md.get("current_price", {}).get("usd"),
                            "market_cap": md.get("market_cap", {}).get("usd"),
                            "ath": md.get("ath", {}).get("usd"),
                            "ath_change_pct": md.get("ath_change_percentage", {}).get("usd"),
                            "change_24h": md.get("price_change_percentage_24h"),
                            "change_7d": md.get("price_change_percentage_7d"),
                            "change_30d": md.get("price_change_percentage_30d"),
                        }
            return None
        except Exception as e:
            logger.error("CoinGecko detail error", coin=coin_id, error=str(e))
            return None
