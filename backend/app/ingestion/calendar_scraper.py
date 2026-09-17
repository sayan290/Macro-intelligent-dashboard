import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Optional
import structlog

logger = structlog.get_logger()


class CalendarScraper:
    """Economic calendar scraper."""

    async def scrape_investing_com(self) -> list[dict]:
        """Scrape economic calendar from investing.com."""
        try:
            url = "https://www.investing.com/economic-calendar/"
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                    if resp.status == 200:
                        html = await resp.text()
                        return self._parse_calendar(html)
            return []
        except Exception as e:
            logger.error("Calendar scrape error", error=str(e))
            return []

    def _parse_calendar(self, html: str) -> list[dict]:
        """Parse economic calendar HTML."""
        soup = BeautifulSoup(html, "lxml")
        events = []
        rows = soup.select("tr.js-event-item")[:50]

        for row in rows:
            try:
                event = {
                    "event_name": row.select_one(".event a").get_text(strip=True) if row.select_one(".event a") else "Unknown",
                    "country": row.get("data-country", ""),
                    "datetime_utc": row.get("data-event-datetime", ""),
                    "impact": self._parse_impact(row),
                    "actual": self._get_cell(row, ".act"),
                    "forecast": self._get_cell(row, ".fore"),
                    "previous": self._get_cell(row, ".prev"),
                    "source": "investing.com",
                }
                events.append(event)
            except Exception:
                continue
        return events

    def _parse_impact(self, row) -> str:
        """Parse impact level from bulls icons."""
        bulls = row.select(".sentiment i.grayFullBullishIcon")
        count = len(bulls)
        if count >= 3:
            return "high"
        elif count >= 2:
            return "medium"
        return "low"

    def _get_cell(self, row, selector: str) -> Optional[str]:
        """Get text from a cell."""
        cell = row.select_one(selector)
        return cell.get_text(strip=True) if cell else None

    async def get_mock_events(self, days: int = 7) -> list[dict]:
        """Return mock economic events for demo purposes."""
        now = datetime.utcnow()
        mock_events = [
            {"event_name": "FOMC Rate Decision", "country": "US", "impact": "high", "category": "Central Banks"},
            {"event_name": "Nonfarm Payrolls", "country": "US", "impact": "high", "category": "Employment"},
            {"event_name": "CPI m/m", "country": "US", "impact": "high", "category": "Inflation"},
            {"event_name": "ECB Rate Decision", "country": "EU", "impact": "high", "category": "Central Banks"},
            {"event_name": "GDP q/q", "country": "US", "impact": "high", "category": "Growth"},
            {"event_name": "PMI Manufacturing", "country": "US", "impact": "medium", "category": "PMI"},
            {"event_name": "Retail Sales m/m", "country": "US", "impact": "medium", "category": "Consumer"},
            {"event_name": "Unemployment Claims", "country": "US", "impact": "medium", "category": "Employment"},
            {"event_name": "BoE Rate Decision", "country": "GB", "impact": "high", "category": "Central Banks"},
            {"event_name": "Core PCE Price Index", "country": "US", "impact": "high", "category": "Inflation"},
        ]
        events = []
        for i, ev in enumerate(mock_events):
            events.append({
                **ev,
                "datetime_utc": str(now + timedelta(days=i * 0.7, hours=i * 3)),
                "actual": None,
                "forecast": f"{2.0 + i * 0.1:.1f}%",
                "previous": f"{1.9 + i * 0.1:.1f}%",
                "source": "mock",
            })
        return events


class EngineIngestion:
    """Central ingestion engine coordinating all data sources."""

    def __init__(self):
        from app.ingestion.yahoo import YahooFinanceClient
        from app.ingestion.fred import FredClient
        from app.ingestion.coingecko import CoinGeckoClient
        from app.ingestion.news_rss import NewsRSSClient

        self.yahoo = YahooFinanceClient()
        self.fred = FredClient()
        self.coingecko = CoinGeckoClient()
        self.news = NewsRSSClient()

    async def ingest_all(self):
        """Run all ingestion tasks."""
        logger.info("Starting full data ingestion")
        results = {}
        # Each ingestion is independent so we gather
        import asyncio
        tasks = {
            "market": self._ingest_market(),
            "macro": self._ingest_macro(),
            "crypto": self._ingest_crypto(),
            "news": self._ingest_news(),
        }
        for name, coro in tasks.items():
            try:
                results[name] = await coro
            except Exception as e:
                logger.error(f"Ingestion failed: {name}", error=str(e))
                results[name] = {"error": str(e)}
        return results

    async def _ingest_market(self):
        symbols = ["SPY", "QQQ", "IWM", "DIA", "TLT", "GLD", "USO"]
        data = []
        for sym in symbols:
            try:
                result = await self.yahoo.get_quote(sym)
                if result:
                    data.append(result)
            except Exception:
                continue
        return {"count": len(data), "symbols": [d["symbol"] for d in data]}

    async def _ingest_macro(self):
        series_ids = ["GDP", "UNRATE", "CPIAUCSL", "FEDFUNDS", "DGS10", "T10Y2Y", "VIXCLS"]
        data = []
        for sid in series_ids:
            try:
                result = await self.fred.get_latest(sid)
                if result:
                    data.append({"series_id": sid, **result})
            except Exception:
                continue
        return {"count": len(data)}

    async def _ingest_crypto(self):
        coins = ["bitcoin", "ethereum", "solana"]
        data = []
        for coin in coins:
            try:
                result = await self.coingecko.get_price(coin)
                if result:
                    data.append(result)
            except Exception:
                continue
        return {"count": len(data)}

    async def _ingest_news(self):
        articles = await self.news.fetch_all()
        return {"count": len(articles)}
