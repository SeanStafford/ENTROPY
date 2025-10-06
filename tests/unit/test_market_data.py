"""Unit tests for market data tools.

Tests market data fetching, analytics, and technical indicators with mocked yfinance.
Demonstrates production hygiene: no network calls, proper error handling.
"""

import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
from datetime import datetime

from entropy.contexts.market_data.tools import (
    get_current_price,
    get_stock_fundamentals,
    get_price_history,
    calculate_price_change,
)
from entropy.contexts.market_data.analytics import compare_performance, calculate_returns
from entropy.contexts.market_data.signals import calculate_sma, calculate_rsi
from tests.fixtures.mock_data import get_mock_ticker_info, get_mock_price_history


@pytest.mark.unit
@pytest.mark.market_data
class TestGetCurrentPrice:
    """Test get_current_price with mocked yfinance."""

    @patch("yfinance.Ticker")
    def test_success(self, mock_ticker_class):
        """Successfully fetch current price."""
        # Setup mock
        mock_ticker = MagicMock()
        mock_ticker.info = get_mock_ticker_info("AAPL")
        mock_ticker_class.return_value = mock_ticker

        # Call function
        result = get_current_price("AAPL")

        # Verify result
        assert result is not None
        assert result.ticker == "AAPL"
        assert result.current_price == 150.25
        assert result.previous_close == 148.50
        assert result.volume == 50000000

    @patch("yfinance.Ticker")
    def test_invalid_ticker(self, mock_ticker_class):
        """Invalid ticker returns None."""
        # Setup mock with empty info
        mock_ticker = MagicMock()
        mock_ticker.info = {}
        mock_ticker_class.return_value = mock_ticker

        # Call function
        result = get_current_price("INVALID")

        # Should return None
        assert result is None

    @patch("yfinance.Ticker")
    def test_network_error(self, mock_ticker_class):
        """Network error is caught and returns None."""
        # Setup mock to raise exception
        mock_ticker_class.side_effect = Exception("Network error")

        # Call function
        result = get_current_price("AAPL")

        # Should handle error gracefully
        assert result is None


@pytest.mark.unit
@pytest.mark.market_data
class TestGetStockFundamentals:
    """Test get_stock_fundamentals with mocked yfinance."""

    @patch("yfinance.Ticker")
    def test_success(self, mock_ticker_class):
        """Successfully fetch fundamentals."""
        # Setup mock
        mock_ticker = MagicMock()
        mock_ticker.info = get_mock_ticker_info("AAPL")
        mock_ticker_class.return_value = mock_ticker

        # Call function
        result = get_stock_fundamentals("AAPL")

        # Verify result
        assert result is not None
        assert result.ticker == "AAPL"
        assert result.market_cap == 2400000000000
        assert result.sector == "Technology"
        assert result.company_name == "Apple Inc."

    @patch("yfinance.Ticker")
    def test_invalid_ticker(self, mock_ticker_class):
        """Invalid ticker returns None."""
        mock_ticker = MagicMock()
        mock_ticker.info = None
        mock_ticker_class.return_value = mock_ticker

        result = get_stock_fundamentals("INVALID")
        assert result is None


@pytest.mark.unit
@pytest.mark.market_data
class TestPriceChange:
    """Test calculate_price_change."""

    @patch("yfinance.Ticker")
    def test_price_change_calculation(self, mock_ticker_class):
        """Calculate price change correctly."""
        # Setup mock
        mock_ticker = MagicMock()
        mock_ticker.info = get_mock_ticker_info("AAPL")

        # Mock history with simple data
        history_data = get_mock_price_history("AAPL", period="1mo")
        history_df = pd.DataFrame(history_data)
        history_df.set_index("Date", inplace=True)
        mock_ticker.history.return_value = history_df

        mock_ticker_class.return_value = mock_ticker

        # Call function
        result = calculate_price_change("AAPL", period="1mo")

        # Verify calculation
        assert result is not None
        assert result.ticker == "AAPL"
        assert result.current_price == 150.25  # From mock info
        assert result.change_percent != 0  # Should have calculated change


@pytest.mark.unit
@pytest.mark.market_data
class TestAnalytics:
    """Test analytics functions."""

    @patch("yfinance.Ticker")
    def test_compare_performance(self, mock_ticker_class):
        """Compare performance across multiple tickers."""
        # Setup mock for multiple tickers
        def mock_ticker_side_effect(ticker):
            mock = MagicMock()
            mock.info = get_mock_ticker_info(ticker)

            # Mock history for price changes
            history_data = get_mock_price_history(ticker)
            history_df = pd.DataFrame(history_data)
            history_df.set_index("Date", inplace=True)
            mock.history.return_value = history_df

            return mock

        mock_ticker_class.side_effect = mock_ticker_side_effect

        # Call compare_performance
        result = compare_performance(["AAPL", "TSLA"], metric="current_price")

        # Verify result
        assert result is not None
        assert len(result.results) == 2
        assert all(r.ticker in ["AAPL", "TSLA"] for r in result.results)


@pytest.mark.unit
@pytest.mark.market_data
class TestTechnicalIndicators:
    """Test technical analysis indicators."""

    @patch("yfinance.Ticker")
    def test_calculate_sma(self, mock_ticker_class):
        """Calculate Simple Moving Average."""
        # Setup mock
        mock_ticker = MagicMock()

        # Create sufficient price history
        history_data = get_mock_price_history("AAPL", period="6mo")
        history_df = pd.DataFrame(history_data)
        history_df.set_index("Date", inplace=True)
        mock_ticker.history.return_value = history_df

        mock_ticker_class.return_value = mock_ticker

        # Calculate SMA with window that fits our data
        result = calculate_sma("AAPL", window=20)

        # Should return TechnicalIndicator object
        assert result is not None
        assert result.ticker == "AAPL"
        assert result.indicator_type == "SMA"
        assert result.value > 0

    @patch("yfinance.Ticker")
    def test_calculate_sma_insufficient_data(self, mock_ticker_class):
        """SMA with insufficient data returns None."""
        # Setup mock with very little data
        mock_ticker = MagicMock()

        # Only 5 price points
        history_data = get_mock_price_history("AAPL", period="1mo")[:5]
        history_df = pd.DataFrame(history_data)
        history_df.set_index("Date", inplace=True)
        mock_ticker.history.return_value = history_df

        mock_ticker_class.return_value = mock_ticker

        # Request window larger than available data
        result = calculate_sma("AAPL", window=50)

        # Should return None
        assert result is None


@pytest.mark.unit
@pytest.mark.market_data
class TestErrorHandling:
    """Test error handling across market data tools."""

    @patch("yfinance.Ticker")
    def test_yfinance_exception_caught(self, mock_ticker_class):
        """All yfinance exceptions should be caught gracefully."""
        # Mock to raise exception
        mock_ticker_class.side_effect = Exception("API error")

        # Should not raise, should return None
        price = get_current_price("AAPL")
        fundamentals = get_stock_fundamentals("AAPL")
        price_change = calculate_price_change("AAPL")

        assert price is None
        assert fundamentals is None
        assert price_change is None

    @patch("yfinance.Ticker")
    def test_technical_indicator_error_handling(self, mock_ticker_class):
        """Technical indicators handle errors gracefully."""
        # Mock to raise exception
        mock_ticker_class.side_effect = Exception("API error")

        # Should not raise, should return None
        sma = calculate_sma("AAPL", window=50)
        assert sma is None
