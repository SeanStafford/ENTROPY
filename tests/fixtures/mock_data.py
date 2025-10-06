"""Mock data for testing without network calls to yfinance API."""

from datetime import datetime, timedelta
from typing import Dict, Any


def get_mock_ticker_info(ticker: str) -> Dict[str, Any]:
    """
    Get mock yfinance ticker.info dict for a given ticker.

    This replaces network calls to yfinance API during testing.
    """
    mock_data = {
        "AAPL": {
            "currentPrice": 150.25,
            "previousClose": 148.50,
            "dayHigh": 151.00,
            "dayLow": 147.80,
            "volume": 50000000,
            "marketCap": 2400000000000,
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "fiftyDayAverage": 145.50,
            "twoHundredDayAverage": 140.00,
            "fiftyTwoWeekHigh": 155.00,
            "fiftyTwoWeekLow": 125.00,
            "longName": "Apple Inc.",
        },
        "TSLA": {
            "currentPrice": 250.00,
            "previousClose": 245.00,
            "dayHigh": 252.50,
            "dayLow": 248.00,
            "volume": 80000000,
            "marketCap": 800000000000,
            "sector": "Consumer Cyclical",
            "industry": "Auto Manufacturers",
            "fiftyDayAverage": 240.00,
            "twoHundredDayAverage": 220.00,
            "fiftyTwoWeekHigh": 270.00,
            "fiftyTwoWeekLow": 180.00,
            "longName": "Tesla, Inc.",
        },
        "MSFT": {
            "currentPrice": 380.50,
            "previousClose": 378.00,
            "dayHigh": 382.00,
            "dayLow": 377.50,
            "volume": 30000000,
            "marketCap": 2800000000000,
            "sector": "Technology",
            "industry": "Software",
            "fiftyDayAverage": 370.00,
            "twoHundredDayAverage": 350.00,
            "fiftyTwoWeekHigh": 390.00,
            "fiftyTwoWeekLow": 320.00,
            "longName": "Microsoft Corporation",
        },
        "NVDA": {
            "currentPrice": 500.00,
            "previousClose": 490.00,
            "dayHigh": 505.00,
            "dayLow": 495.00,
            "volume": 45000000,
            "marketCap": 1200000000000,
            "sector": "Technology",
            "industry": "Semiconductors",
            "fiftyDayAverage": 480.00,
            "twoHundredDayAverage": 450.00,
            "fiftyTwoWeekHigh": 520.00,
            "fiftyTwoWeekLow": 400.00,
            "longName": "NVIDIA Corporation",
        },
        "F": {
            "currentPrice": 12.50,
            "previousClose": 12.30,
            "dayHigh": 12.75,
            "dayLow": 12.20,
            "volume": 60000000,
            "marketCap": 50000000000,
            "sector": "Consumer Cyclical",
            "industry": "Auto Manufacturers",
            "fiftyDayAverage": 12.00,
            "twoHundredDayAverage": 11.50,
            "fiftyTwoWeekHigh": 13.50,
            "fiftyTwoWeekLow": 10.00,
            "longName": "Ford Motor Company",
        },
    }

    return mock_data.get(ticker, {})


def get_mock_price_history(ticker: str, period: str = "1mo") -> Dict[str, Any]:
    """
    Get mock price history for a ticker.

    Returns data in the format that yfinance.Ticker.history() would return.
    """
    # Generate 30 days of synthetic price data
    end_date = datetime.now()
    dates = [end_date - timedelta(days=i) for i in range(30, 0, -1)]

    # Base prices for different tickers
    base_prices = {
        "AAPL": 150.0,
        "TSLA": 250.0,
        "MSFT": 380.0,
        "NVDA": 500.0,
        "F": 12.5,
    }

    base_price = base_prices.get(ticker, 100.0)

    # Generate synthetic OHLCV data
    history_data = []
    for i, date in enumerate(dates):
        # Add some synthetic variation
        variation = (i % 10 - 5) * 0.01 * base_price
        open_price = base_price + variation
        close_price = open_price + ((i % 5 - 2) * 0.005 * base_price)
        high_price = max(open_price, close_price) * 1.01
        low_price = min(open_price, close_price) * 0.99
        volume = 50000000 + (i % 10) * 1000000

        history_data.append(
            {
                "Date": date,
                "Open": open_price,
                "High": high_price,
                "Low": low_price,
                "Close": close_price,
                "Volume": volume,
            }
        )

    return history_data


# Sample news articles for testing (used by conftest.py fixtures)
MOCK_ARTICLES = [
    {
        "text": "Apple Inc announces record Q3 earnings with iPhone sales growth",
        "metadata": {
            "tickers": ["AAPL"],
            "title": "Apple Q3 Earnings Beat Expectations",
            "publisher": "Financial Times",
            "link": "https://example.com/aapl1",
            "publish_date": datetime(2024, 10, 1),
        },
    },
    {
        "text": "Tesla unveils new electric vehicle manufacturing plant in Texas",
        "metadata": {
            "tickers": ["TSLA"],
            "title": "Tesla Expands Production Capacity",
            "publisher": "Reuters",
            "link": "https://example.com/tsla1",
            "publish_date": datetime(2024, 10, 2),
        },
    },
    {
        "text": "Microsoft and Amazon compete for cloud computing market share",
        "metadata": {
            "tickers": ["MSFT", "AMZN"],
            "title": "Cloud Wars: Microsoft vs Amazon",
            "publisher": "Bloomberg",
            "link": "https://example.com/cloud1",
            "publish_date": datetime(2024, 10, 3),
        },
    },
    {
        "text": "Ford announces partnership with electric vehicle charging network",
        "metadata": {
            "tickers": ["F"],
            "title": "Ford Partners on EV Infrastructure",
            "publisher": "Wall Street Journal",
            "link": "https://example.com/ford1",
            "publish_date": datetime(2024, 10, 4),
        },
    },
    {
        "text": "NVIDIA reports strong demand for AI chips and data center GPUs",
        "metadata": {
            "tickers": ["NVDA"],
            "title": "NVIDIA AI Chip Sales Surge",
            "publisher": "TechCrunch",
            "link": "https://example.com/nvda1",
            "publish_date": datetime(2024, 10, 5),
        },
    },
]
