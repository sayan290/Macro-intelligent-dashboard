from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    alert_type = Column(String(50), nullable=False)
    condition = Column(JSONB, nullable=False)
    is_active = Column(Boolean, server_default='true')
    channels = Column(JSONB, server_default='["telegram"]')
    cooldown_minutes = Column(Integer, server_default='60')
    last_triggered = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class AlertTrigger(Base):
    __tablename__ = "alert_triggers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_id = Column(Integer, nullable=False)
    triggered_at = Column(DateTime, default=datetime.utcnow)
    message = Column(Text)
    data = Column(JSONB)
    delivered = Column(Boolean, server_default='false')
