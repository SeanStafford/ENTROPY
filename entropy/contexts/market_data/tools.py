from typing import Optional
from datetime import datetime
import yfinance as yf
from loguru import logger

from .data_structures import StockPrice, StockFundamentals, PriceHistory, PriceChange, PricePoint


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


def get_stock_fundamentals(ticker: str) -> Optional[StockFundamentals]:
    """Get company fundamentals and key metrics."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info:
            return None

        return StockFundamentals(
            ticker=ticker.upper(),
            market_cap=info.get("marketCap"),
            sector=info.get("sector"),
            industry=info.get("industry"),
            fifty_day_avg=info.get("fiftyDayAverage"),
            two_hundred_day_avg=info.get("twoHundredDayAverage"),
            fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
            fifty_two_week_low=info.get("fiftyTwoWeekLow"),
            company_name=info.get("longName"),
        )
    except Exception as e:
        logger.error(f"Error fetching fundamentals for {ticker}: {e}")
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


def calculate_price_change(ticker: str, period: str = "1d") -> Optional[PriceChange]:
    """Calculate price change over period."""
    try:
        current_data = get_current_price(ticker)
        if not current_data or not current_data.current_price:
            return None

        history = get_price_history(ticker, period=period)
        if not history or len(history.prices) < 2:
            return None

        previous_price = history.prices[0].close
        current_price = current_data.current_price

        if previous_price is None:
            return None

        change_amount = current_price - previous_price
        change_percent = (change_amount / previous_price) * 100 if previous_price != 0 else 0

        return PriceChange(
            ticker=ticker.upper(),
            current_price=current_price,
            previous_price=previous_price,
            change_amount=change_amount,
            change_percent=change_percent,
            period=period,
        )
    except Exception as e:
        logger.error(f"Error calculating price change for {ticker}: {e}")
        return None
