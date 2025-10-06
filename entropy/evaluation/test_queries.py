"""
Test query suite for retrieval evaluation.

Each query has associated ground truth relevance judgments to enable
calculation of Precision@K, Recall@K, NDCG, and MRR metrics.
"""

from typing import List, Dict, Any

# Query categories based on assignment requirements and intent classification

EXACT_MATCHING_QUERIES = [
    {
        "query": "AAPL stock price",
        "category": "exact_ticker",
        "expected_tickers": ["AAPL"],
        "description": "Direct ticker mention - BM25 should excel"
    },
    {
        "query": "NVDA earnings report",
        "category": "exact_ticker",
        "expected_tickers": ["NVDA"],
        "description": "Ticker + specific term"
    },
    {
        "query": "Tesla news",
        "category": "exact_company",
        "expected_tickers": ["TSLA"],
        "description": "Company name (not ticker)"
    },
]

SEMANTIC_QUERIES = [
    {
        "query": "electric vehicle manufacturers",
        "category": "semantic_concept",
        "expected_tickers": ["TSLA", "F"],
        "description": "Semantic concept - embeddings should excel"
    },
    {
        "query": "cloud computing revenue growth",
        "category": "semantic_concept",
        "expected_tickers": ["MSFT", "AMZN", "GOOGL"],
        "description": "Multi-word concept without exact matches"
    },
    {
        "query": "companies with strong earnings",
        "category": "semantic_concept",
        "expected_tickers": ["AAPL", "MSFT", "GOOGL", "NVDA", "META", "AMZN"],  # Tech often reports strong earnings
        "description": "Abstract quality assessment"
    },
    {
        "query": "AI chip makers",
        "category": "semantic_concept",
        "expected_tickers": ["NVDA", "AMZN"],
        "description": "Industry category"
    },
]

MULTI_STOCK_QUERIES = [
    {
        "query": "Compare AAPL and MSFT",
        "category": "multi_stock",
        "expected_tickers": ["AAPL", "MSFT"],
        "description": "Explicit comparison of two stocks"
    },
    {
        "query": "Tech stocks performance",
        "category": "multi_stock",
        "expected_tickers": ["AAPL", "MSFT", "GOOGL", "NVDA", "META", "AMZN"],
        "description": "Sector-wide query"
    },
]

TEMPORAL_QUERIES = [
    {
        "query": "Latest TSLA developments",
        "category": "temporal",
        "expected_tickers": ["TSLA"],
        "description": "Recency-focused query"
    },
    {
        "query": "What happened to META this week",
        "category": "temporal",
        "expected_tickers": ["META"],
        "description": "Time-bounded question"
    },
]

ANALYTICAL_QUERIES = [
    {
        "query": "Undervalued healthcare stocks",
        "category": "analytical",
        "expected_tickers": ["JNJ", "UNH"],
        "description": "Requires domain knowledge + analysis"
    },
    {
        "query": "Energy stocks with growth",
        "category": "analytical",
        "expected_tickers": ["XOM", "CVX"],
        "description": "Sector + qualitative filter"
    },
]

EDGE_CASE_QUERIES = [
    {
        "query": "apple",
        "category": "ambiguous",
        "expected_tickers": ["AAPL"],  # Should resolve to stock, not fruit
        "description": "Ambiguous term"
    },
    {
        "query": "microsft",  # Intentional typo
        "category": "misspelling",
        "expected_tickers": ["MSFT"],
        "description": "Common misspelling - embeddings might handle better"
    },
]

# Combine all queries
ALL_QUERIES = (
    EXACT_MATCHING_QUERIES +
    SEMANTIC_QUERIES +
    MULTI_STOCK_QUERIES +
    TEMPORAL_QUERIES +
    ANALYTICAL_QUERIES +
    EDGE_CASE_QUERIES
)


def get_relevance_judgment(query_data: Dict[str, Any], retrieved_doc_metadata: Dict[str, Any]) -> int:
    """
    Judge relevance of a retrieved document for a given query.

    Args:
        query_data: Query dict with expected_tickers and category
        retrieved_doc_metadata: Metadata from retrieved document

    Returns:
        Relevance score:
        - 2: Highly relevant (exact ticker match)
        - 1: Partially relevant (related ticker or topic)
        - 0: Not relevant

    """
    expected_tickers = set(query_data["expected_tickers"])
    doc_tickers = set(retrieved_doc_metadata.get("tickers", [retrieved_doc_metadata.get("ticker", "")]))

    # Exact ticker match
    if expected_tickers & doc_tickers:  # Intersection
        return 2

    # For semantic/analytical queries, allow related tickers
    if query_data["category"] in ["semantic_concept", "analytical", "multi_stock"]:
        # Could implement more sophisticated relevance here
        # For now, treat as not relevant if no ticker match
        return 0

    return 0


def get_test_suite() -> List[Dict[str, Any]]:
    """Get the full test query suite."""
    return ALL_QUERIES


def get_queries_by_category(category: str) -> List[Dict[str, Any]]:
    """Get queries filtered by category."""
    return [q for q in ALL_QUERIES if q["category"] == category]


def get_category_names() -> List[str]:
    """Get list of all query categories."""
    return list(set(q["category"] for q in ALL_QUERIES))
