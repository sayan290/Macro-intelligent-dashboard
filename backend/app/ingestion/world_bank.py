import aiohttp
from typing import Optional
import structlog

logger = structlog.get_logger()


class WorldBankClient:
    """World Bank API client."""

    BASE_URL = "https://api.worldbank.org/v2"

    async def get_indicator(
        self,
        indicator: str,
        country: str = "US",
        per_page: int = 50,
    ) -> list[dict]:
        """Get World Bank indicator data."""
        try:
            url = f"{self.BASE_URL}/country/{country}/indicator/{indicator}"
            params = {"format": "json", "per_page": per_page}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if len(data) >= 2:
                            return [{
                                "date": item["date"],
                                "value": item["value"],
                                "country": item["country"]["value"],
                                "indicator": item["indicator"]["value"],
                            } for item in data[1] if item["value"] is not None]
            return []
        except Exception as e:
            logger.error("World Bank error", indicator=indicator, error=str(e))
            return []

    async def get_gdp_growth(self, country: str = "US") -> list[dict]:
        """Get GDP growth rate."""
        return await self.get_indicator("NY.GDP.MKTP.KD.ZG", country)

    async def get_inflation(self, country: str = "US") -> list[dict]:
        """Get consumer inflation."""
        return await self.get_indicator("FP.CPI.TOTL.ZG", country)
