"""Unit tests for evaluation metrics.

Tests Precision@K, Recall@K, NDCG@K, MRR, and aggregation functions.
These metrics validate the BM25 vs Embeddings evaluation methodology.
"""

import pytest
from entropy.evaluation.metrics import (
    precision_at_k,
    recall_at_k,
    dcg_at_k,
    ndcg_at_k,
    mean_reciprocal_rank,
    calculate_all_metrics,
    aggregate_metrics,
)


@pytest.mark.unit
@pytest.mark.metrics
class TestPrecisionAtK:
    """Test precision@K calculation."""

    def test_all_relevant(self):
        """Perfect results - all retrieved documents are relevant."""
        relevance_scores = [2, 2, 2, 1, 1]
        assert precision_at_k(relevance_scores, k=5) == 1.0
        assert precision_at_k(relevance_scores, k=3) == 1.0

    def test_none_relevant(self):
        """All retrieved documents are not relevant."""
        relevance_scores = [0, 0, 0, 0, 0]
        assert precision_at_k(relevance_scores, k=5) == 0.0
        assert precision_at_k(relevance_scores, k=3) == 0.0

    def test_partial_relevant(self):
        """Mix of relevant and non-relevant results."""
        relevance_scores = [2, 0, 1, 0, 2]
        # Top 3: [2, 0, 1] → 2 relevant out of 3 = 0.667
        assert abs(precision_at_k(relevance_scores, k=3) - 0.667) < 0.01
        # Top 5: [2, 0, 1, 0, 2] → 3 relevant out of 5 = 0.6
        assert precision_at_k(relevance_scores, k=5) == 0.6

    def test_k_zero(self):
        """Edge case: k=0 should return 0."""
        relevance_scores = [2, 1, 0]
        assert precision_at_k(relevance_scores, k=0) == 0.0

    def test_empty_list(self):
        """Edge case: empty relevance scores."""
        assert precision_at_k([], k=5) == 0.0


@pytest.mark.unit
@pytest.mark.metrics
class TestRecallAtK:
    """Test recall@K calculation."""

    def test_found_all_relevant(self):
        """Found all relevant documents in top-K."""
        relevance_scores = [2, 2, 2, 0, 0]
        total_relevant = 3
        assert recall_at_k(relevance_scores, k=5, total_relevant=total_relevant) == 1.0

    def test_found_partial_relevant(self):
        """Found some relevant documents, but not all."""
        relevance_scores = [2, 0, 1, 0, 0]
        total_relevant = 5
        # Found 2 out of 5 relevant = 0.4
        assert recall_at_k(relevance_scores, k=5, total_relevant=total_relevant) == 0.4

    def test_zero_total_relevant(self):
        """Edge case: no relevant documents exist."""
        relevance_scores = [0, 0, 0]
        assert recall_at_k(relevance_scores, k=3, total_relevant=0) == 0.0


@pytest.mark.unit
@pytest.mark.metrics
class TestNDCG:
    """Test NDCG@K (Normalized Discounted Cumulative Gain)."""

    def test_perfect_ranking(self):
        """Perfect ranking: most relevant documents first."""
        relevance_scores = [2, 2, 1, 1, 0]
        # This is already ideal order, so NDCG should be 1.0
        assert ndcg_at_k(relevance_scores, k=5) == pytest.approx(1.0, abs=1e-6)

    def test_reverse_ranking(self):
        """Worst ranking: least relevant documents first."""
        relevance_scores = [0, 0, 1, 2, 2]
        # This is reverse order, NDCG should be low
        ndcg = ndcg_at_k(relevance_scores, k=5)
        assert ndcg < 0.7  # Significantly worse than perfect

    def test_all_zeros(self):
        """Edge case: all documents are non-relevant."""
        relevance_scores = [0, 0, 0, 0, 0]
        # No relevant docs → DCG=0, Ideal DCG=0 → NDCG=0
        assert ndcg_at_k(relevance_scores, k=5) == 0.0

    def test_dcg_calculation(self):
        """Test DCG intermediate calculation."""
        relevance_scores = [3, 2, 1, 0, 0]
        dcg = dcg_at_k(relevance_scores, k=3)
        # DCG = 3/log2(2) + 2/log2(3) + 1/log2(4)
        # DCG = 3.0 + 1.262 + 0.5 = 4.762
        assert dcg == pytest.approx(4.762, abs=0.01)


@pytest.mark.unit
@pytest.mark.metrics
class TestMRR:
    """Test Mean Reciprocal Rank."""

    def test_first_position_relevant(self):
        """First result is relevant → MRR = 1.0."""
        relevance_scores = [2, 0, 0, 0, 0]
        assert mean_reciprocal_rank(relevance_scores) == 1.0

    def test_third_position_relevant(self):
        """First relevant document at position 3 → MRR = 1/3."""
        relevance_scores = [0, 0, 2, 0, 0]
        assert mean_reciprocal_rank(relevance_scores) == pytest.approx(1 / 3, abs=1e-6)

    def test_no_relevant(self):
        """No relevant documents → MRR = 0."""
        relevance_scores = [0, 0, 0, 0, 0]
        assert mean_reciprocal_rank(relevance_scores) == 0.0


@pytest.mark.unit
@pytest.mark.metrics
class TestCalculateAllMetrics:
    """Test aggregation of all metrics."""

    def test_calculate_all_metrics(self):
        """Integration test: calculate all metrics at once."""
        relevance_scores = [2, 0, 1, 2, 0]
        total_relevant = 4

        metrics = calculate_all_metrics(relevance_scores, total_relevant, k_values=[3, 5])

        # Verify all expected keys exist
        assert "precision@3" in metrics
        assert "recall@3" in metrics
        assert "ndcg@3" in metrics
        assert "precision@5" in metrics
        assert "recall@5" in metrics
        assert "ndcg@5" in metrics
        assert "mrr" in metrics

        # Verify MRR is correct (first result is relevant → MRR=1.0)
        assert metrics["mrr"] == 1.0

        # Verify precision@5 (3 relevant out of 5)
        assert metrics["precision@5"] == 0.6


@pytest.mark.unit
@pytest.mark.metrics
class TestAggregateMetrics:
    """Test metric aggregation across multiple queries."""

    def test_aggregate_across_queries(self):
        """Average metrics from multiple query results."""
        query_metrics = [
            {"precision@5": 1.0, "recall@5": 0.8, "ndcg@5": 0.95, "mrr": 1.0},
            {"precision@5": 0.6, "recall@5": 0.6, "ndcg@5": 0.70, "mrr": 0.5},
            {"precision@5": 0.8, "recall@5": 0.7, "ndcg@5": 0.85, "mrr": 1.0},
        ]

        aggregated = aggregate_metrics(query_metrics)

        # Verify averages
        assert aggregated["precision@5"] == pytest.approx(0.8, abs=1e-6)  # (1.0+0.6+0.8)/3
        assert aggregated["recall@5"] == pytest.approx(0.7, abs=1e-6)  # (0.8+0.6+0.7)/3
        assert aggregated["ndcg@5"] == pytest.approx(0.833, abs=0.01)  # (0.95+0.70+0.85)/3
        assert aggregated["mrr"] == pytest.approx(0.833, abs=0.01)  # (1.0+0.5+1.0)/3

    def test_aggregate_empty_list(self):
        """Edge case: no query metrics."""
        aggregated = aggregate_metrics([])
        assert aggregated == {}


@pytest.mark.unit
@pytest.mark.metrics
class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_k_larger_than_results(self):
        """k is larger than number of results."""
        relevance_scores = [2, 1]
        total_relevant = 5

        # k=10 but only 2 results exist
        metrics = calculate_all_metrics(relevance_scores, total_relevant, k_values=[10])

        # Should still work (treat missing results as 0 relevance)
        assert metrics["precision@10"] == 0.2  # 2 relevant out of 10 requested
        assert metrics["recall@10"] == 0.4  # Found 2 out of 5 total

    def test_all_metrics_with_zeros(self):
        """All irrelevant results."""
        relevance_scores = [0, 0, 0, 0, 0]
        total_relevant = 5

        metrics = calculate_all_metrics(relevance_scores, total_relevant, k_values=[5])

        assert metrics["precision@5"] == 0.0
        assert metrics["recall@5"] == 0.0
        assert metrics["ndcg@5"] == 0.0
        assert metrics["mrr"] == 0.0
