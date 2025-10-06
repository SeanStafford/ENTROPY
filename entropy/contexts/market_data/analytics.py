from typing import List, Optional
from datetime import datetime
from loguru import logger

from .data_structures import PerformanceComparison, PerformanceResult
from .tools import get_current_price, calculate_price_change, get_price_history


def compare_performance(
    tickers: List[str], metric: str = "price_change_percent", period: str = "1d"
) -> Optional[PerformanceComparison]:
    """Compare performance across multiple stocks."""
    try:
        results = []

        for ticker in tickers:
            value = None

            if metric == "price_change_percent":
                change = calculate_price_change(ticker, period=period)
                value = change.change_percent if change else None
            elif metric == "price_change_amount":
                change = calculate_price_change(ticker, period=period)
                value = change.change_amount if change else None
            elif metric == "current_price":
                price = get_current_price(ticker)
                value = price.current_price if price else None
            elif metric == "volume":
                price = get_current_price(ticker)
                value = float(price.volume) if price and price.volume else None

            results.append(PerformanceResult(ticker=ticker.upper(), value=value, metric=metric))

        results.sort(key=lambda x: x.value if x.value is not None else float("-inf"), reverse=True)

        return PerformanceComparison(tickers=[t.upper() for t in tickers], metric=metric, results=results, period=period)
    except Exception as e:
        logger.error(f"Error comparing performance: {e}")
        return None


def find_top_performers(
    tickers: List[str], metric: str = "price_change_percent", period: str = "1d", n: int = 5
) -> List[PerformanceResult]:
    """Find top N performing stocks."""
    try:
        comparison = compare_performance(tickers, metric=metric, period=period)
        return comparison.results[:n] if comparison else []
    except Exception as e:
        logger.error(f"Error finding top performers: {e}")
        return []


def calculate_returns(ticker: str, start_date: str, end_date: str) -> Optional[float]:
    """Calculate returns between two dates."""
    try:
        history = get_price_history(ticker, period="1y")

        if not history or len(history.prices) < 2:
            return None

        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        start_price = None
        end_price = None

        for price_point in history.prices:
            if price_point.date.date() == start_dt.date():
                start_price = price_point.close
            if price_point.date.date() == end_dt.date():
                end_price = price_point.close

        if start_price is None:
            start_price = history.prices[0].close
        if end_price is None:
            end_price = history.prices[-1].close

        if start_price is None or end_price is None or start_price == 0:
            return None

        return ((end_price - start_price) / start_price) * 100
    except Exception as e:
        logger.error(f"Error calculating returns for {ticker}: {e}")
        return None
