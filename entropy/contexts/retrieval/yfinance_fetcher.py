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

        Deduplicates articles that appear for multiple tickers and stores
        all related tickers in metadata.

        Args:
            tickers: List of ticker symbols (e.g., ["AAPL", "TSLA"])

        Returns:
            Tuple of (texts, metadata_list) where:
            - texts: List of formatted article strings (deduplicated)
            - metadata_list: List of metadata dicts with tickers (list), title, publisher, link, published

        """
        # Use dict to deduplicate by article link
        articles_by_link = {}

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
                    link = article.get("canonicalUrl", {}).get("url", "")

                    # Use link as unique key (or title if no link)
                    article_key = link if link else title

                    # Format as text for indexing
                    text = f"{title}\n\n{summary}"

                    if article_key in articles_by_link:
                        # Article already seen - add ticker to existing entry
                        if ticker_symbol not in articles_by_link[article_key]["metadata"]["tickers"]:
                            articles_by_link[article_key]["metadata"]["tickers"].append(ticker_symbol)
                    else:
                        # New article
                        articles_by_link[article_key] = {
                            "text": text,
                            "metadata": {
                                "tickers": [ticker_symbol],  # List of tickers
                                "title": title,
                                "publisher": article.get("provider", {}).get("displayName", "Unknown"),
                                "link": link,
                                "published": entry.get("providerPublishTime", 0),
                            }
                        }

                logger.info(f"Fetched {len(news)} articles for {ticker_symbol}")

            except Exception as e:
                logger.error(f"Error fetching news for {ticker_symbol}: {e}")
                continue

        # Convert dict to lists
        all_texts = [item["text"] for item in articles_by_link.values()]
        all_metadata = [item["metadata"] for item in articles_by_link.values()]

        logger.info(f"Total unique articles fetched: {len(all_texts)}")
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
