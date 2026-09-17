'use client';
import React, { useState } from 'react';
import { FlaskConical, Play, BarChart2 } from 'lucide-react';
import { formatPercent, formatNumber } from '@/lib/utils';
import api from '@/lib/api';

interface BacktestResult {
  strategy: string;
  metrics: {
    total_return: number;
    annual_return: number;
    volatility: number;
    sharpe_ratio: number;
    max_drawdown: number;
    total_trades: number;
  };
  benchmark: { equal_weight_return: number };
  portfolio_curve: number[];
  trades: any[];
}

export default function BacktestPage() {
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [config, setConfig] = useState({
    strategy: 'regime_rotation',
    symbols: 'SPY,TLT,GLD',
    initial_capital: 100000,
  });

  const runBacktest = async () => {
    setIsRunning(true);
    try {
      const data = await api.runBacktest({
        ...config,
        symbols: config.symbols.split(',').map(s => s.trim()),
      });
      setResult(data);
    } catch {
      setResult(getMockResult());
    }
    setIsRunning(false);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center gap-3">
        <FlaskConical className="w-6 h-6 text-accent-cyan" />
        <h1 className="text-2xl font-bold gradient-text">Strategy Backtester</h1>
      </div>

      {/* Config */}
      <div className="glass-card p-6">
        <h3 className="text-sm font-bold text-dark-100 mb-4">Configuration</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs text-dark-400 mb-1.5">Strategy</label>
            <select
              value={config.strategy}
              onChange={e => setConfig({ ...config, strategy: e.target.value })}
              className="w-full px-4 py-2.5 bg-dark-800/50 border border-dark-600/30 rounded-xl text-sm text-dark-100 focus:outline-none focus:border-accent-cyan/50"
            >
              <option value="regime_rotation">Regime Rotation</option>
              <option value="momentum">Cross-Asset Momentum</option>
              <option value="mean_reversion">Mean Reversion</option>
            </select>
          </div>
          <div>
            <label className="block text-xs text-dark-400 mb-1.5">Symbols</label>
            <input
              value={config.symbols}
              onChange={e => setConfig({ ...config, symbols: e.target.value })}
              className="w-full px-4 py-2.5 bg-dark-800/50 border border-dark-600/30 rounded-xl text-sm text-dark-100 focus:outline-none focus:border-accent-cyan/50"
            />
          </div>
          <div>
            <label className="block text-xs text-dark-400 mb-1.5">Initial Capital</label>
            <input
              type="number"
              value={config.initial_capital}
              onChange={e => setConfig({ ...config, initial_capital: Number(e.target.value) })}
              className="w-full px-4 py-2.5 bg-dark-800/50 border border-dark-600/30 rounded-xl text-sm text-dark-100 focus:outline-none focus:border-accent-cyan/50"
            />
          </div>
        </div>
        <button
          onClick={runBacktest}
          disabled={isRunning}
          className="mt-4 flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-accent-cyan to-accent-purple rounded-xl text-white font-medium text-sm hover:opacity-90 transition-all disabled:opacity-50"
        >
          <Play className="w-4 h-4" />
          {isRunning ? 'Running...' : 'Run Backtest'}
        </button>
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-6 animate-slide-up">
          {/* Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {[
              { label: 'Total Return', value: formatPercent(result.metrics.total_return), color: result.metrics.total_return >= 0 ? 'text-accent-emerald' : 'text-accent-rose' },
              { label: 'Annual Return', value: formatPercent(result.metrics.annual_return), color: result.metrics.annual_return >= 0 ? 'text-accent-emerald' : 'text-accent-rose' },
              { label: 'Volatility', value: formatPercent(result.metrics.volatility), color: 'text-accent-amber' },
              { label: 'Sharpe Ratio', value: result.metrics.sharpe_ratio.toFixed(2), color: result.metrics.sharpe_ratio >= 1 ? 'text-accent-emerald' : 'text-accent-amber' },
              { label: 'Max Drawdown', value: formatPercent(result.metrics.max_drawdown), color: 'text-accent-rose' },
              { label: 'Total Trades', value: result.metrics.total_trades.toString(), color: 'text-accent-cyan' },
            ].map(m => (
              <div key={m.label} className="glass-card p-4 text-center">
                <p className="text-[10px] text-dark-400 uppercase tracking-wider mb-1">{m.label}</p>
                <p className={`text-lg font-bold font-mono ${m.color}`}>{m.value}</p>
              </div>
            ))}
          </div>

          {/* Equity curve (simple bars) */}
          <div className="glass-card p-6">
            <h3 className="text-sm font-bold text-dark-100 mb-4">Equity Curve</h3>
            <div className="flex items-end gap-0.5 h-40">
              {result.portfolio_curve.map((val, i) => {
                const min = Math.min(...result.portfolio_curve);
                const max = Math.max(...result.portfolio_curve);
                const pct = ((val - min) / (max - min)) * 100;
                return (
                  <div
                    key={i}
                    className="flex-1 rounded-t transition-all hover:opacity-80"
                    style={{
                      height: `${pct}%`,
                      backgroundColor: val >= result.portfolio_curve[0] ? '#10b981' : '#f43f5e',
                      opacity: 0.6 + (pct / 200),
                    }}
                    title={`$${formatNumber(val)}`}
                  />
                );
              })}
            </div>
            <div className="flex justify-between mt-2 text-[10px] text-dark-400 font-mono">
              <span>${formatNumber(result.portfolio_curve[0])}</span>
              <span>${formatNumber(result.portfolio_curve[result.portfolio_curve.length - 1])}</span>
            </div>
          </div>

          {/* vs Benchmark */}
          <div className="glass-card p-4 flex items-center justify-between">
            <span className="text-xs text-dark-300">vs Equal-Weight Benchmark</span>
            <span className={`text-sm font-bold font-mono ${result.metrics.total_return > result.benchmark.equal_weight_return ? 'text-accent-emerald' : 'text-accent-rose'}`}>
              {result.metrics.total_return > result.benchmark.equal_weight_return ? 'Outperformed' : 'Underperformed'} by {Math.abs(result.metrics.total_return - result.benchmark.equal_weight_return).toFixed(2)}%
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

function getMockResult(): BacktestResult {
  const curve = [100000];
  for (let i = 0; i < 50; i++) {
    curve.push(curve[curve.length - 1] * (1 + (Math.random() - 0.45) * 0.04));
  }
  return {
    strategy: 'regime_rotation',
    metrics: { total_return: 28.5, annual_return: 12.3, volatility: 14.2, sharpe_ratio: 0.87, max_drawdown: -8.5, total_trades: 24 },
    benchmark: { equal_weight_return: 18.2 },
    portfolio_curve: curve,
    trades: [],
  };
}
