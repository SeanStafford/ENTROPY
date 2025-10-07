"""BM25 vs Embeddings evaluation script."""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
from loguru import logger

from entropy.contexts.retrieval.bm25_retrieval import BM25DocumentStore
from entropy.contexts.retrieval.embedding_retrieval import EmbeddingDocumentStore
from entropy.evaluation.test_queries import get_test_suite, get_relevance_judgment, get_category_names
from entropy.evaluation.metrics import calculate_all_metrics, aggregate_metrics
from entropy.utils.logging import configure_logging

load_dotenv()
DATA_PATH = Path(os.getenv("DATA_PROCESSED_PATH"))
OUTS_PATH = Path(os.getenv("PROJECT_ROOT")) / "outs" / "evaluation"


def evaluate_retriever(retriever, retriever_name: str, test_queries: List[Dict[str, Any]], k: int = 10) -> Dict[str, Any]:
    """Evaluate retriever on test suite."""
    logger.info(f"{retriever_name}: {len(test_queries)} queries, k={k}")

    query_results = []
    latencies = []

    for i, query_data in enumerate(test_queries, 1):
        query = query_data["query"]
        start_time = time.time()
        try:
            results = retriever.search(query, k=k)
            latency = (time.time() - start_time) * 1000
            latencies.append(latency)
        except Exception as e:
            logger.error(f"Query '{query}' failed: {e}")
            continue

        relevance_scores = [get_relevance_judgment(query_data, result["document"]["metadata"]) for result in results]
        metrics = calculate_all_metrics(relevance_scores, len(query_data["expected_tickers"]), k_values=[3, 5, 10])

        query_results.append({
            "query": query,
            "category": query_data["category"],
            "expected_tickers": query_data["expected_tickers"],
            "num_results": len(results),
            "relevance_scores": relevance_scores,
            "metrics": metrics,
            "latency_ms": latency,
        })

    aggregated = aggregate_metrics([qr["metrics"] for qr in query_results])
    sorted_latencies = sorted(latencies)
    performance = {
        "mean_latency_ms": sum(latencies) / len(latencies) if latencies else 0,
        "p50_latency_ms": sorted_latencies[len(latencies) // 2] if latencies else 0,
        "p95_latency_ms": sorted_latencies[int(len(latencies) * 0.95)] if latencies else 0,
        "p99_latency_ms": sorted_latencies[int(len(latencies) * 0.99)] if latencies else 0,
    }

    logger.info(f"{retriever_name}: P@5={aggregated.get('precision@5', 0):.3f}, NDCG@5={aggregated.get('ndcg@5', 0):.3f}, latency={performance['mean_latency_ms']:.1f}ms")

    return {
        "retriever": retriever_name,
        "results": query_results,
        "aggregated_metrics": aggregated,
        "performance": performance,
    }


def compare_by_category(bm25_results: Dict[str, Any], embedding_results: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Compare BM25 vs Embeddings by query category."""
    comparisons = {}
    for category in get_category_names():
        bm25_cat = [r for r in bm25_results["results"] if r["category"] == category]
        emb_cat = [r for r in embedding_results["results"] if r["category"] == category]
        if bm25_cat and emb_cat:
            comparisons[category] = {
                "bm25": aggregate_metrics([r["metrics"] for r in bm25_cat]),
                "embeddings": aggregate_metrics([r["metrics"] for r in emb_cat]),
                "num_queries": len(bm25_cat),
            }
    return comparisons


def main():
    """Run BM25 vs Embeddings evaluation."""
    configure_logging("evaluation", console_level="INFO")

    logger.info("="*70)
    logger.info("BM25 vs Embeddings Evaluation")
    logger.info("="*70)

    bm25_store = BM25DocumentStore.load(DATA_PATH / "bm25_store_20stocks.pkl")
    embedding_store = EmbeddingDocumentStore.load(DATA_PATH / "embedding_store_20stocks.pkl")
    test_queries = get_test_suite()

    logger.info(f"Loaded: {len(bm25_store.documents)} docs, {len(test_queries)} queries")

    bm25_results = evaluate_retriever(bm25_store, "BM25", test_queries, k=10)
    embedding_results = evaluate_retriever(embedding_store, "Embeddings", test_queries, k=10)

    category_comparison = compare_by_category(bm25_results, embedding_results)
    for category, comp in category_comparison.items():
        logger.info(f"{category}: BM25={comp['bm25'].get('ndcg@5', 0):.3f}, Emb={comp['embeddings'].get('ndcg@5', 0):.3f}")

    OUTS_PATH.mkdir(parents=True, exist_ok=True)
    with open(OUTS_PATH / f"bm25_results_{run_id}.json", "w") as f:
        json.dump(bm25_results, f, indent=2)
    with open(OUTS_PATH / f"embedding_results_{run_id}.json", "w") as f:
        json.dump(embedding_results, f, indent=2)
    with open(OUTS_PATH / f"comparison_{run_id}.json", "w") as f:
        json.dump({
            "bm25": bm25_results["aggregated_metrics"],
            "embeddings": embedding_results["aggregated_metrics"],
            "bm25_performance": bm25_results["performance"],
            "embeddings_performance": embedding_results["performance"],
            "by_category": category_comparison,
        }, f, indent=2)

    logger.success(f"Complete! Results: {OUTS_PATH}/")


if __name__ == "__main__":
    main()
