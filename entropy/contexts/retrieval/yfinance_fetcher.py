from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv
from loguru import logger
import yfinance as yf


class YFinanceFetcher:
    """Fetch news articles and stock data from yfinance API."""

    def __init__(self):
        logger.debug("Initialized YFinanceFetcher")

    def fetch_news(self, tickers: List[str]) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Fetch news articles for given ticker symbols.

        Args:
            tickers: List of ticker symbols (e.g., ["AAPL", "TSLA"])

        Returns:
            Tuple of (texts, metadata_list) where:
            - texts: List of formatted article strings
            - metadata_list: List of metadata dicts with ticker, title, publisher, link, published

        """
        all_texts = []
        all_metadata = []

        for ticker_symbol in tickers:
            logger.info(f"Fetching news for {ticker_symbol}")

            try:
                ticker = yf.Ticker(ticker_symbol)
                news = ticker.news

                if not news:
                    logger.warning(f"No news found for {ticker_symbol}")
                    continue

                for entry in news:
                    article = entry.get("content", {})
                    title = article.get("title", "")
                    summary = article.get("summary", "")

                    # Format as text for indexing
                    text = f"{title}\n\n{summary}"

                    metadata = {
                        "ticker": ticker_symbol,
                        "title": title,
                        "publisher": article.get("provider", {}).get("displayName", "Unknown"),
                        "link": article.get("canonicalUrl", {}).get("url", ""),
                        "published": entry.get("providerPublishTime", 0),
                    }

                    all_texts.append(text)
                    all_metadata.append(metadata)

                logger.info(f"Fetched {len(news)} articles for {ticker_symbol}")

            except Exception as e:
                logger.error(f"Error fetching news for {ticker_symbol}: {e}")
                continue

        logger.info(f"Total articles fetched: {len(all_texts)}")
        return all_texts, all_metadata

    def fetch_stock_info(self, tickers: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Fetch basic stock information for given tickers.

        Args:
            tickers: List of ticker symbols

        Returns:
            Dict mapping ticker -> info dict with fields like sector, industry, marketCap, etc.

        """
        stock_info = {}

        info_fields = [
            "sector",
            "industry",
            "marketCap",
            "currentPrice",
            "fiftyTwoWeekHigh",
            "fiftyTwoWeekLow",
            "longBusinessSummary",
        ]

        for ticker_symbol in tickers:
            logger.info(f"Fetching info for {ticker_symbol}")

            try:
                ticker = yf.Ticker(ticker_symbol)
                info = ticker.info

                ticker_info = {"ticker": ticker_symbol}
                for field in info_fields:
                    ticker_info[field] = info.get(field, "N/A")

                stock_info[ticker_symbol] = ticker_info
                logger.debug(f"Fetched info for {ticker_symbol}")

            except Exception as e:
                logger.error(f"Error fetching info for {ticker_symbol}: {e}")
                continue

        return stock_info
