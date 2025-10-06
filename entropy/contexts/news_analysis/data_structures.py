from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class NewsMetadata:
    source: str
    fetch_timestamp: datetime
    article_hash: str
    language: str = "en"


@dataclass
class SentimentScore:
    positive: float
    negative: float
    neutral: float
    label: str
    confidence: float
    model_name: str = "ProsusAI/finbert"


@dataclass
class NewsArticle:
    title: str
    publisher: str
    link: str
    publish_date: datetime
    text: str
    tickers: List[str]
    sentiment: Optional[SentimentScore] = None
    metadata: Optional[NewsMetadata] = None

    def has_sentiment(self) -> bool:
        return self.sentiment is not None

    def primary_ticker(self) -> str:
        return self.tickers[0] if self.tickers else None


@dataclass
class TickerSentiment:
    ticker: str
    overall_sentiment: str
    avg_positive: float
    avg_negative: float
    avg_neutral: float
    article_count: int
    timeframe_days: int = 7

    def dominant_sentiment_score(self) -> float:
        if self.overall_sentiment == "positive":
            return self.avg_positive
        elif self.overall_sentiment == "negative":
            return self.avg_negative
        elif self.overall_sentiment == "neutral":
            return self.avg_neutral
        else:
            return max(self.avg_positive, self.avg_negative, self.avg_neutral)
