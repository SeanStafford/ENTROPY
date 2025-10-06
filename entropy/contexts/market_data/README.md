# Market Data Context

Quantitative stock data, technical indicators, and performance analytics for ENTROPY.

## Overview

The `market_data` context handles quantitative information about stocks - prices, volumes, fundamentals, and technical indicators.

## Components

### Data Structures
- **StockPrice** - Current price snapshot
- **StockFundamentals** - Company metrics
- **PriceHistory** - Historical OHLCV data
- **PriceChange** - Price change metrics
- **TechnicalIndicator** - Technical indicator results
- **PerformanceComparison** - Multi-stock ranking

### Tools
- `get_current_price(ticker)` - Current price snapshot
- `get_stock_fundamentals(ticker)` - Company fundamentals
- `get_price_history(ticker, period)` - Historical data
- `calculate_price_change(ticker, period)` - Price change

### Analytics
- `compare_performance(tickers, metric, period)` - Compare stocks
- `find_top_performers(tickers, metric, period, n)` - Top N stocks
- `calculate_returns(ticker, start_date, end_date)` - Returns

### Signals
- `calculate_sma(ticker, window)` - Simple Moving Average
- `calculate_ema(ticker, window)` - Exponential Moving Average
- `calculate_rsi(ticker, period)` - RSI (0-100)
- `calculate_macd(ticker)` - MACD
- `detect_golden_cross(ticker)` - MA crossover

## Quick Start

```python
from entropy.contexts.market_data import (
    get_current_price,
    calculate_price_change,
    compare_performance,
    calculate_rsi
)

# Get current price
price = get_current_price("AAPL")
if price:
    print(f"${price.current_price}")

# Calculate daily change
change = calculate_price_change("AAPL", period="1d")
if change:
    print(f"{change.change_percent:+.2f}%")

# Compare stocks
tickers = ["AAPL", "MSFT", "GOOGL"]
comparison = compare_performance(tickers, metric="price_change_percent", period="1d")
for result in comparison.results:
    print(f"{result.ticker}: {result.value:+.2f}%")

# Technical indicator
rsi = calculate_rsi("AAPL", period=14)
if rsi:
    print(f"RSI: {rsi.value:.1f}")
```

## Valid Parameters

**Periods:** `"1d"`, `"5d"`, `"1mo"`, `"3mo"`, `"6mo"`, `"1y"`, `"2y"`, `"5y"`, `"10y"`, `"ytd"`, `"max"`

**Metrics:** `"price_change_percent"`, `"price_change_amount"`, `"current_price"`, `"volume"`

**Dates:** `"YYYY-MM-DD"` format

## Integration

### With Agents

```python
from entropy.contexts.market_data import get_current_price, calculate_rsi

class MarketDataAgent:
    def analyze(self, ticker: str):
        price = get_current_price(ticker)
        rsi = calculate_rsi(ticker)

        if price and rsi:
            return f"{ticker}: ${price.current_price}, RSI {rsi.value:.1f}"
```

## Error Handling

All functions return `Optional` types:
- Returns `None` if ticker invalid
- Returns `None` if insufficient data
- Logs errors with `loguru`

## Dependencies

- `yfinance` - Stock data API
- `pandas` - Data processing
- `pydantic` - Type-safe models
- `loguru` - Logging
