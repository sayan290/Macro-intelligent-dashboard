'use client';
import React from 'react';
import MarketTicker from '@/components/widgets/MarketTicker';
import RegimeCard from '@/components/widgets/RegimeCard';
import EventCountdown from '@/components/widgets/EventCountdown';
import AlertFeed from '@/components/widgets/AlertFeed';
import MacroHeatmap from '@/components/widgets/MacroHeatmap';
import MacroSummary from '@/components/widgets/MacroSummary';
import PriceChart from '@/components/charts/PriceChart';
import RegimeTimeline from '@/components/charts/RegimeTimeline';

export default function DashboardPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Ticker */}
      <MarketTicker />

      {/* Top row: Regime + Price Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-6">
          <RegimeCard />
          <RegimeTimeline />
        </div>
        <div className="lg:col-span-2 space-y-6">
          <PriceChart symbol="SPY" period="3mo" />
          <PriceChart symbol="BTC-USD" period="3mo" />
        </div>
      </div>

      {/* Middle row: Macro */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <MacroSummary />
        <MacroHeatmap />
      </div>

      {/* Bottom row: Events + Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <EventCountdown />
        <AlertFeed />
      </div>
    </div>
  );
}