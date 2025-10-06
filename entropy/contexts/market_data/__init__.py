"""
Market Data Context: Quantitative stock information and technical analysis.

This context handles numerical stock data (prices, volumes, technical indicators)
and provides tools for agents to query and analyze market data.
"""

# Data structures
from .data_structures import (
    StockPrice,
    StockFundamentals,
    PriceHistory,
    PricePoint,
    PriceChange,
    TechnicalIndicator,
    PerformanceResult,
    PerformanceComparison,
)

# Core tools
from .tools import (
    get_current_price,
    get_stock_fundamentals,
    get_price_history,
    calculate_price_change,
)

# Analytics
from .analytics import (
    compare_performance,
    find_top_performers,
    calculate_returns,
)

# Technical signals
from .signals import (
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    detect_golden_cross,
)

__all__ = [
    # Data structures
    "StockPrice",
    "StockFundamentals",
    "PriceHistory",
    "PricePoint",
    "PriceChange",
    "TechnicalIndicator",
    "PerformanceResult",
    "PerformanceComparison",
    # Core tools
    "get_current_price",
    "get_stock_fundamentals",
    "get_price_history",
    "calculate_price_change",
    # Analytics
    "compare_performance",
    "find_top_performers",
    "calculate_returns",
    # Technical signals
    "calculate_sma",
    "calculate_ema",
    "calculate_rsi",
    "calculate_macd",
    "detect_golden_cross",
]
