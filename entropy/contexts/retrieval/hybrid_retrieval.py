"""Hybrid retrieval: BM25 + Embeddings via weighted RRF (2:1 emb:bm25)."""

from typing import List, Dict, Any, Optional
from loguru import logger


class HybridRetriever:
    """Weighted RRF fusion: BM25 (keywords) + Embeddings (semantics)."""

    def __init__(self, bm25_store, embedding_store, emb_weight: float = 2.0, k_rrf: int = 60, verbose: bool = False):
        self.bm25_store = bm25_store
        self.embedding_store = embedding_store
        self.emb_weight = emb_weight
        self.k_rrf = k_rrf
        self.verbose = verbose
        logger.debug(f"HybridRetriever init: emb_weight={emb_weight}, k_rrf={k_rrf}")

    def search(self, query: str, k: int = 10, retrieval_depth: int = 20) -> List[Dict[str, Any]]:
        """Retrieve documents using weighted RRF fusion of BM25 and embeddings."""
        if self.verbose:
            logger.info(f"Hybrid search: '{query}' (k={k}, depth={retrieval_depth})")

        bm25_results = self.bm25_store.search(query, k=retrieval_depth)
        emb_results = self.embedding_store.search(query, k=retrieval_depth)

        rrf_scores = {}
        doc_sources = {}
        all_docs = {}

        for rank, result in enumerate(bm25_results, 1):
            doc_id = hash(result["document"]["text"])
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1.0 / (self.k_rrf + rank)
            doc_sources.setdefault(doc_id, {"bm25_rank": None, "emb_rank": None})["bm25_rank"] = rank
            all_docs[doc_id] = result["document"]

        for rank, result in enumerate(emb_results, 1):
            doc_id = hash(result["document"]["text"])
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + self.emb_weight / (self.k_rrf + rank)
            doc_sources.setdefault(doc_id, {"bm25_rank": None, "emb_rank": None})["emb_rank"] = rank
            all_docs[doc_id] = result["document"]

        ranked = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        results = [
            {
                "document": all_docs[doc_id],
                "rrf_score": float(rrf_score),
                "bm25_rank": doc_sources[doc_id]["bm25_rank"],
                "emb_rank": doc_sources[doc_id]["emb_rank"],
            }
            for doc_id, rrf_score in ranked[:k]
        ]

        if self.verbose and results:
            logger.debug(f"Top: RRF={results[0]['rrf_score']:.3f}, BM25={results[0]['bm25_rank']}, Emb={results[0]['emb_rank']}")

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics from both stores."""
        return {
            "bm25_stats": self.bm25_store.get_stats(),
            "embedding_stats": self.embedding_store.get_stats(),
            "hybrid_config": {"emb_weight": self.emb_weight, "k_rrf": self.k_rrf},
        }
