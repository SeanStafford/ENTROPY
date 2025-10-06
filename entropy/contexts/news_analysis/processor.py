"""Text processing for news articles."""

import re
import hashlib
from typing import List, Dict
from datetime import datetime
from loguru import logger

from .data_structures import NewsArticle, NewsMetadata
from .constants import NewsSource


class NewsProcessor:
    """Process and clean news article text."""

    def __init__(self):
        self.html_entities = {
            "&amp;": "&",
            "&lt;": "<",
            "&gt;": ">",
            "&quot;": '"',
            "&#39;": "'",
            "&nbsp;": " ",
        }

    def clean_text(self, text: str) -> str:
        """Remove HTML, fix encoding, normalize whitespace."""
        if not text:
            return ""

        # Remove HTML tags
        cleaned = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"<style[^>]*>.*?</style>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"<[^>]+>", "", cleaned)

        # Replace HTML entities
        for entity, replacement in self.html_entities.items():
            cleaned = cleaned.replace(entity, replacement)

        # Normalize whitespace
        cleaned = re.sub(r"\n+", "\n", cleaned)
        cleaned = cleaned.replace("\t", " ")
        cleaned = re.sub(r" +", " ", cleaned)

        return cleaned.strip()

    def extract_metadata_from_yfinance(self, raw_article: dict) -> NewsMetadata:
        """Convert yfinance article dict to NewsMetadata."""
        link = raw_article.get("link", "")
        article_hash = hashlib.md5(link.encode()).hexdigest() if link else None

        return NewsMetadata(
            source=NewsSource.YFINANCE.value,
            fetch_timestamp=datetime.now(),
            article_hash=article_hash,
            language="en",
        )

    def format_for_display(self, article: NewsArticle, max_length: int = 200) -> str:
        """Format article as human-readable summary with sentiment badge."""
        if article.has_sentiment():
            sentiment_label = article.sentiment.label.upper()
            confidence = article.sentiment.confidence
            badge = f"[{sentiment_label} {confidence:.0%}]"
        else:
            badge = "[NO SENTIMENT]"

        header = f"{article.title} - {article.publisher}"

        preview = article.text[:max_length]
        if len(article.text) > max_length:
            preview += "..."

        return f"{badge} {header}\n{preview}"

    def deduplicate_by_link(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicate articles based on link URL."""
        seen_links = set()
        unique_articles = []

        for article in articles:
            if article.link not in seen_links:
                seen_links.add(article.link)
                unique_articles.append(article)

        if len(unique_articles) < len(articles):
            logger.info(f"Deduplication: {len(articles)} → {len(unique_articles)}")

        return unique_articles
