"""
News Analysis Context

Domain-driven context for financial news processing, sentiment analysis,
and temporal trend analysis.

This context handles qualitative information about companies, treating
tickers as companies with stories, events, and market perception.

Public API
----------

Models:
    NewsArticle: Canonical representation of a news article
    SentimentScore: Sentiment analysis result (positive/negative/neutral)
    TickerSentiment: Aggregated sentiment for a ticker
    NewsMetadata: Immutable article metadata for tracking

Tools:
    SentimentAnalyzer: Financial sentiment analysis using FinBERT
    NewsProcessor: Text cleaning, entity extraction, formatting
    TickerNewsTimeline: Rich timeline analysis for a ticker's news

Constants:
    SentimentLabel: Enum for sentiment classification
    NewsSource: Enum for article source (yfinance, manual, etc.)
    POSITIVE_THRESHOLD: Threshold for positive sentiment (0.6)
    NEGATIVE_THRESHOLD: Threshold for negative sentiment (0.4)

Example Usage
-------------

Sentiment Analysis:
    >>> from entropy.contexts.news_analysis import SentimentAnalyzer, NewsArticle
    >>> analyzer = SentimentAnalyzer()
    >>> article = NewsArticle(title="AAPL soars on earnings", ...)
    >>> analyzed = analyzer.analyze_article(article)
    >>> print(analyzed.sentiment.label)  # "positive"

Timeline Analysis:
    >>> from entropy.contexts.news_analysis import TickerNewsTimeline
    >>> timeline = TickerNewsTimeline("AAPL", articles)
    >>> trend = timeline.get_sentiment_trend(days=7)
    >>> stats = timeline.get_summary_stats()

Processing:
    >>> from entropy.contexts.news_analysis import NewsProcessor
    >>> processor = NewsProcessor()
    >>> clean_text = processor.clean_text(raw_html_text)
    >>> display = processor.format_for_display(article)
"""

# Models
from .data_structures import (
    NewsArticle,
    SentimentScore,
    TickerSentiment,
    NewsMetadata,
)

# Tools
from .sentiment import SentimentAnalyzer
from .processor import NewsProcessor
from .aggregates import TickerNewsTimeline

# Constants
from .constants import (
    SentimentLabel,
    NewsSource,
    POSITIVE_THRESHOLD,
    NEGATIVE_THRESHOLD,
    DEFAULT_SENTIMENT_MODEL,
    SENTIMENT_MAX_LENGTH,
    DEFAULT_BATCH_SIZE,
)

__all__ = [
    # Models
    "NewsArticle",
    "SentimentScore",
    "TickerSentiment",
    "NewsMetadata",
    # Tools
    "SentimentAnalyzer",
    "NewsProcessor",
    "TickerNewsTimeline",
    # Constants
    "SentimentLabel",
    "NewsSource",
    "POSITIVE_THRESHOLD",
    "NEGATIVE_THRESHOLD",
    "DEFAULT_SENTIMENT_MODEL",
    "SENTIMENT_MAX_LENGTH",
    "DEFAULT_BATCH_SIZE",
]
