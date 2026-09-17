from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://macrointel:macrointel_secret@localhost:5432/macrointel"
    redis_url: str = "redis://localhost:6379/0"
    chroma_url: str = "http://localhost:8000"
    
    # AI
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "deepseek-r1:7b"
    embedding_model: str = "nomic-embed-text"
    
    # API Keys (free tiers)
    fred_api_key: Optional[str] = None
    alpha_vantage_key: Optional[str] = None
    twelve_data_key: Optional[str] = None
    
    # Notifications
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    discord_webhook_url: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_pass: Optional[str] = None
    
    # App
    log_level: str = "INFO"
    data_refresh_interval: int = 300
    cache_ttl: int = 600
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
