'use client';
import React from 'react';

const YIELD_DATA = [
  { maturity: '1M', yield: 5.50 }, { maturity: '3M', yield: 5.48 },
  { maturity: '6M', yield: 5.40 }, { maturity: '1Y', yield: 5.15 },
  { maturity: '2Y', yield: 4.70 }, { maturity: '3Y', yield: 4.45 },
  { maturity: '5Y', yield: 4.30 }, { maturity: '7Y', yield: 4.35 },
  { maturity: '10Y', yield: 4.25 }, { maturity: '20Y', yield: 4.55 },
  { maturity: '30Y', yield: 4.50 },
];

export default function YieldCurve() {
  const min = Math.min(...YIELD_DATA.map(d => d.yield)) - 0.2;
  const max = Math.max(...YIELD_DATA.map(d => d.yield)) + 0.2;
  const range = max - min;

  return (
    <div className="glass-card p-6">
      <h3 className="text-sm font-bold text-dark-100 mb-4">US Treasury Yield Curve</h3>
      <div className="relative h-40">
        <svg className="w-full h-full" viewBox="0 0 400 160" preserveAspectRatio="none">
          <defs>
            <linearGradient id="yc-grad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="rgba(168,85,247,0.2)" />
              <stop offset="100%" stopColor="rgba(168,85,247,0)" />
            </linearGradient>
          </defs>
          {/* Line */}
          <polyline
            fill="none"
            stroke="#a855f7"
            strokeWidth="2"
            points={YIELD_DATA.map((d, i) => `${(i / (YIELD_DATA.length - 1)) * 380 + 10},${160 - ((d.yield - min) / range) * 140 - 10}`).join(' ')}
          />
          {/* Fill */}
          <polygon
            fill="url(#yc-grad)"
            points={`10,150 ${YIELD_DATA.map((d, i) => `${(i / (YIELD_DATA.length - 1)) * 380 + 10},${160 - ((d.yield - min) / range) * 140 - 10}`).join(' ')} 390,150`}
          />
          {/* Dots */}
          {YIELD_DATA.map((d, i) => (
            <circle
              key={i}
              cx={(i / (YIELD_DATA.length - 1)) * 380 + 10}
              cy={160 - ((d.yield - min) / range) * 140 - 10}
              r="3"
              fill="#a855f7"
            />
          ))}
        </svg>
      </div>
      <div className="flex justify-between mt-2">
        {YIELD_DATA.filter((_, i) => i % 2 === 0).map(d => (
          <div key={d.maturity} className="text-center">
            <p className="text-[10px] text-dark-400">{d.maturity}</p>
            <p className="text-[10px] font-mono text-dark-200">{d.yield}%</p>
          </div>
        ))}
      </div>
    </div>
  );
}
