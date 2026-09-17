'use client';
import React, { useEffect, useState } from 'react';
import { Bell, Plus, Trash2, Power, PowerOff } from 'lucide-react';
import { timeAgo } from '@/lib/utils';
import api from '@/lib/api';

interface AlertConfig {
  id: number;
  name: string;
  alert_type: string;
  condition: any;
  is_active: boolean;
  channels: string[];
  last_triggered: string | null;
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<AlertConfig[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: '', alert_type: 'price_cross', condition: { symbol: 'SPY', threshold: 500, direction: 'above' } });

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      const data = await api.getAlerts();
      setAlerts(Array.isArray(data) ? data : getMockAlerts());
    } catch {
      setAlerts(getMockAlerts());
    }
  };

  const createAlert = async () => {
    if (!form.name) return;
    try {
      await api.createAlert({ ...form, channels: ['telegram'] });
      fetchAlerts();
      setShowCreate(false);
      setForm({ name: '', alert_type: 'price_cross', condition: { symbol: 'SPY', threshold: 500, direction: 'above' } });
    } catch {}
  };

  const deleteAlert = async (id: number) => {
    try {
      await api.deleteAlert(id);
      fetchAlerts();
    } catch {}
  };

  const typeIcons: Record<string, string> = {
    price_cross: '📊',
    regime_change: '🔄',
    indicator_threshold: '📈',
    event_upcoming: '📅',
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Bell className="w-6 h-6 text-accent-amber" />
          <h1 className="text-2xl font-bold gradient-text">Alert Management</h1>
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-accent-cyan to-accent-purple rounded-xl text-white text-sm font-medium hover:opacity-90 transition-all"
        >
          <Plus className="w-4 h-4" />
          New Alert
        </button>
      </div>

      {/* Create form */}
      {showCreate && (
        <div className="glass-card p-6 animate-slide-up">
          <h3 className="text-sm font-bold text-dark-100 mb-4">Create Alert</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              placeholder="Alert name"
              value={form.name}
              onChange={e => setForm({ ...form, name: e.target.value })}
              className="px-4 py-2.5 bg-dark-800/50 border border-dark-600/30 rounded-xl text-sm text-dark-100 focus:outline-none focus:border-accent-cyan/50"
            />
            <select
              value={form.alert_type}
              onChange={e => setForm({ ...form, alert_type: e.target.value })}
              className="px-4 py-2.5 bg-dark-800/50 border border-dark-600/30 rounded-xl text-sm text-dark-100 focus:outline-none focus:border-accent-cyan/50"
            >
              <option value="price_cross">Price Cross</option>
              <option value="regime_change">Regime Change</option>
              <option value="indicator_threshold">Indicator Threshold</option>
              <option value="event_upcoming">Event Upcoming</option>
            </select>
          </div>
          <button
            onClick={createAlert}
            className="mt-4 px-6 py-2 bg-accent-cyan/20 text-accent-cyan border border-accent-cyan/30 rounded-xl text-sm font-medium hover:bg-accent-cyan/30 transition-all"
          >
            Create Alert
          </button>
        </div>
      )}

      {/* Alert list */}
      <div className="space-y-3">
        {alerts.map(alert => (
          <div key={alert.id} className="glass-card p-4 flex items-center justify-between group">
            <div className="flex items-center gap-4">
              <span className="text-xl">{typeIcons[alert.alert_type] || '🔔'}</span>
              <div>
                <p className="text-sm font-medium text-dark-100">{alert.name}</p>
                <p className="text-[10px] text-dark-400">
                  {alert.alert_type.replace('_', ' ')} • {alert.channels?.join(', ')}
                  {alert.last_triggered && ` • Last: ${timeAgo(alert.last_triggered)}`}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className={`flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-medium ${alert.is_active ? 'bg-emerald-500/10 text-emerald-400' : 'bg-dark-600/50 text-dark-400'}`}>
                {alert.is_active ? <Power className="w-3 h-3" /> : <PowerOff className="w-3 h-3" />}
                {alert.is_active ? 'Active' : 'Paused'}
              </span>
              <button
                onClick={() => deleteAlert(alert.id)}
                className="p-2 text-dark-400 hover:text-accent-rose transition-all opacity-0 group-hover:opacity-100"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
        {alerts.length === 0 && (
          <div className="glass-card p-12 text-center">
            <Bell className="w-8 h-8 text-dark-400 mx-auto mb-3" />
            <p className="text-dark-400">No alerts configured</p>
          </div>
        )}
      </div>
    </div>
  );
}

function getMockAlerts(): AlertConfig[] {
  return [
    { id: 1, name: 'SPY Above 530', alert_type: 'price_cross', condition: { symbol: 'SPY', threshold: 530, direction: 'above' }, is_active: true, channels: ['telegram'], last_triggered: null },
    { id: 2, name: 'VIX Spike Alert', alert_type: 'indicator_threshold', condition: { series_id: 'VIXCLS', threshold: 20, direction: 'above' }, is_active: true, channels: ['telegram', 'email'], last_triggered: new Date(Date.now() - 86400000).toISOString() },
    { id: 3, name: 'Regime Change', alert_type: 'regime_change', condition: { target_regime: 'stagflation' }, is_active: false, channels: ['telegram'], last_triggered: null },
  ];
}
