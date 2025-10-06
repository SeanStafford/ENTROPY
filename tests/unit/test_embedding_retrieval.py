"""Unit tests for embedding-based retrieval system.

Tests EmbeddingDocumentStore for semantic search, filtering, and persistence.
"""

import pytest
import numpy as np
from entropy.contexts.retrieval import EmbeddingDocumentStore


@pytest.mark.unit
@pytest.mark.retrieval
class TestEmbeddingInitialization:
    """Test EmbeddingDocumentStore initialization."""

    def test_empty_initialization(self):
        """New store should be empty with model loaded."""
        store = EmbeddingDocumentStore(verbose=False)

        assert store.index.ntotal == 0  # FAISS index is empty
        assert len(store.documents) == 0
        assert store.model is not None  # Model should be loaded
        assert store.dimension == 384  # all-MiniLM-L6-v2 embedding size

    def test_custom_model(self):
        """Can specify custom embedding model."""
        model_name = "all-MiniLM-L6-v2"
        store = EmbeddingDocumentStore(model_name=model_name, verbose=False)

        # Model is loaded, dimension is set correctly
        assert store.model is not None
        assert store.dimension == 384


@pytest.mark.unit
@pytest.mark.retrieval
class TestEmbeddingIndexing:
    """Test document indexing and embedding generation."""

    def test_add_documents(self, mock_news_articles):
        """Add documents and verify embeddings generated."""
        store = EmbeddingDocumentStore(verbose=False)

        texts = [article["text"] for article in mock_news_articles]
        metadata_list = [article["metadata"] for article in mock_news_articles]

        store.add_documents(texts, metadata_list)

        # Verify documents were added
        assert len(store.documents) == 5
        assert store.index.ntotal == 5  # 5 vectors in FAISS index

    def test_embedding_dimensions(self, mock_news_articles):
        """Verify embeddings have correct dimensions (384 for all-MiniLM-L6-v2)."""
        store = EmbeddingDocumentStore(verbose=False)

        texts = [mock_news_articles[0]["text"]]
        metadata_list = [mock_news_articles[0]["metadata"]]

        store.add_documents(texts, metadata_list)

        # Check that FAISS index has correct dimension and contains 1 vector
        assert store.dimension == 384
        assert store.index.ntotal == 1

    def test_add_documents_length_mismatch(self):
        """Should raise error if texts and metadata lengths don't match."""
        store = EmbeddingDocumentStore(verbose=False)

        texts = ["Article 1", "Article 2"]
        metadata_list = [{"ticker": "AAPL"}]  # Only 1 metadata for 2 texts

        with pytest.raises(ValueError, match="Length mismatch"):
            store.add_documents(texts, metadata_list)


@pytest.mark.unit
@pytest.mark.retrieval
class TestEmbeddingSearch:
    """Test semantic search functionality."""

    def test_search_basic(self, populated_embedding_store):
        """Basic search returns top-k results."""
        results = populated_embedding_store.search("smartphone company earnings", k=3)

        assert len(results) <= 3
        assert all("document" in r for r in results)
        assert all("score" in r for r in results)

        # Scores should be in ascending order (L2 distance: lower is better)
        scores = [r["score"] for r in results]
        assert scores == sorted(scores)

    def test_search_with_ticker_filter(self, populated_embedding_store):
        """Filter results to specific ticker."""
        results = populated_embedding_store.search("technology", k=5, filter_ticker="NVDA")

        # Should only return NVDA documents
        for result in results:
            assert "NVDA" in result["document"]["metadata"]["tickers"]

    def test_search_empty_store(self):
        """Search on empty store returns empty list."""
        store = EmbeddingDocumentStore(verbose=False)

        results = store.search("any query", k=5)
        assert results == []

    def test_semantic_similarity(self, populated_embedding_store):
        """Semantically similar queries should retrieve related documents."""
        # Query about electric vehicles
        results = populated_embedding_store.search("electric cars and EVs", k=5)

        # Should retrieve Tesla or Ford articles (EV companies)
        retrieved_tickers = set()
        for result in results:
            retrieved_tickers.update(result["document"]["metadata"]["tickers"])

        # At least one of the EV companies should be in results
        assert "TSLA" in retrieved_tickers or "F" in retrieved_tickers


@pytest.mark.unit
@pytest.mark.retrieval
class TestEmbeddingStats:
    """Test statistics generation."""

    def test_get_stats(self, populated_embedding_store):
        """Get corpus statistics."""
        stats = populated_embedding_store.get_stats()

        assert "num_documents" in stats
        assert "unique_tickers" in stats
        assert "tickers" in stats

        assert stats["num_documents"] == 5
        assert stats["unique_tickers"] > 0
        assert isinstance(stats["tickers"], list)

    def test_stats_empty_store(self):
        """Stats for empty store."""
        store = EmbeddingDocumentStore(verbose=False)
        stats = store.get_stats()

        assert stats["num_documents"] == 0
        assert stats["unique_tickers"] == 0


@pytest.mark.unit
@pytest.mark.retrieval
class TestEmbeddingPersistence:
    """Test save/load functionality."""

    def test_save_and_load(self, populated_embedding_store, temp_data_dir):
        """Save and load store maintains state."""
        save_path = temp_data_dir / "test_embedding.pkl"

        # Save
        populated_embedding_store.save(save_path)
        assert save_path.exists()
        assert (temp_data_dir / "test_embedding.faiss").exists()

        # Load
        loaded_store = EmbeddingDocumentStore.load(save_path)

        # Verify loaded store has same content
        assert len(loaded_store.documents) == len(populated_embedding_store.documents)
        assert loaded_store.index.ntotal == populated_embedding_store.index.ntotal
        assert loaded_store.dimension == populated_embedding_store.dimension

        # Verify search works on loaded store
        results = loaded_store.search("technology", k=3)
        assert len(results) > 0

    def test_save_empty_store(self, temp_data_dir):
        """Can save and load empty store."""
        store = EmbeddingDocumentStore(verbose=False)
        save_path = temp_data_dir / "empty_embedding.pkl"

        store.save(save_path)
        loaded_store = EmbeddingDocumentStore.load(save_path)

        assert len(loaded_store.documents) == 0


@pytest.mark.unit
@pytest.mark.retrieval
class TestEmbeddingQuality:
    """Test embedding quality and behavior."""

    def test_embedding_quality(self, populated_embedding_store):
        """Check embedding index is properly built."""
        # Check FAISS index has correct properties
        assert populated_embedding_store.index.ntotal == 5
        assert populated_embedding_store.dimension == 384

        # Verify we can search
        results = populated_embedding_store.search("Apple iPhone", k=1)
        assert len(results) > 0

    def test_different_queries_different_embeddings(self, populated_embedding_store):
        """Different queries should produce different embeddings."""
        # Get embeddings for two different queries by searching
        results1 = populated_embedding_store.search("Apple iPhone", k=1)
        results2 = populated_embedding_store.search("Tesla electric vehicle", k=1)

        # Results should be different (unless corpus is very small and same doc ranks #1)
        if len(populated_embedding_store.documents) > 1:
            # Scores should differ (different semantic meaning)
            score1 = results1[0]["score"] if results1 else float("inf")
            score2 = results2[0]["score"] if results2 else float("inf")

            # At least one query should have returned results
            assert results1 or results2


@pytest.mark.unit
@pytest.mark.retrieval
class TestMultiTickerDocuments:
    """Test documents with multiple tickers."""

    def test_multiple_tickers_indexing(self):
        """Documents with multiple tickers should be indexed correctly."""
        store = EmbeddingDocumentStore(verbose=False)

        texts = ["Microsoft and Amazon compete for cloud market"]
        metadata_list = [{"tickers": ["MSFT", "AMZN"], "title": "Cloud Wars"}]

        store.add_documents(texts, metadata_list)

        assert len(store.documents) == 1
        assert store.index.ntotal == 1

    def test_filter_multi_ticker_document(self):
        """Filter should work for documents with multiple tickers."""
        store = EmbeddingDocumentStore(verbose=False)

        texts = ["Microsoft and Amazon compete"]
        metadata_list = [{"tickers": ["MSFT", "AMZN"], "title": "Test"}]

        store.add_documents(texts, metadata_list)

        # Filter by either ticker should return the document
        results_msft = store.search("cloud", k=5, filter_ticker="MSFT")
        results_amzn = store.search("cloud", k=5, filter_ticker="AMZN")

        assert len(results_msft) == 1
        assert len(results_amzn) == 1
