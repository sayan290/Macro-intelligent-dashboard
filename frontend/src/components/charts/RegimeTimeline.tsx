'use client';
import React, { useEffect, useState } from 'react';
import api from '@/lib/api';

interface RegimeState {
  id: number;
  regime: string;
  confidence: number;
  timestamp: string;
}

const REGIME_COLORS: Record<string, string> = {
  goldilocks: '#10b981',
  reflation: '#f59e0b',
  stagflation: '#ef4444',
  deflation: '#3b82f6',
  unknown: '#6b7280',
};

export default function RegimeTimeline() {
  const [history, setHistory] = useState<RegimeState[]>([]);

  useEffect(() => {
    const fetch = async () => {
      try {
        const data = await api.getRegimeHistory(20);
        setHistory(Array.isArray(data) ? data : getMockHistory());
      } catch {
        setHistory(getMockHistory());
      }
    };
    fetch();
  }, []);

  return (
    <div className="glass-card p-6">
      <h3 className="text-sm font-semibold text-dark-100 mb-4">Regime Timeline</h3>

      <div className="flex items-center gap-1 h-8 mb-3">
        {history.map((state, i) => (
          <div
            key={i}
            className="flex-1 rounded-sm transition-all hover:opacity-80 group relative"
            style={{
              backgroundColor: REGIME_COLORS[state.regime] || REGIME_COLORS.unknown,
              opacity: 0.3 + state.confidence * 0.7,
            }}
            title={`${state.regime} (${Math.round(state.confidence * 100)}%)`}
          >
            <div className="hidden group-hover:block absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-dark-700 rounded text-[10px] text-white whitespace-nowrap z-10">
              {state.regime} — {Math.round(state.confidence * 100)}%
            </div>
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3">
        {Object.entries(REGIME_COLORS).filter(([k]) => k !== 'unknown').map(([regime, color]) => (
          <div key={regime} className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: color }} />
            <span className="text-[10px] text-dark-300 capitalize">{regime}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function getMockHistory(): RegimeState[] {
  const regimes = ['goldilocks', 'goldilocks', 'reflation', 'reflation', 'goldilocks',
    'stagflation', 'stagflation', 'deflation', 'deflation', 'goldilocks',
    'goldilocks', 'reflation', 'goldilocks', 'goldilocks', 'goldilocks'];
  return regimes.map((r, i) => ({
    id: i,
    regime: r,
    confidence: 0.5 + Math.random() * 0.4,
    timestamp: new Date(Date.now() - (15 - i) * 86400000 * 30).toISOString(),
  }));
}
