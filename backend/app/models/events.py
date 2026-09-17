from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from datetime import datetime
from app.database import Base


class EconomicEvent(Base):
    __tablename__ = "economic_events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_name = Column(String(300), nullable=False)
    country = Column(String(5), nullable=False)
    datetime_utc = Column(DateTime, nullable=False, index=True)
    impact = Column(String(10))
    category = Column(String(100))
    actual = Column(String(50))
    forecast = Column(String(50))
    previous = Column(String(50))
    source = Column(String(50))
    is_processed = Column(Boolean, server_default='false')
    created_at = Column(DateTime, default=datetime.utcnow)


class EventImpact(Base):
    __tablename__ = "event_impacts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, nullable=False)
    symbol = Column(String(50), nullable=False)
    pre_event_price = Column(Float)
    post_event_price_5m = Column(Float)
    post_event_price_1h = Column(Float)
    post_event_price_1d = Column(Float)
    volatility_impact = Column(Float)
    direction = Column(String(10))
