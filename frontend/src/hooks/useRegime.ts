'use client';
import useSWR from 'swr';
import api from '@/lib/api';

const fetcher = (key: string) => api.get(key);

export function useCurrentRegime() {
  const { data, error, isLoading } = useSWR('/regime/current', fetcher, {
    refreshInterval: 300000,
    revalidateOnFocus: false,
  });
  return { data, error, isLoading };
}

export function useRegimeHistory(limit = 50) {
  const { data, error, isLoading } = useSWR(`/regime/history?limit=${limit}`, fetcher, {
    revalidateOnFocus: false,
  });
  return { data, error, isLoading };
}
