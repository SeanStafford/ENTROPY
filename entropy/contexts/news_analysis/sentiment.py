"""Financial sentiment analysis using FinBERT."""

from typing import List
from loguru import logger
from transformers import pipeline

from .data_structures import NewsArticle, SentimentScore, TickerSentiment
from .constants import (
    DEFAULT_SENTIMENT_MODEL,
    SENTIMENT_MAX_LENGTH,
    DEFAULT_BATCH_SIZE,
    POSITIVE_THRESHOLD,
)


class SentimentAnalyzer:
    """Financial sentiment analysis using FinBERT."""

    def __init__(self, model_name: str = DEFAULT_SENTIMENT_MODEL):
        self.model_name = model_name
        logger.info(f"Loading sentiment model: {model_name}")
        self.pipeline = pipeline(
            "sentiment-analysis",
            model=model_name,
            return_all_scores=True,
            device=-1,
        )
        logger.success("Sentiment model loaded")

    def analyze_text(self, text: str) -> SentimentScore:
        """Analyze sentiment of text string."""
        if not text or not text.strip():
            return SentimentScore(0.0, 0.0, 1.0, "neutral", 1.0, self.model_name)

        # Truncate if needed
        if len(text) > SENTIMENT_MAX_LENGTH:
            text = text[:SENTIMENT_MAX_LENGTH]

        try:
            raw_output = self.pipeline(text)
            scores = {item["label"].lower(): item["score"] for item in raw_output[0]}

            dominant_label = max(scores, key=scores.get)

            return SentimentScore(
                positive=scores.get("positive", 0.0),
                negative=scores.get("negative", 0.0),
                neutral=scores.get("neutral", 0.0),
                label=dominant_label,
                confidence=scores[dominant_label],
                model_name=self.model_name,
            )
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return SentimentScore(0.33, 0.33, 0.34, "neutral", 0.34, self.model_name)

    def analyze_article(self, article: NewsArticle) -> NewsArticle:
        """Analyze article and return copy with sentiment."""
        combined_text = f"{article.title}. {article.text}"
        sentiment = self.analyze_text(combined_text)

        from dataclasses import replace
        return replace(article, sentiment=sentiment)

    def analyze_batch(
        self, articles: List[NewsArticle], batch_size: int = DEFAULT_BATCH_SIZE
    ) -> List[NewsArticle]:
        """Analyze sentiment for multiple articles."""
        if not articles:
            return []

        logger.info(f"Analyzing sentiment for {len(articles)} articles")
        analyzed = []

        for article in articles:
            analyzed.append(self.analyze_article(article))

        logger.success(f"Sentiment analysis complete")
        return analyzed

    def aggregate_ticker_sentiment(
        self, ticker: str, articles: List[NewsArticle], timeframe_days: int = 7
    ) -> TickerSentiment:
        """Aggregate sentiment across articles for a ticker."""
        articles_with_sentiment = [a for a in articles if a.has_sentiment()]

        if not articles_with_sentiment:
            raise ValueError("No articles have sentiment scores")

        avg_positive = sum(a.sentiment.positive for a in articles_with_sentiment) / len(articles_with_sentiment)
        avg_negative = sum(a.sentiment.negative for a in articles_with_sentiment) / len(articles_with_sentiment)
        avg_neutral = sum(a.sentiment.neutral for a in articles_with_sentiment) / len(articles_with_sentiment)

        if avg_positive > POSITIVE_THRESHOLD:
            overall = "positive"
        elif avg_negative > POSITIVE_THRESHOLD:
            overall = "negative"
        elif avg_neutral > POSITIVE_THRESHOLD:
            overall = "neutral"
        else:
            overall = "mixed"

        return TickerSentiment(
            ticker=ticker.upper(),
            overall_sentiment=overall,
            avg_positive=avg_positive,
            avg_negative=avg_negative,
            avg_neutral=avg_neutral,
            article_count=len(articles_with_sentiment),
            timeframe_days=timeframe_days,
        )
