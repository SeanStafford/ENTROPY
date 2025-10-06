"""
Integration tests for inter-domain communication (Domain Boundaries).

Tests verify that each domain (context) returns expected data structures
and that boundaries between domains work correctly.

Critical for catching DDD integration failures.
"""

import pytest
from typing import Dict, Any

# Import from each context
from entropy.contexts.retrieval import HybridRetriever
from entropy.contexts.generation import MarketDataTools, RetrievalTools
from entropy.contexts.market_data.tools import get_current_price, get_stock_fundamentals


@pytest.mark.integration
class TestRetrievalContextBoundary:
    """Test Retrieval context returns expected contracts."""

    def test_hybrid_retriever_contract(self):
        """HybridRetriever.search() returns expected structure."""
        retriever = HybridRetriever()

        # Execute retrieval
        results = retriever.search("Apple iPhone news", k=3)

        # Contract: Should return list
        assert isinstance(results, list)

        # If results exist, check structure
        if results:
            result = results[0]

            # Contract: Each result has 'document' and 'score'
            assert "document" in result
            assert "score" in result

            # Contract: document has 'text' and 'metadata'
            assert "text" in result["document"]
            assert "metadata" in result["document"]

            # Contract: metadata has 'tickers' (list) and 'title'
            metadata = result["document"]["metadata"]
            assert "tickers" in metadata
            assert isinstance(metadata["tickers"], list)
            assert "title" in metadata

            # Contract: score is numeric
            assert isinstance(result["score"], (int, float))

    def test_retrieval_tools_contract(self):
        """RetrievalTools.search_news() returns expected structure."""
        tools = RetrievalTools()

        # Execute news search
        articles = tools.search_news("Tesla", k=3)

        # Contract: Should return list
        assert isinstance(articles, list)

        # If articles exist, check structure
        if articles:
            article = articles[0]

            # Contract: Each article has expected fields
            required_fields = ["title", "text", "tickers", "publisher", "link"]
            for field in required_fields:
                assert field in article, f"Missing field: {field}"

            # Contract: tickers is a list
            assert isinstance(article["tickers"], list)

            # Contract: text is truncated to 500 chars
            assert len(article["text"]) <= 500

    def test_retrieval_ticker_filtering(self):
        """Retrieval correctly filters by ticker."""
        tools = RetrievalTools()

        # Search for general query
        all_results = tools.search_news("technology", k=10)

        # Filter for specific ticker
        filtered_results = tools.search_news("technology", k=10, tickers=["AAPL"])

        # Contract: Filtered results should be subset
        assert len(filtered_results) <= len(all_results)

        # Contract: All filtered results should contain AAPL
        for article in filtered_results:
            assert "AAPL" in article["tickers"]


@pytest.mark.integration
class TestMarketDataContextBoundary:
    """Test Market Data context returns expected contracts."""

    @pytest.mark.skip(reason="Requires network access to yfinance - may be flaky")
    def test_get_current_price_contract(self):
        """get_current_price() returns expected structure."""
        # Execute price fetch
        result = get_current_price("AAPL")

        if result:  # yfinance might be unavailable
            # Contract: Result has required fields
            assert hasattr(result, "ticker")
            assert hasattr(result, "current_price")
            assert hasattr(result, "previous_close")

            # Contract: ticker matches request
            assert result.ticker == "AAPL"

            # Contract: prices are numeric
            assert isinstance(result.current_price, (int, float))

    @pytest.mark.skip(reason="Requires network access to yfinance - may be flaky")
    def test_get_fundamentals_contract(self):
        """get_stock_fundamentals() returns expected structure."""
        result = get_stock_fundamentals("AAPL")

        if result:  # yfinance might be unavailable
            # Contract: Result has required fields
            assert hasattr(result, "ticker")
            assert hasattr(result, "market_cap")
            assert hasattr(result, "sector")

            # Contract: ticker matches request
            assert result.ticker == "AAPL"

    def test_market_data_tools_contract(self):
        """MarketDataTools methods return expected structures."""
        tools = MarketDataTools()

        # Test get_price
        price_result = tools.get_price("AAPL")

        if price_result:  # May be None if yfinance fails
            # Contract: Returns dict with expected keys
            assert isinstance(price_result, dict)
            assert "ticker" in price_result
            assert "current_price" in price_result


@pytest.mark.integration
class TestGenerationContextBoundary:
    """Test Generation context integrates with other contexts."""

    def test_generation_tools_have_access_to_other_contexts(self):
        """Generation tools can access retrieval and market data."""
        # This tests that the generation context properly imports other contexts

        # Should be able to instantiate tools
        market_tools = MarketDataTools()
        retrieval_tools = RetrievalTools()

        # Should have methods
        assert hasattr(market_tools, "get_price")
        assert hasattr(market_tools, "get_fundamentals")
        assert hasattr(retrieval_tools, "search_news")

    def test_retrieval_tools_initialization(self):
        """RetrievalTools properly initializes hybrid retriever."""
        tools = RetrievalTools()

        # Contract: Should have retriever attribute
        assert hasattr(tools, "retriever")

        # Contract: retriever may be None if initialization failed
        # but attribute should exist
        if tools.retriever:
            # If available, should be HybridRetriever
            from entropy.contexts.retrieval import HybridRetriever
            assert isinstance(tools.retriever, HybridRetriever)


@pytest.mark.integration
class TestTickerExtraction:
    """Test ticker extraction across domains."""

    def test_retrieval_extracts_tickers_from_results(self):
        """Retrieval results contain ticker information."""
        tools = RetrievalTools()

        # Search with ticker-specific query
        results = tools.search_news("AAPL stock price", k=5)

        # Contract: Should find articles
        assert len(results) > 0

        # Contract: At least one result should have AAPL ticker
        has_aapl = any("AAPL" in article["tickers"] for article in results)
        assert has_aapl, "Expected to find AAPL in retrieved articles"

    def test_multi_ticker_extraction(self):
        """Retrieval handles queries with multiple tickers."""
        tools = RetrievalTools()

        # Search for comparison query
        results = tools.search_news("Compare AAPL and MSFT", k=10)

        # Contract: Results should contain both tickers
        all_tickers = set()
        for article in results:
            all_tickers.update(article["tickers"])

        # At least one of the tickers should be found
        assert "AAPL" in all_tickers or "MSFT" in all_tickers


@pytest.mark.integration
class TestErrorPropagation:
    """Test that errors at boundaries are handled gracefully."""

    def test_retrieval_tools_handle_missing_retriever(self):
        """RetrievalTools handles missing retriever gracefully."""
        tools = RetrievalTools()

        # Simulate missing retriever
        tools.retriever = None

        # Should not crash, should return empty list
        results = tools.search_news("test query", k=5)

        # Contract: Returns empty list, not None, not exception
        assert isinstance(results, list)
        assert len(results) == 0

    def test_market_data_tools_handle_invalid_ticker(self):
        """MarketDataTools handles invalid tickers gracefully."""
        tools = MarketDataTools()

        # Try to get price for invalid ticker
        result = tools.get_price("INVALID_TICKER_XYZ")

        # Contract: Should return None, not raise exception
        assert result is None


@pytest.mark.integration
class TestDataFlowIntegration:
    """Test data flows correctly between domains."""

    def test_retrieval_output_usable_by_generation(self):
        """Retrieval output format is usable by generation context."""
        retrieval_tools = RetrievalTools()

        # Get retrieval results
        articles = retrieval_tools.search_news("Apple earnings", k=3)

        # Contract: Generation should be able to extract needed fields
        for article in articles:
            # Should be able to get title and text for prompts
            title = article["title"]
            text = article["text"]
            tickers = article["tickers"]

            assert isinstance(title, str)
            assert isinstance(text, str)
            assert isinstance(tickers, list)

            # Should be able to construct prompt context
            prompt_context = f"{title}: {text}"
            assert len(prompt_context) > 0

    def test_market_data_output_usable_by_generation(self):
        """Market data output format is usable by generation context."""
        market_tools = MarketDataTools()

        # Get market data
        price_data = market_tools.get_price("AAPL")

        if price_data:  # May be None
            # Contract: Should be able to extract price for prompts
            ticker = price_data["ticker"]
            price = price_data["current_price"]

            assert isinstance(ticker, str)
            assert isinstance(price, (int, float))

            # Should be able to construct prompt context
            prompt_context = f"{ticker} is trading at ${price}"
            assert len(prompt_context) > 0
