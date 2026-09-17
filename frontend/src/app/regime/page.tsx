'use client';
import React from 'react';
import { GitBranch } from 'lucide-react';
import RegimeCard from '@/components/widgets/RegimeCard';
import RegimeTimeline from '@/components/charts/RegimeTimeline';

export default function RegimePage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center gap-3">
        <GitBranch className="w-6 h-6 text-accent-emerald" />
        <h1 className="text-2xl font-bold gradient-text">Regime Analysis</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RegimeCard />
        <div className="glass-card p-6">
          <h3 className="text-sm font-bold text-dark-100 mb-4">Regime Framework</h3>
          <div className="space-y-3">
            {[
              { name: 'Goldilocks', color: '#10b981', desc: 'Strong growth, low inflation', assets: 'Equities, Growth' },
              { name: 'Reflation', color: '#f59e0b', desc: 'Rising growth & inflation', assets: 'Commodities, Cyclicals' },
              { name: 'Stagflation', color: '#ef4444', desc: 'Weak growth, high inflation', assets: 'Cash, Gold' },
              { name: 'Deflation', color: '#3b82f6', desc: 'Falling growth & inflation', assets: 'Bonds, Defensives' },
            ].map(r => (
              <div key={r.name} className="flex items-center gap-3 p-3 bg-dark-800/30 rounded-xl">
                <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: r.color }} />
                <div className="flex-1">
                  <p className="text-xs font-bold" style={{ color: r.color }}>{r.name}</p>
                  <p className="text-[10px] text-dark-400">{r.desc}</p>
                </div>
                <span className="text-[10px] text-dark-300 bg-dark-700/50 px-2 py-1 rounded">{r.assets}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <RegimeTimeline />
    </div>
  );
}
