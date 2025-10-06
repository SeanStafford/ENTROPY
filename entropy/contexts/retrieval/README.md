# Retrieval Context

Multi-strategy document retrieval using BM25 (keyword), embeddings (semantic), and hybrid fusion.

## Overview

Three complementary methods for finding relevant financial news:

- **BM25**: Fast keyword matching for ticker symbols
- **Embeddings**: Semantic understanding for concepts
- **Hybrid**: Weighted fusion (recommended for production)

## Components

- **`BM25DocumentStore`** - BM25Okapi keyword retrieval
- **`EmbeddingDocumentStore`** - Semantic search (sentence-transformers + FAISS)
- **`HybridRetriever`** - RRF fusion with 2:1 embeddings:BM25 weighting
- **`YFinanceFetcher`** - News and stock data from yfinance API

## Quick Start

### Keyword Search (BM25)

```python
from entropy.contexts.retrieval import BM25DocumentStore

store = BM25DocumentStore.load("data/processed/bm25_store_20stocks.pkl")
results = store.search("AAPL stock price", k=5)

for r in results:
    print(f"{r['document']['metadata']['title']} (score: {r['score']:.2f})")
```

### Semantic Search (Embeddings)

```python
from entropy.contexts.retrieval import EmbeddingDocumentStore

store = EmbeddingDocumentStore.load("data/processed/embedding_store_20stocks.pkl")
results = store.search("electric vehicle manufacturers", k=5)

for r in results:
    print(f"{r['document']['metadata']['title']}")
```

### Hybrid Search (Recommended)

```python
from entropy.contexts.retrieval import (
    HybridRetriever,
    BM25DocumentStore,
    EmbeddingDocumentStore
)

bm25 = BM25DocumentStore.load("data/processed/bm25_store_20stocks.pkl")
embeddings = EmbeddingDocumentStore.load("data/processed/embedding_store_20stocks.pkl")

hybrid = HybridRetriever(bm25_store=bm25, embedding_store=embeddings)
results = hybrid.search("AAPL stock analysis", k=10)
```

## Performance

| Method | Latency | NDCG@5 | Best For |
|--------|---------|--------|----------|
| BM25 | ~1ms | 0.606 | Ticker symbols, speed |
| Embeddings | ~10ms | 0.979 | Semantic queries, accuracy |
| Hybrid | ~11ms | ~0.98 | Production (best of both) |

## See Also

- **README_internal.md** - Complete API reference and integration examples
- **CONTEXTSCOPE.md** - Architecture boundaries and design philosophy
- **docs/Hybrid_Retrieval_Strategy.md** - Evaluation results and hybrid justification

## License

Part of ENTROPY project for Chaos Labs take-home assignment.
