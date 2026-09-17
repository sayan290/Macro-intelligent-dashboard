'use client';
import React, { useEffect, useState } from 'react';
import { BarChart3 } from 'lucide-react';
import api from '@/lib/api';

export default function CorrelationPage() {
  const [matrix, setMatrix] = useState<{ symbols: string[]; matrix: Record<string, Record<string, number>> } | null>(null);

  useEffect(() => {
    const fetch = async () => {
      try {
        const data = await api.getCorrelationMatrix();
        setMatrix(data);
      } catch {
        setMatrix(getMockMatrix());
      }
    };
    fetch();
  }, []);

  const symbols = matrix?.symbols || [];
  const getCorrelation = (s1: string, s2: string): number => {
    return matrix?.matrix?.[s1]?.[s2] ?? 0;
  };

  const getCorrelationColor = (val: number): string => {
    if (val > 0.7) return 'bg-emerald-500/40';
    if (val > 0.3) return 'bg-emerald-500/20';
    if (val > -0.3) return 'bg-dark-600/50';
    if (val > -0.7) return 'bg-rose-500/20';
    return 'bg-rose-500/40';
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center gap-3">
        <BarChart3 className="w-6 h-6 text-accent-purple" />
        <h1 className="text-2xl font-bold gradient-text">Correlation Matrix</h1>
      </div>

      <div className="glass-card p-6 overflow-x-auto">
        {symbols.length > 0 ? (
          <table className="w-full">
            <thead>
              <tr>
                <th className="p-2 text-xs text-dark-400 text-left" />
                {symbols.map(s => (
                  <th key={s} className="p-2 text-xs text-dark-200 font-mono font-bold text-center">{s}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {symbols.map(s1 => (
                <tr key={s1}>
                  <td className="p-2 text-xs text-dark-200 font-mono font-bold">{s1}</td>
                  {symbols.map(s2 => {
                    const val = getCorrelation(s1, s2);
                    return (
                      <td key={s2} className="p-1 text-center">
                        <div className={`p-2 rounded-lg text-xs font-mono font-bold ${getCorrelationColor(val)} ${s1 === s2 ? 'text-dark-400' : 'text-dark-100'}`}>
                          {val.toFixed(2)}
                        </div>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="text-center py-12">
            <p className="text-dark-400">Loading correlation data...</p>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="glass-card p-4">
        <div className="flex items-center justify-center gap-6">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-emerald-500/40" />
            <span className="text-xs text-dark-300">Strong Positive</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-dark-600/50" />
            <span className="text-xs text-dark-300">Neutral</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-rose-500/40" />
            <span className="text-xs text-dark-300">Strong Negative</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function getMockMatrix() {
  const symbols = ['SPY', 'QQQ', 'TLT', 'GLD', 'BTC-USD', 'DX-Y.NYB'];
  const matrix: Record<string, Record<string, number>> = {};
  symbols.forEach(s1 => {
    matrix[s1] = {};
    symbols.forEach(s2 => {
      if (s1 === s2) matrix[s1][s2] = 1;
      else if (matrix[s2]?.[s1] !== undefined) matrix[s1][s2] = matrix[s2][s1];
      else matrix[s1][s2] = parseFloat((Math.random() * 2 - 1).toFixed(2));
    });
  });
  return { symbols, matrix };
}
