"""Tool execution wrappers for agents."""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

from entropy.contexts.market_data.tools import (
    get_current_price, get_stock_fundamentals, get_price_history, calculate_price_change,
)
from entropy.contexts.market_data.analytics import (
    compare_performance, find_top_performers, calculate_returns,
)
from entropy.contexts.market_data.signals import (
    calculate_sma, calculate_ema, calculate_rsi, calculate_macd, detect_golden_cross,
)


class MarketDataTools:
    """Wrapper for all market data tools."""

    @staticmethod
    def get_price(ticker: str) -> Optional[Dict[str, Any]]:
        logger.debug(f"[BOUNDARY: Generation→MarketData] Fetching price for ticker: {ticker}")
        result = get_current_price(ticker)
        if result:
            logger.debug(f"[BOUNDARY: MarketData→Generation] Price for {ticker}: ${result.current_price}")
            return {
                "ticker": result.ticker, "current_price": result.current_price,
                "previous_close": result.previous_close, "day_high": result.day_high,
                "day_low": result.day_low, "volume": result.volume,
            }
        logger.debug(f"[BOUNDARY: MarketData→Generation] No price data for {ticker}")
        return None

    @staticmethod
    def get_fundamentals(ticker: str) -> Optional[Dict[str, Any]]:
        result = get_stock_fundamentals(ticker)
        if result:
            return {
                "ticker": result.ticker, "market_cap": result.market_cap,
                "sector": result.sector, "industry": result.industry,
                "fifty_day_avg": result.fifty_day_avg,
                "two_hundred_day_avg": result.two_hundred_day_avg,
                "company_name": result.company_name,
            }
        return None

    @staticmethod
    def get_price_change(ticker: str, period: str = "1d") -> Optional[Dict[str, Any]]:
        result = calculate_price_change(ticker, period)
        if result:
            return {
                "ticker": result.ticker, "current_price": result.current_price,
                "previous_price": result.previous_price,
                "change_amount": result.change_amount,
                "change_percent": result.change_percent, "period": result.period,
            }
        return None

    @staticmethod
    def compare_stocks(tickers: List[str], metric: str = "price_change_percent",
                      period: str = "1d") -> Optional[List[Dict[str, Any]]]:
        result = compare_performance(tickers, metric, period)
        if result:
            return [{"ticker": r.ticker, "value": r.value, "metric": r.metric} for r in result.results]
        return None

    @staticmethod
    def get_top_performers(tickers: List[str], metric: str = "price_change_percent",
                          period: str = "1d", n: int = 5) -> List[Dict[str, Any]]:
        results = find_top_performers(tickers, metric, period, n)
        return [{"ticker": r.ticker, "value": r.value, "metric": r.metric} for r in results]

    @staticmethod
    def get_technical_indicators(ticker: str) -> Dict[str, Any]:
        indicators = {}
        sma_50 = calculate_sma(ticker, window=50)
        if sma_50: indicators["sma_50"] = sma_50.value
        sma_200 = calculate_sma(ticker, window=200)
        if sma_200: indicators["sma_200"] = sma_200.value
        ema_12 = calculate_ema(ticker, window=12)
        if ema_12: indicators["ema_12"] = ema_12.value
        rsi = calculate_rsi(ticker, period=14)
        if rsi: indicators["rsi"] = rsi.value
        macd = calculate_macd(ticker)
        if macd: indicators["macd"] = macd.value
        golden_cross = detect_golden_cross(ticker)
        if golden_cross is not None: indicators["golden_cross"] = golden_cross
        return indicators


class RetrievalTools:
    """Wrapper for news retrieval tools."""

    def __init__(self):
        try:
            from entropy.contexts.retrieval import HybridRetriever
            self.retriever = HybridRetriever()
            logger.debug("Initialized hybrid retriever")
        except Exception as e:
            logger.warning(f"Could not initialize hybrid retriever: {e}")
            self.retriever = None

    def search_news(self, query: str, k: int = 5,
                   tickers: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search news articles using hybrid retrieval."""
        logger.debug(f"[BOUNDARY: Generation→Retrieval] Query: '{query}', k={k}, tickers={tickers}")

        if not self.retriever:
            logger.error("Hybrid retriever not available")
            return []

        try:
            results = self.retriever.search(query, k=k)

            if tickers:
                tickers_upper = [t.upper() for t in tickers]
                filtered = []
                for r in results:
                    doc_tickers = r['document']['metadata'].get('tickers', [])
                    if any(t in tickers_upper for t in doc_tickers):
                        filtered.append(r)
                results = filtered

            articles = []
            for r in results:
                doc = r['document']
                articles.append({
                    "title": doc['metadata'].get('title', 'No title'),
                    "text": doc['text'][:500],
                    "tickers": doc['metadata'].get('tickers', []),
                    "publisher": doc['metadata'].get('publisher', 'Unknown'),
                    "link": doc['metadata'].get('link', ''),
                    "published_date": doc['metadata'].get('providerPublishTime', 'Unknown'),
                    "relevance_score": r.get('score', 0.0),
                })

            logger.debug(f"[BOUNDARY: Retrieval→Generation] Returning {len(articles)} articles")
            return articles
        except Exception as e:
            logger.error(f"[BOUNDARY: Retrieval→Generation] News search failed: {e}")
            return []


class DocumentationTools:
    """Wrapper for ENTROPY documentation retrieval."""

    @staticmethod
    def get_documentation(section: Optional[str] = None) -> str:
        """Retrieve ENTROPY documentation."""
        try:
            project_root = Path(os.getenv("PROJECT_ROOT"))
            readme_path = project_root / "README.md"

            if not readme_path.exists():
                logger.warning(f"README not found at {readme_path}")
                return "Documentation not available"

            with open(readme_path, 'r') as f:
                content = f.read()

            if not section:
                logger.debug("Retrieved full README")
                return content

            section_markers = {
                'setup': ['## Setup', '## Installation', '## Getting Started'],
                'api': ['## API', '## Endpoints', '## Usage'],
                'evaluation': ['## Evaluation', '## Testing', '## Metrics'],
                'architecture': ['## Architecture', '## Design', '## Structure'],
            }

            markers = section_markers.get(section.lower(), [])
            for marker in markers:
                if marker in content:
                    start_idx = content.find(marker)
                    next_section = content.find('\n## ', start_idx + len(marker))
                    if next_section == -1:
                        section_content = content[start_idx:]
                    else:
                        section_content = content[start_idx:next_section]
                    logger.debug(f"Retrieved README section: {section}")
                    return section_content

            logger.warning(f"Section '{section}' not found")
            return f"Section '{section}' not found. Available: setup, api, evaluation, architecture"
        except Exception as e:
            logger.error(f"Failed to retrieve documentation: {e}")
            return f"Error retrieving documentation: {e}"
