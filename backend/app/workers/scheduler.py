import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import structlog

from app.workers.tasks import (
    task_update_market_data,
    task_update_macro_data,
    task_detect_regime,
    task_check_alerts,
    task_scrape_calendar,
    task_ingest_news,
)

logger = structlog.get_logger()


def create_scheduler() -> AsyncIOScheduler:
    """Create and configure the scheduler."""
    scheduler = AsyncIOScheduler()

    # Market data - every 5 minutes during market hours
    scheduler.add_job(
        task_update_market_data,
        IntervalTrigger(minutes=5),
        id="update_market",
        name="Update Market Data",
        replace_existing=True,
    )

    # Macro data - every hour
    scheduler.add_job(
        task_update_macro_data,
        IntervalTrigger(hours=1),
        id="update_macro",
        name="Update Macro Data",
        replace_existing=True,
    )

    # Regime detection - every 30 minutes
    scheduler.add_job(
        task_detect_regime,
        IntervalTrigger(minutes=30),
        id="detect_regime",
        name="Detect Regime",
        replace_existing=True,
    )

    # Alert checks - every 2 minutes
    scheduler.add_job(
        task_check_alerts,
        IntervalTrigger(minutes=2),
        id="check_alerts",
        name="Check Alerts",
        replace_existing=True,
    )

    # Calendar scraping - daily at 6 AM UTC
    scheduler.add_job(
        task_scrape_calendar,
        CronTrigger(hour=6, minute=0),
        id="scrape_calendar",
        name="Scrape Calendar",
        replace_existing=True,
    )

    # News ingestion - every 15 minutes
    scheduler.add_job(
        task_ingest_news,
        IntervalTrigger(minutes=15),
        id="ingest_news",
        name="Ingest News",
        replace_existing=True,
    )

    return scheduler


async def main():
    """Main entry point for the worker process."""
    logger.info("Starting worker scheduler")
    scheduler = create_scheduler()
    scheduler.start()

    try:
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down scheduler")
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
