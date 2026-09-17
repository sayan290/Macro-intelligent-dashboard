from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class RegimeState(Base):
    __tablename__ = "regime_states"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    regime = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    sub_regimes = Column(JSONB, server_default='{}')
    indicators = Column(JSONB, server_default='{}')
    description = Column(Text)


class RegimeTransition(Base):
    __tablename__ = "regime_transitions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    from_regime = Column(String(50), nullable=False)
    to_regime = Column(String(50), nullable=False)
    transition_date = Column(DateTime, nullable=False)
    confidence = Column(Float)
    trigger_factors = Column(JSONB, server_default='{}')
