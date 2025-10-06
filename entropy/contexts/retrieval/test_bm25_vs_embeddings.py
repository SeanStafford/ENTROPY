"""
Quick comparison: BM25 vs Embeddings retrieval.

Demonstrates that BM25 excels at exact term matching (ticker symbols)
while embeddings excel at semantic similarity.

Note: Run from project root with: python entropy/contexts/retrieval/test_bm25_vs_embeddings.py
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from entropy.contexts.retrieval.bm25_retrieval import BM25DocumentStore
from entropy.prototype.ingest_documents import SimpleDocumentStore


def create_test_documents():
    """Create sample financial documents for testing."""
    texts = [
        "Apple Inc. announces record iPhone sales in Q4 2024. CEO Tim Cook praised the strong performance.",
        "Tesla reports quarterly earnings beat. Revenue up 25% year-over-year driven by Model 3 sales.",
        "Microsoft Azure cloud revenue grows 30% as enterprise adoption accelerates.",
        "Apple launches new MacBook Pro with M3 chip. Prices start at $1,999.",
        "Tesla stock rallies on delivery numbers. Elon Musk confirms production targets.",
        "Google announces breakthrough in quantum computing research.",
        "NVIDIA unveils new H100 GPU for AI workloads. Data center revenue soars.",
        "Amazon Web Services revenue hits $25B driven by cloud migration.",
    ]

    metadata = [
        {"tickers": ["AAPL"], "title": "Apple Q4 earnings"},
        {"tickers": ["TSLA"], "title": "Tesla earnings beat"},
        {"tickers": ["MSFT"], "title": "Azure growth"},
        {"tickers": ["AAPL"], "title": "MacBook Pro launch"},
        {"tickers": ["TSLA"], "title": "Tesla delivery numbers"},
        {"tickers": ["GOOGL"], "title": "Quantum computing"},
        {"tickers": ["NVDA"], "title": "H100 GPU launch"},
        {"tickers": ["AMZN"], "title": "AWS revenue"},
    ]

    return texts, metadata


def compare_retrievers(query, bm25_store, embedding_store, k=3):
    """Compare BM25 and embedding retrieval results for a query."""
    print(f"\n{'='*70}")
    print(f"Query: '{query}'")
    print(f"{'='*70}\n")

    # BM25 results
    print("BM25 Results (Lexical Matching):")
    print("-" * 70)
    bm25_results = bm25_store.search(query, k=k)

    if not bm25_results:
        print("  No results found")
    else:
        for i, result in enumerate(bm25_results, 1):
            doc = result["document"]
            tickers = ", ".join(doc["metadata"]["tickers"])
            title = doc["metadata"]["title"]
            score = result["score"]
            print(f"{i}. [{tickers}] {title} (score: {score:.2f})")

    # Embedding results
    print("\nEmbedding Results (Semantic Matching):")
    print("-" * 70)
    embedding_results = embedding_store.search(query, k=k)

    if not embedding_results:
        print("  No results found")
    else:
        for i, result in enumerate(embedding_results, 1):
            doc = result["document"]
            tickers = ", ".join(doc["metadata"]["tickers"])
            title = doc["metadata"]["title"]
            score = result["score"]
            print(f"{i}. [{tickers}] {title} (score: {score:.2f})")


def main():
    print("\n" + "="*70)
    print("BM25 vs Embeddings Retrieval Comparison")
    print("="*70)

    # Create test documents
    texts, metadata = create_test_documents()
    print(f"\nCreated {len(texts)} test documents")
    print(f"Tickers: {', '.join(sorted(set(t for m in metadata for t in m['tickers'])))}\n")

    # Initialize both stores
    print("Initializing BM25 store...")
    bm25_store = BM25DocumentStore()
    bm25_store.add_documents(texts, metadata)

    print("Initializing embedding store (this may take a moment)...")
    embedding_store = SimpleDocumentStore(model_name="all-MiniLM-L6-v2")
    embedding_store.add_documents(texts, metadata)

    # Test queries that show BM25 advantages
    print("\n" + "="*70)
    print("TEST 1: Exact ticker symbol matching")
    print("="*70)
    print("Expected: BM25 should excel at exact ticker matches")

    compare_retrievers("NVDA", bm25_store, embedding_store, k=3)
    compare_retrievers("TSLA stock", bm25_store, embedding_store, k=3)

    # Test queries that show embedding advantages
    print("\n" + "="*70)
    print("TEST 2: Semantic similarity")
    print("="*70)
    print("Expected: Embeddings should better understand semantic meaning")

    compare_retrievers(
        "What cloud providers are growing?", bm25_store, embedding_store, k=3
    )
    compare_retrievers(
        "Companies with strong quarterly performance", bm25_store, embedding_store, k=3
    )

    # Test mixed queries
    print("\n" + "="*70)
    print("TEST 3: Mixed queries (lexical + semantic)")
    print("="*70)

    compare_retrievers("Apple product launches", bm25_store, embedding_store, k=3)
    compare_retrievers("GPU for machine learning", bm25_store, embedding_store, k=3)

    print("\n" + "="*70)
    print("Key Insights:")
    print("="*70)
    print("""
1. BM25 Strengths:
   - Exact term matching (ticker symbols: NVDA, AAPL, TSLA)
   - Keyword-based queries (specific company/product names)
   - Fast, no model loading required

2. Embedding Strengths:
   - Semantic understanding (cloud providers, quarterly performance)
   - Conceptual queries without exact keywords
   - Better handling of synonyms and paraphrasing

3. Conclusion:
   - Hybrid approach combining both methods would be optimal
   - Use BM25 for precision on exact terms
   - Use embeddings for recall on semantic concepts
    """)

    print("="*70 + "\n")


if __name__ == "__main__":
    main()
