'use client';
import useSWR from 'swr';
import api from '@/lib/api';

const fetcher = (key: string) => api.get(key);

export function useMarketOverview() {
  const { data, error, isLoading, mutate } = useSWR('/market/overview', fetcher, {
    refreshInterval: 30000,
    revalidateOnFocus: false,
  });
  return { data, error, isLoading, refresh: mutate };
}

export function useMarketPrices(symbol: string, period = '1mo') {
  const { data, error, isLoading } = useSWR(
    symbol ? `/market/prices/${symbol}?period=${period}` : null,
    fetcher,
    { revalidateOnFocus: false }
  );
  return { data, error, isLoading };
}

export function useCryptoOverview() {
  const { data, error, isLoading } = useSWR('/market/crypto', fetcher, {
    refreshInterval: 60000,
  });
  return { data, error, isLoading };
}

export function useMarketHeatmap() {
  const { data, error, isLoading } = useSWR('/market/heatmap', fetcher, {
    refreshInterval: 60000,
  });
  return { data, error, isLoading };
}
