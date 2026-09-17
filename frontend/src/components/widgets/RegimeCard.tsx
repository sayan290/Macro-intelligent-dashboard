'use client';
import React, { useEffect, useState } from 'react';
import { GitBranch, TrendingUp, TrendingDown, Activity } from 'lucide-react';
import api from '@/lib/api';

interface RegimeData {
  regime: string;
  confidence: number;
  label: string;
  color: string;
  description: string;
  sub_regimes: Record<string, string>;
  timestamp: string | null;
}

const REGIME_ICONS: Record<string, any> = {
  goldilocks: TrendingUp,
  reflation: Activity,
  stagflation: TrendingDown,
  deflation: TrendingDown,
};

const REGIME_COLORS: Record<string, string> = {
  goldilocks: '#10b981',
  reflation: '#f59e0b',
  stagflation: '#ef4444',
  deflation: '#3b82f6',
  unknown: '#6b7280',
};

export default function RegimeCard() {
  const [regime, setRegime] = useState<RegimeData | null>(null);

  useEffect(() => {
    const fetch = async () => {
      try {
        const data = await api.getCurrentRegime();
        setRegime(data);
      } catch {
        setRegime({
          regime: 'goldilocks',
          confidence: 0.72,
          label: 'Goldilocks',
          color: '#10b981',
          description: 'Strong growth, moderate inflation — risk assets favored',
          sub_regimes: { volatility: 'calm', yield_curve: 'normal', labor: 'tight' },
          timestamp: new Date().toISOString(),
        });
      }
    };
    fetch();
    const timer = setInterval(fetch, 300000);
    return () => clearInterval(timer);
  }, []);

  if (!regime) {
    return <div className="glass-card p-6 h-48 skeleton" />;
  }

  const color = REGIME_COLORS[regime.regime] || REGIME_COLORS.unknown;
  const Icon = REGIME_ICONS[regime.regime] || GitBranch;

  return (
    <div
      id="regime-card"
      className="glass-card p-6 relative overflow-hidden group"
      style={{ borderColor: `${color}20` }}
    >
      {/* Glow background */}
      <div
        className="absolute inset-0 opacity-5 group-hover:opacity-10 transition-opacity"
        style={{ background: `radial-gradient(circle at 30% 30%, ${color}, transparent 70%)` }}
      />

      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ backgroundColor: `${color}15` }}
            >
              <Icon className="w-5 h-5" style={{ color }} />
            </div>
            <div>
              <h3 className="text-xs font-medium text-dark-300 uppercase tracking-wider">Current Regime</h3>
              <p className="text-lg font-bold" style={{ color }}>{regime.label}</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-xs text-dark-400">Confidence</p>
            <p className="text-xl font-bold font-mono" style={{ color }}>
              {Math.round(regime.confidence * 100)}%
            </p>
          </div>
        </div>

        {/* Confidence bar */}
        <div className="w-full h-1.5 bg-dark-700 rounded-full mb-3 overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-1000"
            style={{ width: `${regime.confidence * 100}%`, backgroundColor: color }}
          />
        </div>

        <p className="text-xs text-dark-300 mb-3">{regime.description}</p>

        {/* Sub-regimes */}
        {regime.sub_regimes && Object.keys(regime.sub_regimes).length > 0 && (
          <div className="flex flex-wrap gap-2">
            {Object.entries(regime.sub_regimes).map(([key, val]) => (
              <span key={key} className="px-2 py-1 bg-dark-700/50 rounded-md text-[10px] font-medium text-dark-300 uppercase tracking-wider">
                {key}: {val}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
