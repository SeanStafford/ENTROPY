"""Ingest news and data for 20 diverse stocks across sectors."""

import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

from entropy.contexts.retrieval.yfinance_fetcher import YFinanceFetcher
from entropy.contexts.retrieval.bm25_retrieval import BM25DocumentStore
from entropy.contexts.retrieval.embedding_retrieval import EmbeddingDocumentStore
from entropy.utils.logging import configure_logging

load_dotenv()
PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT"))
DATA_PATH = Path(os.getenv("DATA_PROCESSED_PATH"))

TICKERS_20 = [
    "AAPL", "MSFT", "GOOGL", "NVDA", "META", "AMZN",  # Tech
    "JPM", "V", "BRK-B",  # Finance
    "XOM", "CVX",  # Energy
    "JNJ", "UNH",  # Healthcare
    "PG", "KO", "NKE",  # Consumer
    "BA", "GE",  # Industrial
    "TSLA", "F"  # Auto
]

def main():
    """Fetch and index 20 stocks for evaluation."""

    # Configure logging with custom UPDATE level
    ABC = "UPDATE"
    logger.level(ABC, no=21)
    log_file = configure_logging("ingest_20_stocks", console_level=ABC)

    print(f"\nLogs will be saved to: {log_file.relative_to(PROJECT_ROOT)}\n")

    logger.log(ABC, "Ingesting 20 Stocks for Evaluation")
    logger.log(ABC, f"Tickers: {', '.join(TICKERS_20)}")

    # Fetch news
    logger.log(ABC, "Fetching news from yfinance...")
    fetcher = YFinanceFetcher()
    texts, metadata = fetcher.fetch_news(TICKERS_20)

    logger.success(f"Fetched {len(texts)} unique articles!")

    # Show ticker distribution
    ticker_counts = {}
    for meta in metadata:
        for ticker in meta.get("tickers", []):
            ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1

    # Index in BM25
    logger.log(ABC, "Building BM25 index...")
    bm25_store = BM25DocumentStore()
    bm25_store.add_documents(texts, metadata)

    bm25_path = DATA_PATH / "bm25_store_20stocks.pkl"
    bm25_store.save(bm25_path)
    logger.success(f"Built it!")

    # Index in Embeddings
    logger.log(ABC, "Building Embedding index...")
    embedding_store = EmbeddingDocumentStore()
    embedding_store.add_documents(texts, metadata)

    embedding_path = DATA_PATH / "embedding_store_20stocks.pkl"
    embedding_store.save(embedding_path)
    logger.success(f"Built it!")

    logger.success("Ingestion complete!")
    logger.log(ABC, f"BM25 index: {bm25_path}")
    logger.log(ABC, f"Embedding index: {embedding_path}")


if __name__ == "__main__":
    main()
