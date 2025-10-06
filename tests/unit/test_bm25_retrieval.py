"""Unit tests for BM25 retrieval system.

Tests BM25DocumentStore for indexing, search, filtering, and persistence.
"""

import pytest
import pickle
from entropy.contexts.retrieval import BM25DocumentStore


@pytest.mark.unit
@pytest.mark.retrieval
class TestBM25Initialization:
    """Test BM25DocumentStore initialization."""

    def test_empty_initialization(self):
        """New store should be empty."""
        store = BM25DocumentStore(verbose=False)

        assert store.bm25_index is None
        assert len(store.documents) == 0
        assert len(store.tokenized_corpus) == 0

    def test_verbose_flag(self):
        """Verbose flag should be stored."""
        store = BM25DocumentStore(verbose=True)
        assert store.verbose is True


@pytest.mark.unit
@pytest.mark.retrieval
class TestBM25Indexing:
    """Test document indexing."""

    def test_add_documents(self, mock_news_articles):
        """Add documents and verify indexing."""
        store = BM25DocumentStore(verbose=False)

        texts = [article["text"] for article in mock_news_articles]
        metadata_list = [article["metadata"] for article in mock_news_articles]

        store.add_documents(texts, metadata_list)

        # Verify documents were added
        assert len(store.documents) == 5
        assert len(store.tokenized_corpus) == 5
        assert store.bm25_index is not None

    def test_add_documents_length_mismatch(self):
        """Should raise error if texts and metadata lengths don't match."""
        store = BM25DocumentStore(verbose=False)

        texts = ["Article 1", "Article 2"]
        metadata_list = [{"ticker": "AAPL"}]  # Only 1 metadata for 2 texts

        with pytest.raises(ValueError, match="Length mismatch"):
            store.add_documents(texts, metadata_list)

    def test_ticker_prepending(self, mock_news_articles):
        """Verify tickers are prepended to indexed text."""
        store = BM25DocumentStore(verbose=False)

        texts = [mock_news_articles[0]["text"]]  # AAPL article
        metadata_list = [mock_news_articles[0]["metadata"]]

        store.add_documents(texts, metadata_list)

        # Check that tokenized corpus includes ticker
        assert "aapl" in store.tokenized_corpus[0]


@pytest.mark.unit
@pytest.mark.retrieval
class TestBM25Search:
    """Test search functionality."""

    def test_search_basic(self, populated_bm25_store):
        """Basic search returns top-k results."""
        results = populated_bm25_store.search("Apple iPhone earnings", k=3)

        assert len(results) <= 3
        assert all("document" in r for r in results)
        assert all("score" in r for r in results)

        # Scores should be in descending order
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_search_with_ticker_filter(self, populated_bm25_store):
        """Filter results to specific ticker."""
        results = populated_bm25_store.search("vehicle", k=5, filter_ticker="TSLA")

        # Should only return TSLA documents
        for result in results:
            assert "TSLA" in result["document"]["metadata"]["tickers"]

    def test_search_empty_store(self):
        """Search on empty store returns empty list."""
        store = BM25DocumentStore(verbose=False)

        results = store.search("any query", k=5)
        assert results == []

    def test_search_relevance_ordering(self, populated_bm25_store):
        """Results should be ordered by relevance score (descending)."""
        results = populated_bm25_store.search("electric vehicle Tesla", k=5)

        if len(results) > 1:
            # Verify scores are descending
            for i in range(len(results) - 1):
                assert results[i]["score"] >= results[i + 1]["score"]


@pytest.mark.unit
@pytest.mark.retrieval
class TestBM25Stats:
    """Test statistics generation."""

    def test_get_stats(self, populated_bm25_store):
        """Get corpus statistics."""
        stats = populated_bm25_store.get_stats()

        assert "num_documents" in stats
        assert "avg_doc_length" in stats
        assert "unique_tickers" in stats
        assert "tickers" in stats

        assert stats["num_documents"] == 5
        assert stats["unique_tickers"] > 0
        assert isinstance(stats["tickers"], list)

    def test_stats_empty_store(self):
        """Stats for empty store."""
        store = BM25DocumentStore(verbose=False)
        stats = store.get_stats()

        assert stats["num_documents"] == 0
        assert stats["avg_doc_length"] == 0
        assert stats["unique_tickers"] == 0


@pytest.mark.unit
@pytest.mark.retrieval
class TestBM25Persistence:
    """Test save/load functionality."""

    def test_save_and_load(self, populated_bm25_store, temp_data_dir):
        """Save and load store maintains state."""
        save_path = temp_data_dir / "test_bm25.pkl"

        # Save
        populated_bm25_store.save(save_path)
        assert save_path.exists()

        # Load
        loaded_store = BM25DocumentStore.load(save_path)

        # Verify loaded store has same content
        assert len(loaded_store.documents) == len(populated_bm25_store.documents)
        assert len(loaded_store.tokenized_corpus) == len(populated_bm25_store.tokenized_corpus)

        # Verify search works on loaded store
        results = loaded_store.search("Apple", k=3)
        assert len(results) > 0

    def test_save_empty_store(self, temp_data_dir):
        """Can save and load empty store."""
        store = BM25DocumentStore(verbose=False)
        save_path = temp_data_dir / "empty_bm25.pkl"

        store.save(save_path)
        loaded_store = BM25DocumentStore.load(save_path)

        assert len(loaded_store.documents) == 0


@pytest.mark.unit
@pytest.mark.retrieval
class TestBM25Tokenization:
    """Test tokenization behavior."""

    def test_tokenization_lowercase(self):
        """Tokenization should lowercase text."""
        store = BM25DocumentStore(verbose=False)

        text = "Apple ANNOUNCES New iPhone"
        tokens = store._tokenize(text)

        # All tokens should be lowercase
        assert all(token.islower() for token in tokens)
        assert "apple" in tokens
        assert "announces" in tokens

    def test_tokenization_splitting(self):
        """Tokenization should split on whitespace."""
        store = BM25DocumentStore(verbose=False)

        text = "Apple Inc announces earnings"
        tokens = store._tokenize(text)

        assert len(tokens) == 4
        assert tokens == ["apple", "inc", "announces", "earnings"]


@pytest.mark.unit
@pytest.mark.retrieval
class TestBM25MultiTickerDocuments:
    """Test documents with multiple tickers."""

    def test_multiple_tickers_indexing(self):
        """Documents with multiple tickers should be indexed correctly."""
        store = BM25DocumentStore(verbose=False)

        texts = ["Microsoft and Amazon compete for cloud market"]
        metadata_list = [{"tickers": ["MSFT", "AMZN"], "title": "Cloud Wars"}]

        store.add_documents(texts, metadata_list)

        # Both tickers should be in tokenized corpus
        assert "msft" in store.tokenized_corpus[0]
        assert "amzn" in store.tokenized_corpus[0]

    def test_filter_multi_ticker_document(self):
        """Filter should work for documents with multiple tickers."""
        store = BM25DocumentStore(verbose=False)

        texts = ["Microsoft and Amazon compete"]
        metadata_list = [{"tickers": ["MSFT", "AMZN"], "title": "Test"}]

        store.add_documents(texts, metadata_list)

        # Filter by either ticker should return the document
        results_msft = store.search("cloud", k=5, filter_ticker="MSFT")
        results_amzn = store.search("cloud", k=5, filter_ticker="AMZN")

        assert len(results_msft) == 1
        assert len(results_amzn) == 1
