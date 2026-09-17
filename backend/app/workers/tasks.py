import structlog
from datetime import datetime

logger = structlog.get_logger()


async def task_update_market_data():
    """Update market data from all sources."""
    logger.info("Task: Updating market data")
    try:
        from app.ingestion.yahoo import YahooFinanceClient
        yahoo = YahooFinanceClient()

        symbols = ["SPY", "QQQ", "IWM", "DIA", "TLT", "GLD", "USO", "BTC-USD", "ETH-USD"]
        for symbol in symbols:
            try:
                await yahoo.get_quote(symbol)
            except Exception as e:
                logger.warning(f"Failed to update {symbol}", error=str(e))

        logger.info("Market data updated", count=len(symbols))
    except Exception as e:
        logger.error("Market data update failed", error=str(e))


async def task_update_macro_data():
    """Update macro economic data."""
    logger.info("Task: Updating macro data")
    try:
        from app.ingestion.fred import FredClient
        fred = FredClient()

        series = ["GDP", "UNRATE", "CPIAUCSL", "FEDFUNDS", "DGS10", "T10Y2Y", "VIXCLS", "M2SL"]
        for sid in series:
            try:
                await fred.get_latest(sid)
            except Exception as e:
                logger.warning(f"Failed to update {sid}", error=str(e))

        logger.info("Macro data updated", count=len(series))
    except Exception as e:
        logger.error("Macro data update failed", error=str(e))


async def task_detect_regime():
    """Run regime detection."""
    logger.info("Task: Detecting regime")
    try:
        from app.analysis.regime_detector import RegimeDetector
        from app.database import AsyncSessionLocal, get_redis
        from app.models.regime import RegimeState
        import json

        detector = RegimeDetector()
        result = await detector.detect()

        # Store in database
        async with AsyncSessionLocal() as db:
            state = RegimeState(
                timestamp=datetime.utcnow(),
                regime=result["regime"],
                confidence=result["confidence"],
                sub_regimes=result.get("sub_regimes", {}),
                indicators=result.get("indicators", {}),
                description=result.get("description"),
            )
            db.add(state)
            await db.commit()

        # Cache in Redis
        redis = await get_redis()
        await redis.setex("regime:current", 300, json.dumps(result, default=str))

        logger.info("Regime detected", regime=result["regime"], confidence=result["confidence"])
    except Exception as e:
        logger.error("Regime detection failed", error=str(e))


async def task_check_alerts():
    """Check all active alerts."""
    logger.info("Task: Checking alerts")
    try:
        from app.alerts.engine import AlertEngine
        engine = AlertEngine()
        await engine.check_all_alerts()
    except Exception as e:
        logger.error("Alert check failed", error=str(e))


async def task_scrape_calendar():
    """Scrape economic calendar."""
    logger.info("Task: Scraping calendar")
    try:
        from app.ingestion.calendar_scraper import CalendarScraper
        from app.database import AsyncSessionLocal
        from app.models.events import EconomicEvent

        scraper = CalendarScraper()
        events = await scraper.get_mock_events()

        async with AsyncSessionLocal() as db:
            for ev in events:
                event = EconomicEvent(
                    event_name=ev["event_name"],
                    country=ev["country"],
                    datetime_utc=ev.get("datetime_utc"),
                    impact=ev.get("impact"),
                    category=ev.get("category"),
                    forecast=ev.get("forecast"),
                    previous=ev.get("previous"),
                    source=ev.get("source", "scraper"),
                    created_at=datetime.utcnow(),
                )
                db.add(event)
            await db.commit()

        logger.info("Calendar scraped", events=len(events))
    except Exception as e:
        logger.error("Calendar scrape failed", error=str(e))


async def task_ingest_news():
    """Ingest news from RSS feeds."""
    logger.info("Task: Ingesting news")
    try:
        from app.ingestion.news_rss import NewsRSSClient
        from app.database import get_redis
        import json

        news = NewsRSSClient()
        articles = await news.fetch_all()

        redis = await get_redis()
        await redis.setex("news:latest", 900, json.dumps(articles[:20], default=str))

        logger.info("News ingested", count=len(articles))
    except Exception as e:
        logger.error("News ingestion failed", error=str(e))
