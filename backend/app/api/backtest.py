from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional

from app.backtest.engine import BacktestEngine

router = APIRouter()


class BacktestRequest(BaseModel):
    strategy: str  # regime_rotation, momentum, mean_reversion
    symbols: list[str] = ["SPY", "TLT", "GLD"]
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    initial_capital: float = 100000
    parameters: dict = {}


@router.post("/run")
async def run_backtest(request: BacktestRequest):
    """Run a backtest with specified strategy."""
    engine = BacktestEngine(
        strategy=request.strategy,
        symbols=request.symbols,
        initial_capital=request.initial_capital,
        parameters=request.parameters,
    )
    results = await engine.run(
        start_date=request.start_date,
        end_date=request.end_date,
    )
    return results


@router.get("/strategies")
async def list_strategies():
    """List available backtesting strategies."""
    return {
        "strategies": [
            {
                "id": "regime_rotation",
                "name": "Regime-Based Rotation",
                "description": "Rotates between asset classes based on detected macro regime",
                "parameters": {
                    "rebalance_frequency": "Monthly/Weekly",
                    "risk_budget": "Max allocation per asset",
                },
            },
            {
                "id": "momentum",
                "name": "Cross-Asset Momentum",
                "description": "Follows momentum signals across asset classes",
                "parameters": {
                    "lookback_period": "Days for momentum calculation",
                    "top_n": "Number of assets to hold",
                },
            },
            {
                "id": "mean_reversion",
                "name": "Mean Reversion",
                "description": "Trades mean reversion in correlated pairs",
                "parameters": {
                    "z_score_entry": "Z-score threshold for entry",
                    "z_score_exit": "Z-score threshold for exit",
                },
            },
        ]
    }
