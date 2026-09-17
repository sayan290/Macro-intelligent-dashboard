import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.config import get_settings
from app.database import engine, redis_client

settings = get_settings()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Macro Intelligence Dashboard")
    # Startup
    yield
    # Shutdown
    await engine.dispose()
    await redis_client.close()
    logger.info("Shutdown complete")


app = FastAPI(
    title="Macro Intelligence Dashboard",
    description="Open-source macroeconomic research and market intelligence platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "macro-intel-dashboard"}