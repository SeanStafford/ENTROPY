"""Constants and enums for news analysis domain."""

from enum import Enum


class SentimentLabel(Enum):
    """Sentiment classification labels."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class NewsSource(Enum):
    """Source of news article data."""
    YFINANCE = "yfinance"
    MANUAL = "manual"


# Financial sentiment thresholds
POSITIVE_THRESHOLD = 0.6
NEGATIVE_THRESHOLD = 0.4

# FinBERT configuration
DEFAULT_SENTIMENT_MODEL = "ProsusAI/finbert"
SENTIMENT_MAX_LENGTH = 512
DEFAULT_BATCH_SIZE = 8
