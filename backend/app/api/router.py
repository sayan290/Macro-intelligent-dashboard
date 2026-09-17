from fastapi import APIRouter
from app.api import market, macro, regime, correlation, calendar, alerts, ai_assistant, backtest

api_router = APIRouter()

api_router.include_router(market.router, prefix="/market", tags=["Market Data"])
api_router.include_router(macro.router, prefix="/macro", tags=["Macro Data"])
api_router.include_router(regime.router, prefix="/regime", tags=["Regime Detection"])
api_router.include_router(correlation.router, prefix="/correlation", tags=["Correlation"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["Economic Calendar"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(ai_assistant.router, prefix="/ai", tags=["AI Assistant"])
api_router.include_router(backtest.router, prefix="/backtest", tags=["Backtesting"])