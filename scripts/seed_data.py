"""Seed initial data into the database."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)) + '/backend')

from app.database import AsyncSessionLocal
from app.models.events import EconomicEvent
from app.ingestion.calendar_scraper import CalendarScraper
from datetime import datetime


async def seed():
    print("Seeding economic events...")
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
                source="seed",
                created_at=datetime.utcnow(),
            )
            db.add(event)
        await db.commit()
    print(f"Seeded {len(events)} events.")


if __name__ == "__main__":
    asyncio.run(seed())
