from sqlalchemy import Column, BigInteger, Integer, String, Float, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.database import Base


class MarketData(Base):
    __tablename__ = "market_data"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(50), nullable=False, index=True)
    asset_class = Column(String(30), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float, nullable=False)
    volume = Column(Float)
    metadata_json = Column(JSONB, server_default='{}')


class MarketDataDaily(Base):
    __tablename__ = "market_data_daily"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(50), nullable=False, index=True)
    asset_class = Column(String(30), nullable=False)
    date = Column(DateTime, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float, nullable=False)
    adj_close = Column(Float)
    volume = Column(BigInteger)
    change_pct = Column(Float)
