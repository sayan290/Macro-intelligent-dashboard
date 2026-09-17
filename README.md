# 🧠 Macro Intelligence Dashboard

Advanced macroeconomic research & market intelligence platform for institutional-grade analysis.

![Tech Stack](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-000?style=flat&logo=next.js&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)

## ✨ Features

- **Real-time Market Data**: Live prices for equities, crypto, bonds, commodities, FX
- **Macro Dashboard**: 20+ economic indicators from FRED (GDP, CPI, Unemployment, Fed Funds)
- **Regime Detection**: ML-based macro regime classification (Goldilocks/Reflation/Stagflation/Deflation)
- **Correlation Matrix**: Cross-asset correlation analysis with rolling windows
- **Economic Calendar**: Upcoming high-impact events with countdown timers
- **AI Research Assistant**: RAG-powered analysis using local LLM (Ollama)
- **Alert System**: Configurable alerts via Telegram, Discord, Email
- **Strategy Backtester**: Regime rotation, momentum, and mean reversion strategies
- **WebSocket Streaming**: Real-time data updates

## 🏗 Architecture

```
macro-intel-dashboard/
├── backend/           # FastAPI + SQLAlchemy (async)
│   ├── app/
│   │   ├── api/       # REST endpoints
│   │   ├── models/    # SQLAlchemy ORM
│   │   ├── ingestion/ # Yahoo, FRED, CoinGecko, Binance, ECB, World Bank
│   │   ├── analysis/  # Regime detection, correlation, volatility
│   │   ├── ai/        # Ollama LLM + ChromaDB RAG
│   │   ├── alerts/    # Telegram, Discord, Email
│   │   ├── backtest/  # Strategy backtesting engine
│   │   └── workers/   # APScheduler background tasks
│   └── alembic/       # Database migrations
├── frontend/          # Next.js 14 + TypeScript + TailwindCSS
│   └── src/
│       ├── app/       # Pages (dashboard, markets, macro, regime, etc.)
│       ├── components/# Widgets, charts, layout
│       ├── hooks/     # React hooks (useMarketData, useRegime, useWebSocket)
│       ├── lib/       # API client, utilities
│       └── store/     # Zustand state management
├── docker-compose.yml # Full infrastructure
└── Makefile           # Dev shortcuts
```

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone <repo> && cd macro-intel-dashboard
make setup

# 2. Start everything
make start

# 3. Open dashboard
open http://localhost:3000
```

### Services
| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | Next.js Dashboard |
| Backend | 8080 | FastAPI REST API |
| PostgreSQL | 5432 | TimescaleDB |
| Redis | 6379 | Cache & Pub/Sub |
| ChromaDB | 8000 | Vector Store |
| Ollama | 11434 | Local LLM |

## 📊 Data Sources

| Source | Data | API Key |
|--------|------|---------|
| Yahoo Finance | Prices, OHLCV | Free |
| FRED | US Macro Indicators | Free (register) |
| CoinGecko | Crypto Prices | Free |
| Binance | Crypto Depth, Funding | Free |
| ECB | EUR Exchange Rates | Free |
| World Bank | Global Indicators | Free |

## ⚙️ Configuration

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Key configuration:
- `FRED_API_KEY` - Get from https://fred.stlouisfed.org/docs/api/api_key.html
- `TELEGRAM_BOT_TOKEN` - For alert notifications
- `DISCORD_WEBHOOK_URL` - For alert notifications

## 📖 API Docs

Once running, visit `http://localhost:8080/docs` for interactive Swagger documentation.

## License

MIT
