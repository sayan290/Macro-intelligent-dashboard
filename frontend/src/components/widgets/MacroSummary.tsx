'use client';
import React, { useEffect, useState } from 'react';
import { Globe, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { formatNumber, getChangeColor, formatPercent } from '@/lib/utils';
import api from '@/lib/api';

interface MacroCategory {
  series_id: string;
  name: string;
  value: number | null;
  change_pct: number | null;
  units: string;
}

export default function MacroSummary() {
  const [dashboard, setDashboard] = useState<Record<string, MacroCategory[]>>({});

  useEffect(() => {
    const fetch = async () => {
      try {
        const data = await api.getMacroDashboard();
        setDashboard(data && typeof data === 'object' ? data : getMockDashboard());
      } catch {
        setDashboard(getMockDashboard());
      }
    };
    fetch();
  }, []);

  const categories = Object.keys(dashboard);

  return (
    <div id="macro-summary" className="glass-card p-6">
      <div className="flex items-center gap-2 mb-4">
        <Globe className="w-5 h-5 text-accent-blue" />
        <h3 className="text-sm font-semibold text-dark-100">Macro Summary</h3>
      </div>

      <div className="space-y-4">
        {categories.slice(0, 4).map(cat => (
          <div key={cat}>
            <h4 className="text-[10px] font-bold text-dark-400 uppercase tracking-widest mb-2">{cat}</h4>
            <div className="space-y-1.5">
              {(dashboard[cat] || []).slice(0, 3).map(item => {
                const TrendIcon = (item.change_pct || 0) > 0 ? TrendingUp : (item.change_pct || 0) < 0 ? TrendingDown : Minus;
                return (
                  <div key={item.series_id} className="flex items-center justify-between py-1.5 px-2 rounded-lg hover:bg-dark-800/30 transition-all">
                    <div className="flex items-center gap-2">
                      <TrendIcon className={`w-3 h-3 ${getChangeColor(item.change_pct)}`} />
                      <span className="text-xs text-dark-200">{item.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-bold text-dark-100">
                        {item.value !== null ? formatNumber(item.value) : '—'}
                      </span>
                      <span className={`text-[10px] font-mono ${getChangeColor(item.change_pct)}`}>
                        {formatPercent(item.change_pct)}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function getMockDashboard(): Record<string, MacroCategory[]> {
  return {
    growth: [
      { series_id: 'GDP', name: 'GDP', value: 27000, change_pct: 0.5, units: 'B$' },
      { series_id: 'PAYEMS', name: 'Nonfarm Payrolls', value: 157000, change_pct: 0.2, units: 'K' },
      { series_id: 'UNRATE', name: 'Unemployment', value: 3.7, change_pct: -0.1, units: '%' },
    ],
    inflation: [
      { series_id: 'CPIAUCSL', name: 'CPI', value: 310, change_pct: 0.3, units: 'Index' },
      { series_id: 'T10YIE', name: '10Y Breakeven', value: 2.3, change_pct: 0.05, units: '%' },
    ],
    rates: [
      { series_id: 'FEDFUNDS', name: 'Fed Funds', value: 5.33, change_pct: 0, units: '%' },
      { series_id: 'DGS10', name: '10Y Treasury', value: 4.2, change_pct: -0.05, units: '%' },
      { series_id: 'T10Y2Y', name: 'Yield Curve', value: -0.3, change_pct: 0.1, units: '%' },
    ],
    sentiment: [
      { series_id: 'VIXCLS', name: 'VIX', value: 14, change_pct: -3.2, units: 'Index' },
      { series_id: 'UMCSENT', name: 'Consumer Sent.', value: 67, change_pct: 1.2, units: 'Index' },
    ],
  };
}
