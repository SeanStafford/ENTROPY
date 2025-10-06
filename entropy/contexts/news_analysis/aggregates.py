"""News timeline aggregates for ticker analysis."""

from typing import List, Tuple, Dict, Any
from datetime import date, timedelta
from collections import defaultdict
from loguru import logger

from .data_structures import NewsArticle
from .constants import SentimentLabel


class TickerNewsTimeline:
    """News timeline aggregate for a ticker."""

    def __init__(self, ticker: str, articles: List[NewsArticle]):
        self.ticker = ticker.upper()
        self.articles = sorted(articles, key=lambda a: a.publish_date, reverse=True)
        logger.debug(f"{ticker}: {len(articles)} articles")

    def get_sentiment_trend(self, days: int = 30) -> List[Tuple[date, float]]:
        """Daily average sentiment scores."""
        if not self.articles:
            return []
        # articles are already sorted newest first (see __init__)
        most_recent = self.articles[0].publish_date.date()
        start_date = most_recent - timedelta(days=days)

        articles_by_date = defaultdict(list)
        for article in self.articles:
            if article.publish_date.date() >= start_date and article.has_sentiment():
                articles_by_date[article.publish_date.date()].append(article)

        trend = []
        current_date = start_date
        while current_date <= most_recent:
            if current_date in articles_by_date:
                avg = sum(a.sentiment.positive - a.sentiment.negative for a in articles_by_date[current_date]) / len(articles_by_date[current_date])
                trend.append((current_date, avg))
            else:
                trend.append((current_date, 0.0))
            current_date += timedelta(days=1)
        return trend

    def get_volume_spike_dates(self, threshold: float = 2.0) -> List[date]:
        """Dates with unusually high article volume."""
        if not self.articles:
            return []
        articles_by_date = defaultdict(int)
        for article in self.articles:
            articles_by_date[article.publish_date.date()] += 1
        counts = list(articles_by_date.values())
        avg_volume = sum(counts) / len(counts) if counts else 0
        # spike = 2x normal coverage (probably something interesting happened)
        return sorted([d for d, count in articles_by_date.items() if count > threshold * avg_volume])

    def get_recent_sentiment_shift(self, window_days: int = 7) -> float:
        """Sentiment change: recent window vs previous window."""
        if not self.articles:
            return 0.0
        most_recent = self.articles[0].publish_date.date()
        recent_start = most_recent - timedelta(days=window_days)
        previous_start = recent_start - timedelta(days=window_days)

        recent = [a for a in self.articles if recent_start <= a.publish_date.date() <= most_recent and a.has_sentiment()]
        previous = [a for a in self.articles if previous_start <= a.publish_date.date() < recent_start and a.has_sentiment()]

        # need both windows to compare
        if not recent or not previous:
            return 0.0
        recent_avg = sum(a.sentiment.positive - a.sentiment.negative for a in recent) / len(recent)
        previous_avg = sum(a.sentiment.positive - a.sentiment.negative for a in previous) / len(previous)
        return recent_avg - previous_avg

    def get_summary_stats(self) -> Dict[str, Any]:
        """Overall statistics for ticker news."""
        if not self.articles:
            return {"article_count": 0}
        dates = [a.publish_date.date() for a in self.articles]
        earliest, latest = min(dates), max(dates)
        # +1 because both endpoints are inclusive (math is hard sometimes)
        days_span = (latest - earliest).days + 1

        with_sentiment = [a for a in self.articles if a.has_sentiment()]
        if with_sentiment:
            avg_sentiment = sum(a.sentiment.positive - a.sentiment.negative for a in with_sentiment) / len(with_sentiment)
            breakdown = defaultdict(int)
            for a in with_sentiment:
                breakdown[a.sentiment.label] += 1
        else:
            avg_sentiment, breakdown = 0.0, {}

        return {
            "article_count": len(self.articles),
            "date_range": (earliest, latest),
            "days_span": days_span,
            "avg_sentiment": avg_sentiment,
            "sentiment_breakdown": dict(breakdown),
            "articles_per_day": len(self.articles) / days_span if days_span > 0 else 0.0,
        }

    def filter_by_sentiment(self, sentiment: SentimentLabel) -> List[NewsArticle]:
        """Articles matching specified sentiment."""
        filtered = [a for a in self.articles if a.has_sentiment() and a.sentiment.label == sentiment.value]
        logger.debug(f"{len(filtered)} {sentiment.value} articles")
        return filtered
