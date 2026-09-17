from sqlalchemy import Column, Integer, BigInteger, String, Float, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class MacroSeries(Base):
    __tablename__ = "macro_series"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    series_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(500), nullable=False)
    source = Column(String(50), nullable=False)
    category = Column(String(100))
    frequency = Column(String(20))
    units = Column(String(200))
    description = Column(Text)
    last_updated = Column(DateTime)
    metadata_json = Column(JSONB, server_default='{}')


class MacroDataPoint(Base):
    __tablename__ = "macro_data_points"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    series_id = Column(String(100), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    value = Column(Float, nullable=False)
    previous_value = Column(Float)
    change = Column(Float)
    change_pct = Column(Float)
