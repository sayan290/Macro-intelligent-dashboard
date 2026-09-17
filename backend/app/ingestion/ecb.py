import aiohttp
import xml.etree.ElementTree as ET
from typing import Optional
import structlog

logger = structlog.get_logger()


class ECBClient:
    """European Central Bank data API client."""

    BASE_URL = "https://sdw-wsrest.ecb.europa.eu/service"

    async def get_exchange_rates(self) -> list[dict]:
        """Get daily EUR exchange rates."""
        try:
            url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        root = ET.fromstring(text)
                        ns = {"gesmes": "http://www.gesmes.org/xml/2002-08-01",
                              "ecb": "http://www.ecb.int/vocabulary/2002-08-01/eurofxref"}
                        rates = []
                        for cube in root.findall(".//ecb:Cube[@currency]", ns):
                            rates.append({
                                "currency": cube.get("currency"),
                                "rate": float(cube.get("rate")),
                            })
                        return rates
            return []
        except Exception as e:
            logger.error("ECB rates error", error=str(e))
            return []

    async def get_key_rate(self) -> Optional[dict]:
        """Get ECB key interest rate."""
        try:
            url = f"{self.BASE_URL}/data/FM/M.U2.EUR.4F.KR.MRR_FR.LEV"
            headers = {"Accept": "application/json"}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        obs = data.get("dataSets", [{}])[0].get("series", {})
                        for key, series in obs.items():
                            observations = series.get("observations", {})
                            if observations:
                                last_key = max(observations.keys())
                                return {
                                    "rate": observations[last_key][0],
                                    "name": "ECB Main Refinancing Rate",
                                }
            return None
        except Exception as e:
            logger.error("ECB rate error", error=str(e))
            return None
