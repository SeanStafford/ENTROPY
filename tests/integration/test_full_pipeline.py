"""
End-to-end integration tests for full query pipeline.

Tests verify that queries flow correctly through all domains:
API → Generation → (Retrieval + Market Data + News Analysis) → Response

These tests trace the complete journey of a user query.
"""

import pytest
from httpx import AsyncClient
import re

from entropy.api.main import app
from entropy.contexts.generation import RetrievalTools, MarketDataTools


@pytest.mark.integration
@pytest.mark.asyncio
class TestDiagnosticEndpoint:
    """Test the diagnostic endpoint shows domain flow."""

    async def test_diagnostic_endpoint_exists(self):
        """Diagnostic endpoint is accessible."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/diagnostic/test query")

        assert response.status_code == 200

    async def test_diagnostic_shows_all_contexts(self):
        """Diagnostic endpoint reveals all domain interactions."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/diagnostic/What is AAPL price?")

        assert response.status_code == 200
        data = response.json()

        # Should have all context traces
        assert "flow_trace" in data
        flow_trace = data["flow_trace"]

        assert "retrieval" in flow_trace
        assert "market_data" in flow_trace
        assert "generation" in flow_trace

    async def test_diagnostic_retrieval_context(self):
        """Diagnostic shows retrieval context activity."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/diagnostic/Tesla news")

        data = response.json()
        retrieval = data["flow_trace"]["retrieval"]

        # Should attempt retrieval
        assert "success" in retrieval

        # If successful, should have results
        if retrieval["success"]:
            assert "num_results" in retrieval
            assert isinstance(retrieval["num_results"], int)

    async def test_diagnostic_market_data_context(self):
        """Diagnostic shows market data context activity."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/diagnostic/AAPL stock price")

        data = response.json()
        market_data = data["flow_trace"]["market_data"]

        # Should attempt ticker extraction
        assert "ticker_extracted" in market_data

        # Should have extracted AAPL
        if market_data["ticker_extracted"]:
            assert market_data["ticker_extracted"] == "AAPL"

    async def test_diagnostic_handles_no_ticker(self):
        """Diagnostic handles queries without tickers."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/diagnostic/general market news")

        data = response.json()
        market_data = data["flow_trace"]["market_data"]

        # Should note no ticker found
        assert market_data["ticker_extracted"] is None or market_data["success"] is False


@pytest.mark.integration
class TestRetrievalPipeline:
    """Test retrieval context in full pipeline."""

    def test_news_retrieval_query(self):
        """Query for news flows through retrieval context."""
        tools = RetrievalTools()

        # Execute news query
        results = tools.search_news("Latest Apple news", k=5)

        # Should get results
        assert isinstance(results, list)

        # Results should have news structure
        if results:
            article = results[0]
            assert "title" in article
            assert "text" in article
            assert "tickers" in article

    def test_ticker_specific_news(self):
        """Ticker-specific queries retrieve relevant articles."""
        tools = RetrievalTools()

        # Query for specific ticker
        results = tools.search_news("TSLA", k=5)

        # Should find Tesla-related articles
        if results:
            # At least one should have TSLA ticker
            has_tsla = any("TSLA" in article["tickers"] for article in results)
            assert has_tsla, "Expected TSLA articles for TSLA query"

    def test_semantic_news_search(self):
        """Semantic queries retrieve conceptually related news."""
        tools = RetrievalTools()

        # Semantic query (no explicit ticker)
        results = tools.search_news("electric vehicle manufacturers", k=5)

        # Should find EV-related articles
        assert len(results) > 0

        # Should find Tesla or Ford (EV manufacturers)
        all_tickers = set()
        for article in results:
            all_tickers.update(article["tickers"])

        ev_manufacturers = {"TSLA", "F", "GM"}
        assert len(all_tickers & ev_manufacturers) > 0, "Expected EV manufacturer tickers"


@pytest.mark.integration
class TestMarketDataPipeline:
    """Test market data context in full pipeline."""

    @pytest.mark.skip(reason="Requires network access - may be flaky")
    def test_price_query_pipeline(self):
        """Price query flows through market data context."""
        tools = MarketDataTools()

        # Execute price query
        result = tools.get_price("AAPL")

        # Should get price data
        if result:  # May be None if yfinance unavailable
            assert "ticker" in result
            assert "current_price" in result
            assert result["ticker"] == "AAPL"

    @pytest.mark.skip(reason="Requires network access - may be flaky")
    def test_fundamentals_query_pipeline(self):
        """Fundamentals query flows through market data context."""
        tools = MarketDataTools()

        # Execute fundamentals query
        result = tools.get_fundamentals("AAPL")

        # Should get fundamental data
        if result:
            assert "ticker" in result
            assert "market_cap" in result
            assert "sector" in result


@pytest.mark.integration
class TestMultiContextQueries:
    """Test queries that use multiple contexts."""

    def test_price_and_news_query(self):
        """Query requiring both market data and news."""
        retrieval_tools = RetrievalTools()
        market_tools = MarketDataTools()

        query = "AAPL stock price and recent news"

        # Should use retrieval context
        news_results = retrieval_tools.search_news(query, k=3)

        # Should use market data context
        price_result = market_tools.get_price("AAPL")

        # Both contexts should provide data
        assert len(news_results) > 0
        # price_result may be None if yfinance unavailable

    def test_comparison_query(self):
        """Comparison query uses multiple contexts."""
        retrieval_tools = RetrievalTools()

        # Comparison query
        query = "Compare AAPL and MSFT"

        # Should retrieve relevant articles
        results = retrieval_tools.search_news(query, k=10)

        # Should find articles about both companies
        all_tickers = set()
        for article in results:
            all_tickers.update(article["tickers"])

        # Should have found at least one of the companies
        assert "AAPL" in all_tickers or "MSFT" in all_tickers


@pytest.mark.integration
class TestQueryTracing:
    """Test query flow tracing through pipeline."""

    def test_retrieval_logging(self, caplog):
        """Retrieval operations are logged."""
        tools = RetrievalTools()

        # Execute retrieval
        tools.search_news("Apple", k=3)

        # Check logs for retrieval activity
        log_messages = [record.message for record in caplog.records]

        # Should have retrieval-related logs
        retrieval_logs = [
            msg for msg in log_messages
            if "retriev" in msg.lower() or "search" in msg.lower()
        ]

        assert len(retrieval_logs) > 0, "Expected retrieval activity in logs"

    def test_market_data_logging(self, caplog):
        """Market data operations are logged."""
        tools = MarketDataTools()

        # Execute market data fetch
        tools.get_price("AAPL")

        # Check logs for market data activity
        log_messages = [record.message for record in caplog.records]

        # Should have market data related logs (or error if yfinance unavailable)
        market_logs = [
            msg for msg in log_messages
            if "market" in msg.lower() or "price" in msg.lower() or "error" in msg.lower()
        ]

        # Either success logs or error logs should exist
        assert len(market_logs) > 0, "Expected market data activity in logs"


@pytest.mark.integration
class TestDataIntegration:
    """Test data from different contexts integrates correctly."""

    def test_retrieval_and_market_data_compatibility(self):
        """Data from retrieval and market data contexts are compatible."""
        retrieval_tools = RetrievalTools()
        market_tools = MarketDataTools()

        # Get data from both contexts
        articles = retrieval_tools.search_news("AAPL", k=3)
        price_data = market_tools.get_price("AAPL")

        # Data should be usable together
        if articles and price_data:
            # Should be able to combine information
            ticker = price_data["ticker"]
            article_tickers = [t for article in articles for t in article["tickers"]]

            # Should reference same company
            assert ticker in article_tickers, "Market data and news should reference same ticker"

    def test_prompt_construction_from_multiple_contexts(self):
        """Can construct LLM prompt from multiple context data."""
        retrieval_tools = RetrievalTools()
        market_tools = MarketDataTools()

        # Get data
        articles = retrieval_tools.search_news("AAPL earnings", k=2)
        price_data = market_tools.get_price("AAPL")

        # Should be able to construct coherent prompt
        prompt_parts = []

        # Add price context
        if price_data:
            prompt_parts.append(f"{price_data['ticker']} price: ${price_data['current_price']}")

        # Add news context
        for article in articles:
            prompt_parts.append(f"News: {article['title']}")

        # Should have constructed non-empty prompt
        if price_data or articles:
            full_prompt = "\n".join(prompt_parts)
            assert len(full_prompt) > 0
            assert "AAPL" in full_prompt or "Apple" in full_prompt


@pytest.mark.integration
class TestEdgeCases:
    """Test edge cases in pipeline flow."""

    def test_query_with_no_results(self):
        """Query with no matches handled gracefully."""
        tools = RetrievalTools()

        # Query unlikely to match anything
        results = tools.search_news("xyz123nonexistentquery456", k=5)

        # Should return empty list, not crash
        assert isinstance(results, list)
        # May or may not be empty depending on corpus

    def test_malformed_ticker(self):
        """Malformed ticker handled gracefully."""
        tools = MarketDataTools()

        # Try various malformed tickers
        result1 = tools.get_price("")
        result2 = tools.get_price("TOOLONGTICKERXYZ")
        result3 = tools.get_price("123")

        # Should return None, not crash
        assert result1 is None
        assert result2 is None
        assert result3 is None

    def test_empty_query(self):
        """Empty query handled gracefully."""
        tools = RetrievalTools()

        # Empty query
        results = tools.search_news("", k=5)

        # Should return list (may be empty)
        assert isinstance(results, list)
