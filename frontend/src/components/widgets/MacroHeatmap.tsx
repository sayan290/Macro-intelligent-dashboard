'use client';
import React, { useEffect, useState } from 'react';
import { Activity } from 'lucide-react';
import { getChangeColor, formatPercent } from '@/lib/utils';
import api from '@/lib/api';

interface HeatmapItem {
  category: string;
  name: string;
  series_id: string;
  value: number | null;
  change_pct: number | null;
  trend: string;
}

export default function MacroHeatmap() {
  const [data, setData] = useState<HeatmapItem[]>([]);

  useEffect(() => {
    const fetch = async () => {
      try {
        const result = await api.getMacroHeatmap();
        setData(Array.isArray(result) ? result : getMockHeatmap());
      } catch {
        setData(getMockHeatmap());
      }
    };
    fetch();
  }, []);

  const categories = [...new Set(data.map(d => d.category))];

  return (
    <div id="macro-heatmap" className="glass-card p-6">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="w-5 h-5 text-accent-emerald" />
        <h3 className="text-sm font-semibold text-dark-100">Macro Heatmap</h3>
      </div>

      <div className="space-y-4">
        {categories.map(cat => (
          <div key={cat}>
            <h4 className="text-[10px] font-bold text-dark-400 uppercase tracking-widest mb-2">{cat}</h4>
            <div className="grid grid-cols-2 gap-2">
              {data.filter(d => d.category === cat).map(item => (
                <div
                  key={item.series_id}
                  className="p-2.5 bg-dark-800/40 rounded-lg border border-dark-600/20 hover:border-dark-500/30 transition-all"
                >
                  <p className="text-[10px] text-dark-400 truncate">{item.name}</p>
                  <div className="flex items-baseline gap-2 mt-0.5">
                    <span className="text-sm font-bold font-mono text-dark-100">
                      {item.value !== null ? item.value.toLocaleString() : '—'}
                    </span>
                    <span className={`text-[10px] font-mono font-medium ${getChangeColor(item.change_pct)}`}>
                      {formatPercent(item.change_pct)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function getMockHeatmap(): HeatmapItem[] {
  return [
    { category: 'growth', name: 'GDP', series_id: 'GDP', value: 27000, change_pct: 0.5, trend: 'up' },
    { category: 'growth', name: 'Unemployment', series_id: 'UNRATE', value: 3.7, change_pct: -0.1, trend: 'down' },
    { category: 'inflation', name: 'CPI', series_id: 'CPIAUCSL', value: 310, change_pct: 0.3, trend: 'up' },
    { category: 'inflation', name: 'Core CPI', series_id: 'CPILFESL', value: 315, change_pct: 0.2, trend: 'up' },
    { category: 'rates', name: 'Fed Funds', series_id: 'FEDFUNDS', value: 5.33, change_pct: 0, trend: 'neutral' },
    { category: 'rates', name: '10Y Treasury', series_id: 'DGS10', value: 4.2, change_pct: -0.05, trend: 'down' },
    { category: 'rates', name: '10Y-2Y Spread', series_id: 'T10Y2Y', value: -0.3, change_pct: 0.1, trend: 'up' },
    { category: 'sentiment', name: 'VIX', series_id: 'VIXCLS', value: 14, change_pct: -3.2, trend: 'down' },
  ];
}
