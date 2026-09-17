'use client';
import React, { useEffect, useState } from 'react';
import { Bell, ArrowUpRight, ArrowDownRight, Info, AlertTriangle } from 'lucide-react';
import { timeAgo } from '@/lib/utils';
import api from '@/lib/api';

interface AlertItem {
  id: number;
  message: string;
  triggered_at: string;
  data: any;
  alert_id: number;
}

export default function AlertFeed() {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);

  useEffect(() => {
    const fetch = async () => {
      try {
        const data = await api.getAlertTriggers();
        setAlerts(Array.isArray(data) ? data.slice(0, 8) : getMockAlerts());
      } catch {
        setAlerts(getMockAlerts());
      }
    };
    fetch();
    const timer = setInterval(fetch, 60000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div id="alert-feed" className="glass-card p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Bell className="w-5 h-5 text-accent-amber" />
          <h3 className="text-sm font-semibold text-dark-100">Alert Feed</h3>
        </div>
        <span className="text-[10px] text-dark-400 font-mono">{alerts.length} alerts</span>
      </div>

      <div className="space-y-2 max-h-72 overflow-y-auto">
        {alerts.map((alert, i) => (
          <div
            key={alert.id || i}
            className="flex items-start gap-3 p-3 bg-dark-800/30 rounded-lg border border-dark-600/20 hover:border-accent-amber/20 transition-all animate-slide-up"
            style={{ animationDelay: `${i * 50}ms` }}
          >
            <div className="mt-0.5">
              <AlertTriangle className="w-3.5 h-3.5 text-accent-amber" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs text-dark-100 leading-relaxed">{alert.message}</p>
              <p className="text-[10px] text-dark-400 mt-1">{timeAgo(alert.triggered_at)}</p>
            </div>
          </div>
        ))}
        {alerts.length === 0 && (
          <p className="text-xs text-dark-400 text-center py-8">No recent alerts</p>
        )}
      </div>
    </div>
  );
}

function getMockAlerts(): AlertItem[] {
  const now = new Date();
  return [
    { id: 1, alert_id: 1, message: 'VIX crossed above 18 — elevated volatility detected', triggered_at: new Date(now.getTime() - 300000).toISOString(), data: null },
    { id: 2, alert_id: 2, message: '10Y-2Y spread narrowing — watch for inversion signal', triggered_at: new Date(now.getTime() - 1800000).toISOString(), data: null },
    { id: 3, alert_id: 3, message: 'BTC/USD up 4.2% — momentum breakout detected', triggered_at: new Date(now.getTime() - 3600000).toISOString(), data: null },
    { id: 4, alert_id: 4, message: 'FOMC meeting in 48 hours — positioning alert', triggered_at: new Date(now.getTime() - 7200000).toISOString(), data: null },
  ];
}
