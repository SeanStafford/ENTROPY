"""IR evaluation metrics: Precision@K, Recall@K, NDCG@K, MRR."""

import math
from typing import List, Dict, Any


def precision_at_k(relevance_scores: List[int], k: int) -> float:
    """Fraction of top-K results that are relevant."""
    if k == 0 or not relevance_scores:
        return 0.0
    return sum(1 for score in relevance_scores[:k] if score > 0) / k


def recall_at_k(relevance_scores: List[int], k: int, total_relevant: int) -> float:
    """Fraction of all relevant documents found in top-K."""
    if total_relevant == 0 or k == 0 or not relevance_scores:
        return 0.0
    return sum(1 for score in relevance_scores[:k] if score > 0) / total_relevant


def dcg_at_k(relevance_scores: List[int], k: int) -> float:
    """DCG: sum(rel_i / log2(i+1)) for i in 1..K."""
    if k == 0 or not relevance_scores:
        return 0.0
    return sum(rel / math.log2(i + 1) for i, rel in enumerate(relevance_scores[:k], 1))


def ndcg_at_k(relevance_scores: List[int], k: int) -> float:
    """Normalized DCG: actual_dcg / ideal_dcg."""
    actual_dcg = dcg_at_k(relevance_scores, k)
    ideal_dcg = dcg_at_k(sorted(relevance_scores, reverse=True), k)
    return actual_dcg / ideal_dcg if ideal_dcg > 0 else 0.0


def mean_reciprocal_rank(relevance_scores: List[int]) -> float:
    """1/rank of first relevant document."""
    for i, rel in enumerate(relevance_scores, 1):
        if rel > 0:
            return 1.0 / i
    return 0.0


def calculate_all_metrics(relevance_scores: List[int], total_relevant: int, k_values: List[int] = [3, 5, 10]) -> Dict[str, Any]:
    """Calculate all information retrieval metrics for given relevance scores."""
    metrics = {"mrr": mean_reciprocal_rank(relevance_scores)}
    for k in k_values:
        metrics[f"precision@{k}"] = precision_at_k(relevance_scores, k)
        metrics[f"recall@{k}"] = recall_at_k(relevance_scores, k, total_relevant)
        metrics[f"ndcg@{k}"] = ndcg_at_k(relevance_scores, k)
    return metrics


def aggregate_metrics(all_query_metrics: List[Dict[str, float]]) -> Dict[str, float]:
    """Average metrics across multiple queries."""
    if not all_query_metrics:
        return {}
    metric_names = list(all_query_metrics[0].keys())
    aggregated = {}
    for metric_name in metric_names:
        values = [m[metric_name] for m in all_query_metrics if metric_name in m]
        aggregated[metric_name] = sum(values) / len(values) if values else 0.0
    return aggregated
