import feedparser
import asyncio
from datetime import datetime
from typing import Optional
import structlog

logger = structlog.get_logger()

RSS_FEEDS = {
    "reuters": "https://news.google.com/rss/search?q=reuters+economy",
    "bloomberg": "https://news.google.com/rss/search?q=bloomberg+markets",
    "fed": "https://www.federalreserve.gov/feeds/press_all.xml",
    "imf": "https://www.imf.org/en/News/Rss",
}


class NewsRSSClient:
    """RSS news aggregator for financial/macro news."""

    async def fetch_feed(self, feed_name: str, url: str) -> list[dict]:
        """Fetch and parse a single RSS feed."""
        try:
            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(None, feedparser.parse, url)
            articles = []
            for entry in feed.entries[:15]:
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6]).isoformat()

                articles.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "source": feed_name,
                    "published": published,
                    "summary": entry.get("summary", "")[:300],
                })
            return articles
        except Exception as e:
            logger.error("RSS feed error", feed=feed_name, error=str(e))
            return []

    async def fetch_all(self) -> list[dict]:
        """Fetch all configured RSS feeds."""
        tasks = [self.fetch_feed(name, url) for name, url in RSS_FEEDS.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        articles = []
        for result in results:
            if isinstance(result, list):
                articles.extend(result)
        articles.sort(key=lambda x: x.get("published") or "", reverse=True)
        return articles
