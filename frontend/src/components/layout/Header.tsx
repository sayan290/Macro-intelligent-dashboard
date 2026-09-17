'use client';
import React, { useState, useEffect } from 'react';
import { Search, Bell, Wifi, WifiOff } from 'lucide-react';

export default function Header() {
  const [time, setTime] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [isConnected, setIsConnected] = useState(true);

  useEffect(() => {
    const tick = () => {
      const now = new Date();
      setTime(now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }));
    };
    tick();
    const timer = setInterval(tick, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="h-16 bg-dark-900/80 backdrop-blur-xl border-b border-dark-600/50 flex items-center justify-between px-6 sticky top-0 z-20">
      {/* Search */}
      <div className="relative w-96">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-400" />
        <input
          id="global-search"
          type="text"
          placeholder="Search symbols, indicators, events..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-2 bg-dark-800/50 border border-dark-600/50 rounded-xl text-sm text-dark-100 placeholder-dark-400 focus:outline-none focus:border-accent-cyan/50 focus:ring-1 focus:ring-accent-cyan/20 transition-all"
        />
      </div>

      {/* Right side */}
      <div className="flex items-center gap-4">
        {/* Connection status */}
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium ${isConnected ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
          {isConnected ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
          {isConnected ? 'Live' : 'Offline'}
        </div>

        {/* Clock */}
        <div className="text-sm font-mono text-dark-300 bg-dark-800/50 px-3 py-1.5 rounded-lg">
          {time} UTC
        </div>

        {/* Notifications */}
        <button
          id="notifications-btn"
          className="relative p-2 rounded-xl bg-dark-800/50 border border-dark-600/30 text-dark-300 hover:text-white hover:border-accent-cyan/30 transition-all"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute -top-1 -right-1 w-4 h-4 bg-accent-rose rounded-full text-[10px] font-bold flex items-center justify-center text-white">3</span>
        </button>
      </div>
    </header>
  );
}
