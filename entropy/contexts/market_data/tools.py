from typing import Optional
from datetime import datetime
import yfinance as yf
from loguru import logger

from .data_structures import StockPrice


def get_current_price(ticker: str) -> Optional[StockPrice]:
    """Get current stock price snapshot."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or "currentPrice" not in info:
            return None

        return StockPrice(
            ticker=ticker.upper(),
            current_price=info.get("currentPrice"),
            previous_close=info.get("previousClose"),
            day_high=info.get("dayHigh"),
            day_low=info.get("dayLow"),
            volume=info.get("volume"),
            timestamp=datetime.now(),
        )
    except Exception as e:
        logger.error(f"Error fetching price for {ticker}: {e}")
        return None

