import numpy as np
import pandas as pd
from typing import Optional
from datetime import datetime
import structlog

from app.ingestion.yahoo import YahooFinanceClient

logger = structlog.get_logger()


class BacktestEngine:
    """Backtesting engine for macro-based trading strategies."""

    def __init__(
        self,
        strategy: str = "regime_rotation",
        symbols: list[str] = None,
        initial_capital: float = 100000,
        parameters: dict = None,
    ):
        self.strategy = strategy
        self.symbols = symbols or ["SPY", "TLT", "GLD"]
        self.initial_capital = initial_capital
        self.parameters = parameters or {}
        self.yahoo = YahooFinanceClient()

    async def run(self, start_date: str = None, end_date: str = None) -> dict:
        """Run the backtest."""
        # Fetch data
        price_data = {}
        for sym in self.symbols:
            data = await self.yahoo.get_history(sym, period="5y", interval="1d")
            if data.get("data"):
                series = {d["timestamp"][:10]: d["close"] for d in data["data"]}
                price_data[sym] = series

        if len(price_data) < 1:
            return {"error": "Insufficient price data"}

        df = pd.DataFrame(price_data).dropna()
        if df.empty:
            return {"error": "No overlapping price data"}

        # Run strategy
        if self.strategy == "regime_rotation":
            result = self._regime_rotation(df)
        elif self.strategy == "momentum":
            result = self._momentum(df)
        elif self.strategy == "mean_reversion":
            result = self._mean_reversion(df)
        else:
            return {"error": f"Unknown strategy: {self.strategy}"}

        return result

    def _regime_rotation(self, df: pd.DataFrame) -> dict:
        """Regime-based rotation strategy."""
        returns = df.pct_change().dropna()
        lookback = self.parameters.get("lookback", 63)
        rebalance = self.parameters.get("rebalance_frequency", 21)

        portfolio_values = [self.initial_capital]
        trades = []

        for i in range(lookback, len(returns), rebalance):
            window = returns.iloc[i - lookback:i]
            sharpe = (window.mean() / window.std()) * np.sqrt(252)
            best = sharpe.idxmax()

            period_return = returns.iloc[i:i + rebalance][best].sum()
            new_value = portfolio_values[-1] * (1 + period_return)
            portfolio_values.append(new_value)
            trades.append({
                "date": str(returns.index[i]),
                "action": "rotate",
                "symbol": best,
                "signal": f"Best Sharpe: {round(sharpe[best], 2)}",
            })

        return self._compute_metrics(portfolio_values, df, trades)

    def _momentum(self, df: pd.DataFrame) -> dict:
        """Cross-asset momentum strategy."""
        returns = df.pct_change().dropna()
        lookback = self.parameters.get("lookback_period", 63)
        top_n = self.parameters.get("top_n", 2)
        rebalance = self.parameters.get("rebalance_frequency", 21)

        portfolio_values = [self.initial_capital]
        trades = []

        for i in range(lookback, len(returns), rebalance):
            momentum = returns.iloc[i - lookback:i].sum()
            top = momentum.nlargest(top_n).index.tolist()

            period_returns = returns.iloc[i:i + rebalance][top].mean(axis=1)
            period_total = period_returns.sum()
            new_value = portfolio_values[-1] * (1 + period_total)
            portfolio_values.append(new_value)
            trades.append({
                "date": str(returns.index[i]),
                "action": "rebalance",
                "symbols": top,
                "signal": f"Top {top_n} momentum",
            })

        return self._compute_metrics(portfolio_values, df, trades)

    def _mean_reversion(self, df: pd.DataFrame) -> dict:
        """Mean reversion strategy on the first two symbols."""
        if len(df.columns) < 2:
            return {"error": "Need at least 2 symbols for mean reversion"}

        sym1, sym2 = df.columns[0], df.columns[1]
        ratio = df[sym1] / df[sym2]
        z_score_entry = self.parameters.get("z_score_entry", 2.0)
        z_score_exit = self.parameters.get("z_score_exit", 0.5)
        window = self.parameters.get("window", 30)

        mean = ratio.rolling(window).mean()
        std = ratio.rolling(window).std()
        z = (ratio - mean) / std

        portfolio_values = [self.initial_capital]
        position = 0
        trades = []

        returns_s1 = df[sym1].pct_change()

        for i in range(window, len(z)):
            if position == 0:
                if z.iloc[i] > z_score_entry:
                    position = -1
                    trades.append({"date": str(z.index[i]), "action": "short_ratio", "z_score": round(z.iloc[i], 2)})
                elif z.iloc[i] < -z_score_entry:
                    position = 1
                    trades.append({"date": str(z.index[i]), "action": "long_ratio", "z_score": round(z.iloc[i], 2)})
            else:
                if abs(z.iloc[i]) < z_score_exit:
                    position = 0
                    trades.append({"date": str(z.index[i]), "action": "close", "z_score": round(z.iloc[i], 2)})

            ret = returns_s1.iloc[i] * position * 0.5
            portfolio_values.append(portfolio_values[-1] * (1 + ret))

        return self._compute_metrics(portfolio_values, df, trades)

    def _compute_metrics(self, portfolio_values: list, df: pd.DataFrame, trades: list) -> dict:
        """Compute backtest performance metrics."""
        pv = np.array(portfolio_values)
        returns = np.diff(pv) / pv[:-1]

        total_return = (pv[-1] / pv[0] - 1) * 100
        annual_return = total_return / max(len(returns) / 252, 1)
        volatility = np.std(returns) * np.sqrt(252) * 100
        sharpe = annual_return / volatility if volatility > 0 else 0

        running_max = np.maximum.accumulate(pv)
        drawdowns = (pv - running_max) / running_max * 100
        max_drawdown = np.min(drawdowns)

        # Benchmark (equal weight)
        bm_returns = df.pct_change().dropna().mean(axis=1)
        bm_total = (1 + bm_returns).cumprod().iloc[-1] - 1

        return {
            "strategy": self.strategy,
            "symbols": self.symbols,
            "metrics": {
                "total_return": round(total_return, 2),
                "annual_return": round(annual_return, 2),
                "volatility": round(volatility, 2),
                "sharpe_ratio": round(sharpe, 2),
                "max_drawdown": round(max_drawdown, 2),
                "total_trades": len(trades),
            },
            "benchmark": {
                "equal_weight_return": round(bm_total * 100, 2),
            },
            "portfolio_curve": [round(v, 2) for v in pv[::max(len(pv) // 100, 1)]],
            "trades": trades[-20:],
        }
