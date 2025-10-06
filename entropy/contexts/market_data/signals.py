from typing import Optional, Callable
from datetime import datetime
import pandas as pd
from loguru import logger

from .data_structures import TechnicalIndicator
from .tools import get_price_history


def _get_closes(ticker: str, period: str, min_length: int) -> Optional[pd.DataFrame]:
    """Helper to fetch and validate price history."""
    history = get_price_history(ticker, period=period)
    if not history or len(history.prices) < min_length:
        
        return None
    closes = [p.close for p in history.prices if p.close is not None]
    return pd.DataFrame({"close": closes}) if len(closes) >= min_length else None


def _safe_indicator(ticker: str, indicator_type: str, calc_fn: Callable, error_msg: str) -> Optional[TechnicalIndicator]:
    """Wrap indicator calculation with error handling."""
    try:
        return calc_fn()
    except Exception as e:
        logger.error(f"{error_msg} {ticker}: {e}")
        return None


def calculate_sma(ticker: str, window: int = 50) -> Optional[TechnicalIndicator]:
    """Calculate Simple Moving Average."""
    
    def calc():
        df = _get_closes(ticker, "6mo" if window <= 50 else "1y", window)
        if df is None:
            return None
        return TechnicalIndicator(
            ticker=ticker.upper(), indicator_type="SMA",
            value=float(df["close"].rolling(window=window).mean().iloc[-1]),
            timestamp=datetime.now(), parameters={"window": window}
        )
    return _safe_indicator(ticker, "SMA", calc, "Error calculating SMA for")


def calculate_ema(ticker: str, window: int = 50) -> Optional[TechnicalIndicator]:
    """Calculate Exponential Moving Average."""
    
    def calc():
        df = _get_closes(ticker, "6mo" if window <= 50 else "1y", window)
        if df is None:
            return None
        return TechnicalIndicator(
            ticker=ticker.upper(), indicator_type="EMA",
            value=float(df["close"].ewm(span=window, adjust=False).mean().iloc[-1]),
            timestamp=datetime.now(), parameters={"window": window}
        )
    return _safe_indicator(ticker, "EMA", calc, "Error calculating EMA for")


def calculate_rsi(ticker: str, period: int = 14) -> Optional[TechnicalIndicator]:
    """Calculate Relative Strength Index (0-100)."""
    
    def calc():
        df = _get_closes(ticker, "3mo", period + 1)
        if df is None:
            return None
        delta = df["close"].diff()
        gains = delta.where(delta > 0, 0).rolling(window=period).mean()
        losses = -delta.where(delta < 0, 0).rolling(window=period).mean()
        rs = gains / losses
        rsi = 100 - (100 / (1 + rs))
        return TechnicalIndicator(
            ticker=ticker.upper(), indicator_type="RSI",
            value=float(rsi.iloc[-1]),
            timestamp=datetime.now(), parameters={"period": period}
        )
    return _safe_indicator(ticker, "RSI", calc, "Error calculating RSI for")


def calculate_macd(ticker: str) -> Optional[TechnicalIndicator]:
    """Calculate 'Moving Average Convergence Divergence' (MACD) (12-day EMA - 26-day EMA)."""
    
    def calc():
        df = _get_closes(ticker, "6mo", 26)
        if df is None:

            return None
        ema_12 = df["close"].ewm(span=12, adjust=False).mean()
        ema_26 = df["close"].ewm(span=26, adjust=False).mean()
        return TechnicalIndicator(
            ticker=ticker.upper(), indicator_type="MACD",
            value=float((ema_12 - ema_26).iloc[-1]),
            timestamp=datetime.now(), parameters={"fast_period": 12, "slow_period": 26}
        )
    return _safe_indicator(ticker, "MACD", calc, "Error calculating MACD for")


def detect_golden_cross(ticker: str) -> Optional[bool]:
    """Detect the so-called 'golden cross' (50-day MA crosses above 200-day MA)."""
    try:
        df = _get_closes(ticker, "1y", 200)
        if df is None:
            return None
        sma_50 = df["close"].rolling(window=50).mean()
        sma_200 = df["close"].rolling(window=200).mean()
        if len(sma_50) < 2 or len(sma_200) < 2:
            return None
        return (sma_50.iloc[-2] <= sma_200.iloc[-2]) and (sma_50.iloc[-1] > sma_200.iloc[-1])
    except Exception as e:
        logger.error(f"Error detecting golden cross for {ticker}: {e}")
        return None
