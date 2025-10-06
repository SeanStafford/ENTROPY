"""Pytest fixtures for ENTROPY tests."""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from entropy.contexts.retrieval import BM25DocumentStore, EmbeddingDocumentStore


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data (save/load tests)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_news_articles():
    """Sample news articles for retrieval testing."""
    return [
        {
            "text": "Apple Inc announces record Q3 earnings with iPhone sales growth",
            "metadata": {
                "tickers": ["AAPL"],
                "title": "Apple Q3 Earnings Beat Expectations",
                "publisher": "Financial Times",
                "link": "https://example.com/aapl1",
                "publish_date": datetime(2024, 10, 1),
            },
        },
        {
            "text": "Tesla unveils new electric vehicle manufacturing plant in Texas",
            "metadata": {
                "tickers": ["TSLA"],
                "title": "Tesla Expands Production Capacity",
                "publisher": "Reuters",
                "link": "https://example.com/tsla1",
                "publish_date": datetime(2024, 10, 2),
            },
        },
        {
            "text": "Microsoft and Amazon compete for cloud computing market share",
            "metadata": {
                "tickers": ["MSFT", "AMZN"],
                "title": "Cloud Wars: Microsoft vs Amazon",
                "publisher": "Bloomberg",
                "link": "https://example.com/cloud1",
                "publish_date": datetime(2024, 10, 3),
            },
        },
        {
            "text": "Ford announces partnership with electric vehicle charging network",
            "metadata": {
                "tickers": ["F"],
                "title": "Ford Partners on EV Infrastructure",
                "publisher": "Wall Street Journal",
                "link": "https://example.com/ford1",
                "publish_date": datetime(2024, 10, 4),
            },
        },
        {
            "text": "NVIDIA reports strong demand for AI chips and data center GPUs",
            "metadata": {
                "tickers": ["NVDA"],
                "title": "NVIDIA AI Chip Sales Surge",
                "publisher": "TechCrunch",
                "link": "https://example.com/nvda1",
                "publish_date": datetime(2024, 10, 5),
            },
        },
    ]


@pytest.fixture
def populated_bm25_store(mock_news_articles):
    """BM25DocumentStore pre-populated with test articles."""
    store = BM25DocumentStore(verbose=False)

    texts = [article["text"] for article in mock_news_articles]
    metadata_list = [article["metadata"] for article in mock_news_articles]

    store.add_documents(texts, metadata_list)

    return store


@pytest.fixture
def populated_embedding_store(mock_news_articles):
    """EmbeddingDocumentStore pre-populated with test articles."""
    store = EmbeddingDocumentStore(verbose=False)

    texts = [article["text"] for article in mock_news_articles]
    metadata_list = [article["metadata"] for article in mock_news_articles]

    store.add_documents(texts, metadata_list)

    return store
