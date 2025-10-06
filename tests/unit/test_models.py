"""Unit tests for data models.

Tests dataclasses and pydantic models for market data and news analysis.
"""

import pytest
from datetime import datetime

from entropy.contexts.market_data.data_structures import (
    StockPrice,
    StockFundamentals,
    PriceHistory,
    PricePoint,
    PriceChange,
)
from entropy.contexts.news_analysis.models import (
    NewsArticle,
    SentimentScore,
    TickerSentiment,
    NewsMetadata,
)


@pytest.mark.unit
class TestStockPriceDataclass:
    """Test StockPrice dataclass."""

    def test_creation(self):
        """Create StockPrice with valid data."""
        price = StockPrice(
            ticker="AAPL",
            current_price=150.25,
            previous_close=148.50,
            day_high=151.00,
            day_low=147.80,
            volume=50000000,
            timestamp=datetime(2024, 10, 6),
        )

        assert price.ticker == "AAPL"
        assert price.current_price == 150.25
        assert price.volume == 50000000

    def test_optional_fields(self):
        """Optional fields can be None."""
        price = StockPrice(
            ticker="AAPL",
            current_price=150.25,
            previous_close=None,
            day_high=None,
            day_low=None,
            volume=None,
            timestamp=datetime.now(),
        )

        assert price.ticker == "AAPL"
        assert price.previous_close is None


@pytest.mark.unit
class TestPriceChangeCalculation:
    """Test PriceChange dataclass."""

    def test_price_change_dataclass(self):
        """Create PriceChange with calculated values."""
        change = PriceChange(
            ticker="AAPL",
            current_price=150.25,
            previous_price=148.50,
            change_amount=1.75,
            change_percent=1.18,
            period="1d",
        )

        assert change.ticker == "AAPL"
        assert change.change_amount == 1.75
        assert change.change_percent == pytest.approx(1.18, abs=0.01)

    def test_negative_change(self):
        """Handle negative price changes."""
        change = PriceChange(
            ticker="TSLA",
            current_price=245.00,
            previous_price=250.00,
            change_amount=-5.00,
            change_percent=-2.00,
            period="1d",
        )

        assert change.change_amount < 0
        assert change.change_percent < 0


@pytest.mark.unit
class TestNewsArticleModel:
    """Test NewsArticle dataclass."""

    def test_news_article_creation(self):
        """Create NewsArticle with required fields."""
        article = NewsArticle(
            title="Apple Q3 Earnings",
            publisher="Financial Times",
            link="https://example.com/article1",
            publish_date=datetime(2024, 10, 1),
            text="Apple announces record earnings...",
            tickers=["AAPL"],
            sentiment=None,
            metadata=None,
        )

        assert article.title == "Apple Q3 Earnings"
        assert article.tickers == ["AAPL"]
        assert article.sentiment is None

    def test_has_sentiment_method(self):
        """Test has_sentiment() method."""
        # Article without sentiment
        article1 = NewsArticle(
            title="Test",
            publisher="Test Publisher",
            link="https://example.com",
            publish_date=datetime.now(),
            text="Test text",
            tickers=["AAPL"],
        )

        assert article1.has_sentiment() is False

        # Article with sentiment
        sentiment = SentimentScore(
            positive=0.8, negative=0.1, neutral=0.1, label="positive", confidence=0.8
        )

        article2 = NewsArticle(
            title="Test",
            publisher="Test Publisher",
            link="https://example.com",
            publish_date=datetime.now(),
            text="Test text",
            tickers=["AAPL"],
            sentiment=sentiment,
        )

        assert article2.has_sentiment() is True

    def test_primary_ticker_method(self):
        """Test primary_ticker() method."""
        article = NewsArticle(
            title="Test",
            publisher="Test Publisher",
            link="https://example.com",
            publish_date=datetime.now(),
            text="Test text",
            tickers=["AAPL", "MSFT", "GOOGL"],
        )

        # Should return first ticker
        assert article.primary_ticker() == "AAPL"

    def test_primary_ticker_empty_list(self):
        """Handle empty ticker list."""
        article = NewsArticle(
            title="Test",
            publisher="Test Publisher",
            link="https://example.com",
            publish_date=datetime.now(),
            text="Test text",
            tickers=[],
        )

        assert article.primary_ticker() is None


@pytest.mark.unit
class TestSentimentScore:
    """Test SentimentScore dataclass."""

    def test_sentiment_creation(self):
        """Create SentimentScore with valid data."""
        sentiment = SentimentScore(
            positive=0.7,
            negative=0.2,
            neutral=0.1,
            label="positive",
            confidence=0.7,
            model_name="finbert",
        )

        assert sentiment.positive == 0.7
        assert sentiment.label == "positive"
        assert sentiment.confidence == 0.7

    def test_sentiment_sum_approximately_one(self):
        """Sentiment probabilities should sum to ~1.0."""
        sentiment = SentimentScore(
            positive=0.7,
            negative=0.2,
            neutral=0.1,
            label="positive",
            confidence=0.7,
        )

        total = sentiment.positive + sentiment.negative + sentiment.neutral
        assert total == pytest.approx(1.0, abs=0.01)


@pytest.mark.unit
class TestTickerSentiment:
    """Test TickerSentiment aggregated sentiment."""

    def test_ticker_sentiment_creation(self):
        """Create TickerSentiment with aggregated data."""
        ticker_sentiment = TickerSentiment(
            ticker="AAPL",
            overall_sentiment="positive",
            avg_positive=0.65,
            avg_negative=0.20,
            avg_neutral=0.15,
            article_count=10,
            timeframe_days=7,
        )

        assert ticker_sentiment.ticker == "AAPL"
        assert ticker_sentiment.overall_sentiment == "positive"
        assert ticker_sentiment.article_count == 10

    def test_dominant_sentiment_score(self):
        """Test dominant_sentiment_score() method."""
        # Positive sentiment
        sentiment = TickerSentiment(
            ticker="AAPL",
            overall_sentiment="positive",
            avg_positive=0.70,
            avg_negative=0.15,
            avg_neutral=0.15,
            article_count=10,
        )

        assert sentiment.dominant_sentiment_score() == 0.70

        # Negative sentiment
        sentiment_neg = TickerSentiment(
            ticker="TSLA",
            overall_sentiment="negative",
            avg_positive=0.15,
            avg_negative=0.70,
            avg_neutral=0.15,
            article_count=5,
        )

        assert sentiment_neg.dominant_sentiment_score() == 0.70


@pytest.mark.unit
class TestPriceHistory:
    """Test PriceHistory dataclass."""

    def test_price_history_with_multiple_points(self):
        """Create PriceHistory with multiple price points."""
        prices = [
            PricePoint(
                date=datetime(2024, 10, 1),
                open=150.0,
                high=152.0,
                low=149.0,
                close=151.0,
                volume=50000000,
            ),
            PricePoint(
                date=datetime(2024, 10, 2),
                open=151.0,
                high=153.0,
                low=150.0,
                close=152.5,
                volume=55000000,
            ),
        ]

        history = PriceHistory(
            ticker="AAPL",
            prices=prices,
            period="1mo",
            start_date=datetime(2024, 10, 1),
            end_date=datetime(2024, 10, 2),
        )

        assert history.ticker == "AAPL"
        assert len(history.prices) == 2
        assert history.prices[0].close == 151.0
        assert history.prices[1].close == 152.5
