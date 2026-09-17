'use client';
import React from 'react';

interface Props {
  value?: number;
  label?: string;
}

export default function LiquidityGauge({ value = 65, label = 'Net Liquidity' }: Props) {
  const circumference = 2 * Math.PI * 50;
  const strokeDashoffset = circumference - (value / 100) * circumference;
  const color = value > 70 ? '#10b981' : value > 40 ? '#f59e0b' : '#ef4444';

  return (
    <div className="glass-card p-6 text-center">
      <h3 className="text-sm font-bold text-dark-100 mb-4">{label}</h3>
      <div className="relative w-32 h-32 mx-auto">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r="50" fill="none" stroke="#1e293b" strokeWidth="8" />
          <circle
            cx="60" cy="60" r="50" fill="none"
            stroke={color} strokeWidth="8" strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            style={{ transition: 'stroke-dashoffset 1s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-2xl font-bold font-mono" style={{ color }}>{value}%</span>
        </div>
      </div>
      <p className="text-[10px] text-dark-400 mt-2">Liquidity Score</p>
    </div>
  );
}
