'use client';
import React, { useEffect, useState } from 'react';
import { Calendar, Clock, AlertTriangle } from 'lucide-react';
import api from '@/lib/api';

interface CalendarEvent {
  event_name: string;
  country: string;
  datetime_utc: string;
  impact: string;
  forecast: string | null;
  previous: string | null;
}

export default function EventCountdown() {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [countdowns, setCountdowns] = useState<Record<number, string>>({});

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const data = await api.getUpcomingEvents(7);
        setEvents(Array.isArray(data) ? data.slice(0, 5) : getMockEvents());
      } catch {
        setEvents(getMockEvents());
      }
    };
    fetchEvents();
  }, []);

  useEffect(() => {
    const tick = () => {
      const now = new Date().getTime();
      const newCountdowns: Record<number, string> = {};
      events.forEach((e, i) => {
        const eventTime = new Date(e.datetime_utc).getTime();
        const diff = eventTime - now;
        if (diff > 0) {
          const d = Math.floor(diff / 86400000);
          const h = Math.floor((diff % 86400000) / 3600000);
          const m = Math.floor((diff % 3600000) / 60000);
          newCountdowns[i] = d > 0 ? `${d}d ${h}h` : `${h}h ${m}m`;
        } else {
          newCountdowns[i] = 'Now';
        }
      });
      setCountdowns(newCountdowns);
    };
    tick();
    const timer = setInterval(tick, 60000);
    return () => clearInterval(timer);
  }, [events]);

  const impactColors: Record<string, string> = {
    high: 'bg-rose-500/20 text-rose-400 border-rose-500/30',
    medium: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    low: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  };

  return (
    <div id="event-countdown" className="glass-card p-6">
      <div className="flex items-center gap-2 mb-4">
        <Calendar className="w-5 h-5 text-accent-purple" />
        <h3 className="text-sm font-semibold text-dark-100">Upcoming Events</h3>
      </div>

      <div className="space-y-3">
        {events.map((event, i) => (
          <div key={i} className="flex items-center justify-between p-3 bg-dark-800/40 rounded-xl border border-dark-600/20 hover:border-dark-500/30 transition-all group">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold uppercase border ${impactColors[event.impact] || impactColors.low}`}>
                  {event.impact}
                </span>
                <span className="text-[10px] text-dark-400 font-mono">{event.country}</span>
              </div>
              <p className="text-xs font-medium text-dark-100 truncate">{event.event_name}</p>
              {event.forecast && (
                <p className="text-[10px] text-dark-400 mt-0.5">
                  F: {event.forecast} | P: {event.previous || '—'}
                </p>
              )}
            </div>
            <div className="text-right flex-shrink-0 ml-3">
              <div className="flex items-center gap-1 text-accent-cyan">
                <Clock className="w-3 h-3" />
                <span className="text-xs font-mono font-bold">{countdowns[i] || '...'}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function getMockEvents(): CalendarEvent[] {
  const now = new Date();
  return [
    { event_name: 'FOMC Rate Decision', country: 'US', datetime_utc: new Date(now.getTime() + 86400000 * 2).toISOString(), impact: 'high', forecast: '5.25%', previous: '5.25%' },
    { event_name: 'Nonfarm Payrolls', country: 'US', datetime_utc: new Date(now.getTime() + 86400000 * 4).toISOString(), impact: 'high', forecast: '180K', previous: '216K' },
    { event_name: 'CPI m/m', country: 'US', datetime_utc: new Date(now.getTime() + 86400000 * 6).toISOString(), impact: 'high', forecast: '0.3%', previous: '0.4%' },
    { event_name: 'ECB Rate Decision', country: 'EU', datetime_utc: new Date(now.getTime() + 86400000 * 8).toISOString(), impact: 'high', forecast: '4.50%', previous: '4.50%' },
    { event_name: 'PMI Manufacturing', country: 'US', datetime_utc: new Date(now.getTime() + 86400000 * 3).toISOString(), impact: 'medium', forecast: '49.5', previous: '49.0' },
  ];
}
