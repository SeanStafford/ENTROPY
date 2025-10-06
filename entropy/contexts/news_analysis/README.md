# News Analysis Context

Financial news sentiment analysis, text processing, and timeline analytics.

## Components

### Models
- **NewsArticle**: News article with text, metadata, and sentiment
- **SentimentScore**: Sentiment result (positive/negative/neutral)
- **TickerSentiment**: Aggregated sentiment for a ticker
- **NewsMetadata**: Article tracking metadata

### Tools
- **SentimentAnalyzer**: FinBERT-based sentiment analysis
- **NewsProcessor**: Text cleaning and formatting
- **TickerNewsTimeline**: Timeline analytics and trends

### Constants
- **SentimentLabel**: Sentiment enum (POSITIVE, NEGATIVE, NEUTRAL, MIXED)
- **NewsSource**: Source enum (YFINANCE, MANUAL)
- **POSITIVE_THRESHOLD**: 0.6
- **NEGATIVE_THRESHOLD**: 0.4

## Quick Start

```python
from entropy.contexts.news_analysis import SentimentAnalyzer, NewsArticle
from datetime import datetime

article = NewsArticle(
    title="Apple Reports Record Earnings",
    publisher="WSJ",
    link="https://wsj.com/...",
    publish_date=datetime.now(),
    text="Apple Inc reported strong results...",
    tickers=["AAPL"]
)

analyzer = SentimentAnalyzer()
analyzed = analyzer.analyze_article(article)
print(f"{analyzed.sentiment.label}: {analyzed.sentiment.confidence:.0%}")
```

### Timeline Analysis

```python
from entropy.contexts.news_analysis import TickerNewsTimeline

timeline = TickerNewsTimeline("AAPL", analyzed_articles)
trend = timeline.get_sentiment_trend(days=7)
shift = timeline.get_recent_sentiment_shift(window_days=7)
stats = timeline.get_summary_stats()
```

## API Reference

### SentimentAnalyzer
```python
analyzer = SentimentAnalyzer()
score = analyzer.analyze_text("Stock prices surge...")
analyzed = analyzer.analyze_article(article)
analyzed_list = analyzer.analyze_batch(articles, batch_size=8)
ticker_sentiment = analyzer.aggregate_ticker_sentiment("AAPL", articles)
```

### NewsProcessor
```python
processor = NewsProcessor()
clean = processor.clean_text(raw_html_text)
metadata = processor.extract_metadata_from_yfinance(raw_dict)
display = processor.format_for_display(article, max_length=200)
unique = processor.deduplicate_by_link(articles)
```

### TickerNewsTimeline
```python
timeline = TickerNewsTimeline("AAPL", articles)
trend = timeline.get_sentiment_trend(days=30)
spikes = timeline.get_volume_spike_dates(threshold=2.0)
shift = timeline.get_recent_sentiment_shift(window_days=7)
stats = timeline.get_summary_stats()
positive = timeline.filter_by_sentiment(SentimentLabel.POSITIVE)
```

## Data Models

### NewsArticle
```python
title: str
publisher: str
link: str
publish_date: datetime
text: str
tickers: List[str]
sentiment: Optional[SentimentScore]
metadata: Optional[NewsMetadata]
```

### SentimentScore
```python
positive: float
negative: float
neutral: float
label: str
confidence: float
model_name: str
```

### TickerSentiment
```python
ticker: str
overall_sentiment: str
avg_positive: float
avg_negative: float
avg_neutral: float
article_count: int
timeframe_days: int
```

## Integration

### With retrieval/
```python
from entropy.contexts.retrieval import YFinanceFetcher
from entropy.contexts.news_analysis import NewsProcessor, NewsArticle

fetcher = YFinanceFetcher()
processor = NewsProcessor()
raw_articles = fetcher.fetch_news(["AAPL"])
# Convert raw → NewsArticle with processor.clean_text()
```

### With generation/
```python
from entropy.contexts.news_analysis import SentimentAnalyzer, TickerNewsTimeline

class NewsAgent:
    def __init__(self):
        self.analyzer = SentimentAnalyzer()

    def analyze_ticker(self, ticker, articles):
        analyzed = self.analyzer.analyze_batch(articles)
        timeline = TickerNewsTimeline(ticker, analyzed)
        return self.synthesize_narrative(timeline)
```

## Dependencies

- `transformers`: FinBERT model
- `torch`: PyTorch backend
- `loguru`: Structured logging
