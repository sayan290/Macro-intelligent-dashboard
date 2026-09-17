'use client';
import React, { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, BarChart2 } from 'lucide-react';
import PriceChart from '@/components/charts/PriceChart';
import { formatPercent, getChangeColor, formatNumber } from '@/lib/utils';
import api from '@/lib/api';

interface AssetQuote {
  symbol: string;
  price: number;
  change_pct: number;
  volume: number;
  high: number;
  low: number;
}

export default function MarketsPage() {
  const [overview, setOverview] = useState<Record<string, AssetQuote[]>>({});
  const [selectedSymbol, setSelectedSymbol] = useState('SPY');
  const [heatmap, setHeatmap] = useState<any[]>([]);

  useEffect(() => {
    const fetch = async () => {
      try {
        const data = await api.getMarketOverview();
        setOverview(data || {});
      } catch {
        setOverview(getMockOverview());
      }
      try {
        const hm = await api.getMarketHeatmap();
        setHeatmap(Array.isArray(hm) ? hm : getMockHeatmap());
      } catch {
        setHeatmap(getMockHeatmap());
      }
    };
    fetch();
  }, []);

  const assetClasses = Object.entries(overview);

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center gap-3">
        <BarChart2 className="w-6 h-6 text-accent-cyan" />
        <h1 className="text-2xl font-bold gradient-text">Markets Overview</h1>
      </div>

      {/* Chart */}
      <PriceChart symbol={selectedSymbol} period="3mo" />

      {/* Asset classes */}
      {assetClasses.length > 0 ? assetClasses.map(([cls, assets]) => (
        <div key={cls} className="glass-card p-6">
          <h2 className="text-sm font-bold text-dark-100 uppercase tracking-wider mb-4">{cls}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {(assets as AssetQuote[]).map(asset => (
              <button
                key={asset.symbol}
                onClick={() => setSelectedSymbol(asset.symbol)}
                className={`p-4 rounded-xl border transition-all text-left ${
                  selectedSymbol === asset.symbol
                    ? 'bg-accent-cyan/10 border-accent-cyan/30'
                    : 'bg-dark-800/30 border-dark-600/20 hover:border-dark-500/40'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-bold text-dark-100">{asset.symbol}</span>
                  {asset.change_pct >= 0 ? (
                    <TrendingUp className="w-4 h-4 text-accent-emerald" />
                  ) : (
                    <TrendingDown className="w-4 h-4 text-accent-rose" />
                  )}
                </div>
                <p className="text-lg font-bold font-mono text-dark-100 mt-1">
                  ${asset.price?.toLocaleString()}
                </p>
                <p className={`text-xs font-mono font-medium ${getChangeColor(asset.change_pct)}`}>
                  {formatPercent(asset.change_pct)}
                </p>
              </button>
            ))}
          </div>
        </div>
      )) : (
        <div className="glass-card p-6">
          <p className="text-dark-400 text-center py-8">Loading market data...</p>
        </div>
      )}

      {/* Sector Heatmap */}
      <div className="glass-card p-6">
        <h2 className="text-sm font-bold text-dark-100 uppercase tracking-wider mb-4">Sector Performance</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
          {heatmap.map(item => (
            <div
              key={item.symbol}
              className={`p-3 rounded-xl border border-dark-600/20 text-center transition-all hover:scale-105 ${
                (item.change_pct || 0) >= 0 ? 'bg-emerald-500/5' : 'bg-rose-500/5'
              }`}
            >
              <p className="text-[10px] text-dark-300 font-medium truncate">{item.sector}</p>
              <p className={`text-sm font-bold font-mono mt-1 ${getChangeColor(item.change_pct)}`}>
                {formatPercent(item.change_pct)}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function getMockOverview(): Record<string, AssetQuote[]> {
  return {
    equity: [
      { symbol: 'SPY', price: 525.3, change_pct: 0.45, volume: 85000000, high: 527, low: 523 },
      { symbol: 'QQQ', price: 445.1, change_pct: 0.72, volume: 55000000, high: 447, low: 443 },
      { symbol: 'IWM', price: 198.5, change_pct: -0.32, volume: 30000000, high: 200, low: 197 },
    ],
    crypto: [
      { symbol: 'bitcoin', price: 67500, change_pct: 1.3, volume: 25000000000, high: 68500, low: 66000 },
      { symbol: 'ethereum', price: 3450, change_pct: 2.15, volume: 12000000000, high: 3550, low: 3400 },
    ],
    bond: [
      { symbol: 'TLT', price: 92.5, change_pct: -0.18, volume: 20000000, high: 93, low: 92 },
    ],
  };
}

function getMockHeatmap(): any[] {
  return [
    { sector: 'Technology', symbol: 'XLK', change_pct: 1.2 },
    { sector: 'Healthcare', symbol: 'XLV', change_pct: -0.4 },
    { sector: 'Financial', symbol: 'XLF', change_pct: 0.8 },
    { sector: 'Energy', symbol: 'XLE', change_pct: -1.1 },
    { sector: 'Consumer', symbol: 'XLY', change_pct: 0.3 },
    { sector: 'Industrial', symbol: 'XLI', change_pct: 0.5 },
  ];
}
