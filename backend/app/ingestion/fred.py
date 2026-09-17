import aiohttp
from datetime import datetime
from typing import Optional
import structlog
from app.config import get_settings

logger = structlog.get_logger()


class FredClient:
    """FRED (Federal Reserve Economic Data) API client."""

    BASE_URL = "https://api.stlouisfed.org/fred"

    def __init__(self):
        self.api_key = get_settings().fred_api_key

    async def get_series(
        self,
        series_id: str,
        limit: int = 500,
        sort_order: str = "desc",
    ) -> list[dict]:
        """Fetch time series observations from FRED."""
        if not self.api_key:
            logger.warning("FRED API key not configured, returning mock data")
            return self._mock_data(series_id)

        url = f"{self.BASE_URL}/series/observations"
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "sort_order": sort_order,
            "limit": limit,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status != 200:
                        logger.error("FRED API error", status=resp.status, series=series_id)
                        return []
                    data = await resp.json()
                    observations = data.get("observations", [])

                    results = []
                    prev_val = None
                    for obs in observations:
                        if obs.get("value") == ".":
                            continue
                        try:
                            val = float(obs["value"])
                        except (ValueError, TypeError):
                            continue

                        change = (val - prev_val) if prev_val is not None else None
                        change_pct = (change / abs(prev_val) * 100) if prev_val and prev_val != 0 else None

                        results.append({
                            "date": obs["date"],
                            "value": val,
                            "change": round(change, 4) if change is not None else None,
                            "change_pct": round(change_pct, 2) if change_pct is not None else None,
                        })
                        prev_val = val

                    return results
        except Exception as e:
            logger.error("FRED request error", error=str(e), series=series_id)
            return self._mock_data(series_id)

    async def get_latest(self, series_id: str) -> dict:
        """Get the latest value for a series."""
        data = await self.get_series(series_id, limit=2)
        if data:
            return data[0]
        return {"value": None, "date": None, "change": None, "change_pct": None}

    async def get_series_info(self, series_id: str) -> Optional[dict]:
        """Get metadata about a series."""
        if not self.api_key:
            return None

        url = f"{self.BASE_URL}/series"
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        serieses = data.get("seriess", [])
                        if serieses:
                            s = serieses[0]
                            return {
                                "id": s["id"],
                                "title": s["title"],
                                "frequency": s.get("frequency"),
                                "units": s.get("units"),
                            }
        except Exception as e:
            logger.error("FRED info error", error=str(e))
        return None

    def _mock_data(self, series_id: str) -> list[dict]:
        """Return mock data when API key not available."""
        import random
        from datetime import timedelta
        base = datetime(2024, 1, 1)
        mock_values = {
            "GDP": 27000, "UNRATE": 3.7, "CPIAUCSL": 310,
            "FEDFUNDS": 5.33, "DGS10": 4.2, "DGS2": 4.5,
            "T10Y2Y": -0.3, "VIXCLS": 14, "M2SL": 20800,
            "T10YIE": 2.3, "UMCSENT": 67, "INDPRO": 103,
            "PAYEMS": 157000, "PCEPI": 120, "CPILFESL": 315,
            "WALCL": 7700000, "RRPONTSYD": 500,
        }
        base_val = mock_values.get(series_id, 100)
        data = []
        for i in range(12):
            val = base_val * (1 + random.uniform(-0.02, 0.02))
            data.append({
                "date": str((base + timedelta(days=30 * i)).date()),
                "value": round(val, 2),
                "change": round(random.uniform(-2, 2), 2),
                "change_pct": round(random.uniform(-1, 1), 2),
            })
        return data
