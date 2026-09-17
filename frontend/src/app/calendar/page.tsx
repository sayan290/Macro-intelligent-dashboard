'use client';
import React, { useEffect, useState } from 'react';
import { Calendar, Clock, Filter } from 'lucide-react';
import api from '@/lib/api';

interface CalendarEvent {
  id: number;
  event_name: string;
  country: string;
  datetime_utc: string;
  impact: string;
  actual: string | null;
  forecast: string | null;
  previous: string | null;
}

export default function CalendarPage() {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    const fetch = async () => {
      try {
        const data = await api.getUpcomingEvents(14);
        setEvents(Array.isArray(data) ? data : getMockEvents());
      } catch {
        setEvents(getMockEvents());
      }
    };
    fetch();
  }, []);

  const filtered = filter === 'all' ? events : events.filter(e => e.impact === filter);

  const impactStyle: Record<string, string> = {
    high: 'bg-rose-500/20 text-rose-400 border-rose-500/30',
    medium: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    low: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Calendar className="w-6 h-6 text-accent-purple" />
          <h1 className="text-2xl font-bold gradient-text">Economic Calendar</h1>
        </div>
        <div className="flex gap-2">
          {['all', 'high', 'medium', 'low'].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all capitalize ${
                filter === f ? 'bg-accent-cyan/20 text-accent-cyan border border-accent-cyan/30' : 'bg-dark-800/50 text-dark-300 border border-dark-600/30 hover:border-dark-500'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      <div className="glass-card overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-dark-600/30">
              <th className="px-4 py-3 text-left text-[10px] text-dark-400 uppercase tracking-wider font-bold">Time</th>
              <th className="px-4 py-3 text-left text-[10px] text-dark-400 uppercase tracking-wider font-bold">Country</th>
              <th className="px-4 py-3 text-left text-[10px] text-dark-400 uppercase tracking-wider font-bold">Event</th>
              <th className="px-4 py-3 text-center text-[10px] text-dark-400 uppercase tracking-wider font-bold">Impact</th>
              <th className="px-4 py-3 text-right text-[10px] text-dark-400 uppercase tracking-wider font-bold">Forecast</th>
              <th className="px-4 py-3 text-right text-[10px] text-dark-400 uppercase tracking-wider font-bold">Previous</th>
              <th className="px-4 py-3 text-right text-[10px] text-dark-400 uppercase tracking-wider font-bold">Actual</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((e, i) => (
              <tr key={e.id || i} className="border-b border-dark-600/10 hover:bg-dark-800/30 transition-all">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1.5">
                    <Clock className="w-3 h-3 text-dark-400" />
                    <span className="text-xs font-mono text-dark-200">
                      {new Date(e.datetime_utc).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-dark-400">
                    {new Date(e.datetime_utc).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className="text-xs font-bold text-dark-200">{e.country}</span>
                </td>
                <td className="px-4 py-3">
                  <span className="text-xs font-medium text-dark-100">{e.event_name}</span>
                </td>
                <td className="px-4 py-3 text-center">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${impactStyle[e.impact] || impactStyle.low}`}>
                    {e.impact}
                  </span>
                </td>
                <td className="px-4 py-3 text-right text-xs font-mono text-dark-200">{e.forecast || '—'}</td>
                <td className="px-4 py-3 text-right text-xs font-mono text-dark-300">{e.previous || '—'}</td>
                <td className="px-4 py-3 text-right text-xs font-mono font-bold text-dark-100">{e.actual || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <div className="text-center py-8 text-dark-400 text-xs">No events found</div>
        )}
      </div>
    </div>
  );
}

function getMockEvents(): CalendarEvent[] {
  const now = new Date();
  return [
    { id: 1, event_name: 'FOMC Rate Decision', country: 'US', datetime_utc: new Date(now.getTime() + 86400000 * 2).toISOString(), impact: 'high', actual: null, forecast: '5.25%', previous: '5.25%' },
    { id: 2, event_name: 'Nonfarm Payrolls', country: 'US', datetime_utc: new Date(now.getTime() + 86400000 * 4).toISOString(), impact: 'high', actual: null, forecast: '180K', previous: '216K' },
    { id: 3, event_name: 'CPI m/m', country: 'US', datetime_utc: new Date(now.getTime() + 86400000 * 6).toISOString(), impact: 'high', actual: null, forecast: '0.3%', previous: '0.4%' },
    { id: 4, event_name: 'PMI Manufacturing', country: 'US', datetime_utc: new Date(now.getTime() + 86400000 * 3).toISOString(), impact: 'medium', actual: null, forecast: '49.5', previous: '49.0' },
    { id: 5, event_name: 'Retail Sales m/m', country: 'US', datetime_utc: new Date(now.getTime() + 86400000 * 5).toISOString(), impact: 'medium', actual: null, forecast: '0.4%', previous: '0.6%' },
    { id: 6, event_name: 'ECB Rate Decision', country: 'EU', datetime_utc: new Date(now.getTime() + 86400000 * 8).toISOString(), impact: 'high', actual: null, forecast: '4.50%', previous: '4.50%' },
    { id: 7, event_name: 'BoE Rate Decision', country: 'GB', datetime_utc: new Date(now.getTime() + 86400000 * 10).toISOString(), impact: 'high', actual: null, forecast: '5.25%', previous: '5.25%' },
    { id: 8, event_name: 'Unemployment Claims', country: 'US', datetime_utc: new Date(now.getTime() + 86400000).toISOString(), impact: 'low', actual: null, forecast: '210K', previous: '215K' },
  ];
}
