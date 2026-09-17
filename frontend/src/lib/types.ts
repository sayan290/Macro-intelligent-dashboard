export interface MarketQuote {
  symbol: string;
  price: number;
  change: number;
  change_pct: number;
  volume: number;
  high: number;
  low: number;
  open: number;
  timestamp: string;
}

export interface MacroIndicator {
  series_id: string;
  name: string;
  value: number | null;
  date: string | null;
  change: number | null;
  change_pct: number | null;
  units: string;
}

export interface RegimeState {
  regime: string;
  confidence: number;
  label: string;
  color: string;
  description: string;
  sub_regimes: Record<string, string>;
  indicators: Record<string, number | null>;
  timestamp: string | null;
}

export interface CalendarEvent {
  id: number;
  event_name: string;
  country: string;
  datetime_utc: string;
  impact: 'high' | 'medium' | 'low';
  actual: string | null;
  forecast: string | null;
  previous: string | null;
}

export interface AlertConfig {
  id: number;
  name: string;
  alert_type: string;
  condition: Record<string, any>;
  is_active: boolean;
  channels: string[];
  cooldown_minutes: number;
  last_triggered: string | null;
}

export interface BacktestResult {
  strategy: string;
  metrics: {
    total_return: number;
    annual_return: number;
    volatility: number;
    sharpe_ratio: number;
    max_drawdown: number;
    total_trades: number;
  };
  benchmark: { equal_weight_return: number };
  portfolio_curve: number[];
  trades: any[];
}
