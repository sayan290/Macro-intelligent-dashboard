'use client';
import React, { useEffect, useRef, useState } from 'react';
import api from '@/lib/api';

interface PricePoint {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface Props {
  symbol?: string;
  period?: string;
}

export default function PriceChart({ symbol = 'SPY', period = '3mo' }: Props) {
  const [data, setData] = useState<PricePoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const fetch = async () => {
      setIsLoading(true);
      try {
        const result = await api.getMarketPrices(symbol, period);
        setData(result?.data || getMockPriceData());
      } catch {
        setData(getMockPriceData());
      }
      setIsLoading(false);
    };
    fetch();
  }, [symbol, period]);

  useEffect(() => {
    if (!canvasRef.current || data.length === 0) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    const w = rect.width;
    const h = rect.height;
    const padding = { top: 20, right: 60, bottom: 30, left: 10 };
    const chartW = w - padding.left - padding.right;
    const chartH = h - padding.top - padding.bottom;

    const closes = data.map(d => d.close);
    const minP = Math.min(...closes) * 0.998;
    const maxP = Math.max(...closes) * 1.002;

    ctx.clearRect(0, 0, w, h);

    // Grid
    ctx.strokeStyle = '#1e293b';
    ctx.lineWidth = 0.5;
    for (let i = 0; i <= 4; i++) {
      const y = padding.top + (chartH / 4) * i;
      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(w - padding.right, y);
      ctx.stroke();

      const price = maxP - ((maxP - minP) / 4) * i;
      ctx.fillStyle = '#64748b';
      ctx.font = '10px JetBrains Mono, monospace';
      ctx.textAlign = 'left';
      ctx.fillText(`$${price.toFixed(2)}`, w - padding.right + 5, y + 3);
    }

    // Line
    const isUp = closes[closes.length - 1] >= closes[0];
    const lineColor = isUp ? '#10b981' : '#f43f5e';

    ctx.beginPath();
    ctx.strokeStyle = lineColor;
    ctx.lineWidth = 2;
    ctx.lineJoin = 'round';

    data.forEach((d, i) => {
      const x = padding.left + (chartW / (data.length - 1)) * i;
      const y = padding.top + chartH - ((d.close - minP) / (maxP - minP)) * chartH;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Gradient fill
    const lastX = padding.left + chartW;
    const gradient = ctx.createLinearGradient(0, padding.top, 0, padding.top + chartH);
    gradient.addColorStop(0, isUp ? 'rgba(16,185,129,0.15)' : 'rgba(244,63,94,0.15)');
    gradient.addColorStop(1, 'rgba(0,0,0,0)');

    ctx.lineTo(lastX, padding.top + chartH);
    ctx.lineTo(padding.left, padding.top + chartH);
    ctx.closePath();
    ctx.fillStyle = gradient;
    ctx.fill();

    // Current price marker
    const lastPrice = closes[closes.length - 1];
    const lastY = padding.top + chartH - ((lastPrice - minP) / (maxP - minP)) * chartH;
    ctx.beginPath();
    ctx.arc(lastX, lastY, 4, 0, Math.PI * 2);
    ctx.fillStyle = lineColor;
    ctx.fill();
    ctx.beginPath();
    ctx.arc(lastX, lastY, 8, 0, Math.PI * 2);
    ctx.strokeStyle = lineColor;
    ctx.lineWidth = 1;
    ctx.globalAlpha = 0.3;
    ctx.stroke();
    ctx.globalAlpha = 1;

  }, [data]);

  if (isLoading) {
    return <div className="w-full h-64 skeleton rounded-xl" />;
  }

  return (
    <div className="glass-card p-4">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h3 className="text-sm font-bold text-dark-100">{symbol}</h3>
          <p className="text-xs text-dark-400">{period} price chart</p>
        </div>
        {data.length > 0 && (
          <div className="text-right">
            <p className="text-lg font-bold font-mono text-dark-100">${data[data.length - 1]?.close.toFixed(2)}</p>
            <p className={`text-xs font-mono ${data[data.length - 1]?.close >= data[0]?.close ? 'text-accent-emerald' : 'text-accent-rose'}`}>
              {((data[data.length - 1]?.close / data[0]?.close - 1) * 100).toFixed(2)}%
            </p>
          </div>
        )}
      </div>
      <canvas ref={canvasRef} className="w-full h-56" style={{ width: '100%', height: '224px' }} />
    </div>
  );
}

function getMockPriceData(): PricePoint[] {
  const data: PricePoint[] = [];
  let price = 480;
  for (let i = 0; i < 60; i++) {
    const change = (Math.random() - 0.48) * 4;
    price += change;
    data.push({
      timestamp: new Date(Date.now() - (60 - i) * 86400000).toISOString(),
      open: price - Math.random(),
      high: price + Math.random() * 2,
      low: price - Math.random() * 2,
      close: price,
      volume: Math.floor(Math.random() * 100000000),
    });
  }
  return data;
}
