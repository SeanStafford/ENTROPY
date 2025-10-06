from typing import Optional
from datetime import datetime
import yfinance as yf
from loguru import logger

from .data_structures import StockPrice, PriceHistory, PricePoint


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

def get_price_history(ticker: str, period: str = "1mo") -> Optional[PriceHistory]:
    """Get historical price data."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        if hist.empty:
            return None

        prices = [
            PricePoint(
                date=date,
                open=row.get("Open"),
                high=row.get("High"),
                low=row.get("Low"),
                close=row.get("Close"),
                volume=int(row.get("Volume")) if row.get("Volume") else None,
            )
            for date, row in hist.iterrows()
        ]

        return PriceHistory(
            ticker=ticker.upper(),
            prices=prices,
            period=period,
            start_date=hist.index[0] if len(hist) > 0 else None,
            end_date=hist.index[-1] if len(hist) > 0 else None,
        )
    except Exception as e:
        logger.error(f"Error fetching history for {ticker}: {e}")
        return None
