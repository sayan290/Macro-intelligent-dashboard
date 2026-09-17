'use client';
import React, { useEffect, useState } from 'react';
import { Globe, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { formatNumber, formatPercent, getChangeColor } from '@/lib/utils';
import api from '@/lib/api';

interface MacroIndicator {
  series_id: string;
  name: string;
  value: number | null;
  change_pct: number | null;
  units: string;
  date: string | null;
}

export default function MacroPage() {
  const [dashboard, setDashboard] = useState<Record<string, MacroIndicator[]>>({});

  useEffect(() => {
    const fetch = async () => {
      try {
        const data = await api.getMacroDashboard();
        setDashboard(data && typeof data === 'object' ? data : {});
      } catch {
        setDashboard(getMockDashboard());
      }
    };
    fetch();
  }, []);

  const categoryLabels: Record<string, { label: string; icon: string; color: string }> = {
    growth: { label: 'Economic Growth', icon: '📈', color: 'text-accent-emerald' },
    inflation: { label: 'Inflation', icon: '🔥', color: 'text-accent-amber' },
    rates: { label: 'Interest Rates', icon: '🏦', color: 'text-accent-blue' },
    money: { label: 'Money Supply', icon: '💰', color: 'text-accent-purple' },
    sentiment: { label: 'Sentiment', icon: '📊', color: 'text-accent-cyan' },
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center gap-3">
        <Globe className="w-6 h-6 text-accent-blue" />
        <h1 className="text-2xl font-bold gradient-text">Macro Dashboard</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {Object.entries(dashboard).map(([category, indicators]) => {
          const meta = categoryLabels[category] || { label: category, icon: '📋', color: 'text-dark-200' };
          return (
            <div key={category} className="glass-card p-6">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-lg">{meta.icon}</span>
                <h2 className={`text-sm font-bold uppercase tracking-wider ${meta.color}`}>{meta.label}</h2>
              </div>

              <div className="space-y-2">
                {(indicators as MacroIndicator[]).map(ind => {
                  const TrendIcon = (ind.change_pct || 0) > 0 ? TrendingUp : (ind.change_pct || 0) < 0 ? TrendingDown : Minus;
                  return (
                    <div key={ind.series_id} className="flex items-center justify-between p-3 bg-dark-800/30 rounded-xl hover:bg-dark-800/50 transition-all">
                      <div className="flex items-center gap-3">
                        <TrendIcon className={`w-4 h-4 ${getChangeColor(ind.change_pct)}`} />
                        <div>
                          <p className="text-sm font-medium text-dark-100">{ind.name}</p>
                          <p className="text-[10px] text-dark-400">{ind.series_id} • {ind.units}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-bold font-mono text-dark-100">
                          {ind.value !== null ? formatNumber(ind.value) : '—'}
                        </p>
                        <p className={`text-xs font-mono ${getChangeColor(ind.change_pct)}`}>
                          {formatPercent(ind.change_pct)}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function getMockDashboard(): Record<string, MacroIndicator[]> {
  return {
    growth: [
      { series_id: 'GDP', name: 'GDP', value: 27000, change_pct: 0.5, units: 'Billions $', date: '2024-01' },
      { series_id: 'PAYEMS', name: 'Nonfarm Payrolls', value: 157000, change_pct: 0.2, units: 'Thousands', date: '2024-01' },
      { series_id: 'UNRATE', name: 'Unemployment Rate', value: 3.7, change_pct: -0.1, units: '%', date: '2024-01' },
    ],
    inflation: [
      { series_id: 'CPIAUCSL', name: 'CPI All Urban', value: 310, change_pct: 0.3, units: 'Index', date: '2024-01' },
      { series_id: 'CPILFESL', name: 'Core CPI', value: 315, change_pct: 0.2, units: 'Index', date: '2024-01' },
      { series_id: 'T10YIE', name: '10Y Breakeven', value: 2.3, change_pct: 0.05, units: '%', date: '2024-01' },
    ],
    rates: [
      { series_id: 'FEDFUNDS', name: 'Fed Funds Rate', value: 5.33, change_pct: 0, units: '%', date: '2024-01' },
      { series_id: 'DGS10', name: '10Y Treasury', value: 4.2, change_pct: -0.05, units: '%', date: '2024-01' },
      { series_id: 'T10Y2Y', name: '10Y-2Y Spread', value: -0.3, change_pct: 0.1, units: '%', date: '2024-01' },
    ],
    sentiment: [
      { series_id: 'VIXCLS', name: 'VIX', value: 14, change_pct: -3.2, units: 'Index', date: '2024-01' },
      { series_id: 'UMCSENT', name: 'Consumer Sentiment', value: 67, change_pct: 1.2, units: 'Index', date: '2024-01' },
    ],
  };
}
