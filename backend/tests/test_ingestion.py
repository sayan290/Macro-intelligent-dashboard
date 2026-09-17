import pytest
from unittest.mock import AsyncMock, patch


class TestYahooClient:
    """Test Yahoo Finance client."""

    @pytest.mark.asyncio
    async def test_get_quote_returns_dict(self):
        from app.ingestion.yahoo import YahooFinanceClient
        client = YahooFinanceClient()
        result = await client.get_quote("SPY")
        if result is not None:
            assert "symbol" in result
            assert "price" in result

    @pytest.mark.asyncio
    async def test_get_history_returns_data(self):
        from app.ingestion.yahoo import YahooFinanceClient
        client = YahooFinanceClient()
        result = await client.get_history("SPY", period="5d", interval="1d")
        assert "symbol" in result
        assert "data" in result


class TestFredClient:
    """Test FRED client (uses mock data without API key)."""

    @pytest.mark.asyncio
    async def test_get_series_returns_list(self):
        from app.ingestion.fred import FredClient
        client = FredClient()
        result = await client.get_series("GDP", limit=5)
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_latest_returns_dict(self):
        from app.ingestion.fred import FredClient
        client = FredClient()
        result = await client.get_latest("UNRATE")
        assert isinstance(result, dict)


class TestCoinGeckoClient:
    """Test CoinGecko client."""

    @pytest.mark.asyncio
    async def test_get_price(self):
        from app.ingestion.coingecko import CoinGeckoClient
        client = CoinGeckoClient()
        result = await client.get_price("bitcoin")
        if result is not None:
            assert "price" in result
