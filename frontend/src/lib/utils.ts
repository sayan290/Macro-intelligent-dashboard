import { clsx, type ClassValue } from 'clsx';

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export function formatNumber(num: number | null | undefined, decimals = 2): string {
  if (num === null || num === undefined) return '—';
  if (Math.abs(num) >= 1e12) return `${(num / 1e12).toFixed(decimals)}T`;
  if (Math.abs(num) >= 1e9) return `${(num / 1e9).toFixed(decimals)}B`;
  if (Math.abs(num) >= 1e6) return `${(num / 1e6).toFixed(decimals)}M`;
  if (Math.abs(num) >= 1e3) return `${(num / 1e3).toFixed(decimals)}K`;
  return num.toFixed(decimals);
}

export function formatPercent(num: number | null | undefined): string {
  if (num === null || num === undefined) return '—';
  const sign = num >= 0 ? '+' : '';
  return `${sign}${num.toFixed(2)}%`;
}

export function formatCurrency(num: number | null | undefined): string {
  if (num === null || num === undefined) return '—';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(num);
}

export function getChangeColor(value: number | null | undefined): string {
  if (value === null || value === undefined || value === 0) return 'text-dark-300';
  return value > 0 ? 'text-accent-emerald' : 'text-accent-rose';
}

export function getChangeBg(value: number | null | undefined): string {
  if (value === null || value === undefined || value === 0) return 'bg-dark-600';
  return value > 0 ? 'bg-emerald-500/10' : 'bg-rose-500/10';
}

export function timeAgo(dateStr: string | null): string {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}
