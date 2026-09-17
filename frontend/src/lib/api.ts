const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${API_BASE}/api`;
  }

  private async request<T>(path: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...options?.headers },
      ...options,
    });
    if (!res.ok) {
      throw new Error(`API error: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }

  async get<T = any>(path: string): Promise<T> {
    return this.request<T>(path);
  }

  async post<T = any>(path: string, body?: any): Promise<T> {
    return this.request<T>(path, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async put<T = any>(path: string, body?: any): Promise<T> {
    return this.request<T>(path, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async delete<T = any>(path: string): Promise<T> {
    return this.request<T>(path, { method: 'DELETE' });
  }

  // Market
  async getMarketOverview() { return this.get('/market/overview'); }
  async getMarketPrices(symbol: string, period = '1mo', interval = '1d') {
    return this.get(`/market/prices/${symbol}?period=${period}&interval=${interval}`);
  }
  async getMarketHeatmap() { return this.get('/market/heatmap'); }
  async getCryptoOverview() { return this.get('/market/crypto'); }

  // Macro
  async getMacroDashboard() { return this.get('/macro/dashboard'); }
  async getMacroSeries(seriesId: string, limit = 500) {
    return this.get(`/macro/series/${seriesId}?limit=${limit}`);
  }
  async getMacroIndicators() { return this.get('/macro/indicators'); }
  async getMacroHeatmap() { return this.get('/macro/heatmap'); }

  // Regime
  async getCurrentRegime() { return this.get('/regime/current'); }
  async getRegimeHistory(limit = 50) { return this.get(`/regime/history?limit=${limit}`); }
  async getRegimeTransitions() { return this.get('/regime/transitions'); }

  // Correlation
  async getCorrelationMatrix(symbols?: string, period = '3mo') {
    const s = symbols || 'SPY,QQQ,TLT,GLD,BTC-USD,DX-Y.NYB';
    return this.get(`/correlation/matrix?symbols=${s}&period=${period}`);
  }
  async getRollingCorrelation(s1: string, s2: string, window = 30) {
    return this.get(`/correlation/rolling?symbol1=${s1}&symbol2=${s2}&window=${window}`);
  }

  // Calendar
  async getUpcomingEvents(days = 7) { return this.get(`/calendar/upcoming?days=${days}`); }
  async getTodayEvents() { return this.get('/calendar/today'); }

  // Alerts
  async getAlerts() { return this.get('/alerts/'); }
  async createAlert(alert: any) { return this.post('/alerts/', alert); }
  async deleteAlert(id: number) { return this.delete(`/alerts/${id}`); }
  async getAlertTriggers() { return this.get('/alerts/triggers'); }

  // AI
  async aiChat(message: string, useRag = false) {
    return this.post('/ai/chat', { message, use_rag: useRag, stream: false });
  }
  async aiAnalyze(topic: string) { return this.post(`/ai/analyze?topic=${topic}`); }

  // Backtest
  async runBacktest(config: any) { return this.post('/backtest/run', config); }
  async getStrategies() { return this.get('/backtest/strategies'); }

  // Health
  async healthCheck() { return this.get('/health'); }
}

export const api = new ApiClient();
export default api;