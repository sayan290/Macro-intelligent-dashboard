'use client';
import React, { useEffect, useState } from 'react';
import { formatPercent, getChangeColor } from '@/lib/utils';
import api from '@/lib/api';

interface TickerItem {
  symbol: string;
  price: number;
  change_pct: number;
}

export default function MarketTicker() {
  const [items, setItems] = useState<TickerItem[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await api.getMarketOverview();
        const all: TickerItem[] = [];
        for (const cls of Object.values(data || {})) {
          if (Array.isArray(cls)) {
            all.push(...(cls as TickerItem[]));
          }
        }
        setItems(all.length > 0 ? all : getMockData());
      } catch {
        setItems(getMockData());
      }
    };
    fetchData();
    const timer = setInterval(fetchData, 30000);
    return () => clearInterval(timer);
  }, []);

  const displayItems = [...items, ...items]; // Duplicate for seamless scroll

  return (
    <div className="w-full overflow-hidden bg-dark-900/60 backdrop-blur border-b border-dark-600/30">
      <div className="ticker-scroll flex gap-8 py-2 px-4 whitespace-nowrap">
        {displayItems.map((item, i) => (
          <div key={`${item.symbol}-${i}`} className="flex items-center gap-2 text-xs">
            <span className="font-semibold text-dark-100">{item.symbol}</span>
            <span className="font-mono text-dark-200">${item.price?.toLocaleString()}</span>
            <span className={`font-mono font-medium ${getChangeColor(item.change_pct)}`}>
              {formatPercent(item.change_pct)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function getMockData(): TickerItem[] {
  return [
    { symbol: 'SPY', price: 525.30, change_pct: 0.45 },
    { symbol: 'QQQ', price: 445.10, change_pct: 0.72 },
    { symbol: 'TLT', price: 92.50, change_pct: -0.18 },
    { symbol: 'GLD', price: 195.80, change_pct: 0.25 },
    { symbol: 'BTC', price: 67500, change_pct: 1.30 },
    { symbol: 'ETH', price: 3450, change_pct: 2.15 },
    { symbol: 'DXY', price: 104.25, change_pct: -0.12 },
    { symbol: 'USO', price: 78.40, change_pct: 0.65 },
    { symbol: 'VIX', price: 13.50, change_pct: -3.20 },
  ];
}
