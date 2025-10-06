import os
import pickle
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
from rank_bm25 import BM25Okapi

load_dotenv()
DATA_PATH = Path(os.getenv("DATA_PROCESSED_PATH"))
LOGS_PATH = Path(os.getenv("LOGS_PATH"))

class BM25DocumentStore:
    def __init__(self, verbose: bool = False):
        self.bm25_index: Optional[BM25Okapi] = None
        self.documents: List[Dict[str, Any]] = []
        self.tokenized_corpus: List[List[str]] = []
        self.verbose = verbose
        logger.debug("Initialized empty BM25DocumentStore")

    def _tokenize(self, text: str) -> List[str]:
        return text.lower().split()

    def add_documents(self, texts: List[str], metadata_list: List[Dict[str, Any]]) -> None:
        if len(texts) != len(metadata_list):
            raise ValueError(f"Length mismatch: {len(texts)} texts vs {len(metadata_list)} metadata")

        if self.verbose:
            logger.info(f"Adding {len(texts)} documents to BM25 store")

        new_tokenized = [self._tokenize(text) for text in texts]
        self.tokenized_corpus.extend(new_tokenized)

        for text, metadata in zip(texts, metadata_list):
            self.documents.append({"text": text, "metadata": metadata})

        logger.debug("Building BM25 index")
        self.bm25_index = BM25Okapi(self.tokenized_corpus)
        logger.info(f"BM25 store now contains {len(self.documents)} documents")

    def search(
        self, query: str, k: int = 3, filter_ticker: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if not self.bm25_index:
            logger.warning("BM25 index is empty, returning no results")
            return []

        logger.debug(f"Searching: '{query}' (k={k}, filter={filter_ticker})")

        tokenized_query = self._tokenize(query)
        scores = self.bm25_index.get_scores(tokenized_query)

        scored_docs = [(score, idx) for idx, score in enumerate(scores)]
        scored_docs.sort(reverse=True, key=lambda x: x[0])

        if filter_ticker:
            logger.debug(f"Filtering to ticker: {filter_ticker}")
            scored_docs = [
                (score, idx)
                for score, idx in scored_docs
                if filter_ticker in self.documents[idx]["metadata"]["tickers"]
            ]

        top_results = scored_docs[:k]
        results = [
            {"document": self.documents[idx], "score": float(score)}
            for score, idx in top_results
        ]

        if results:
            logger.info(f"Found {len(results)} results (top score: {results[0]['score']:.2f})")
        else:
            logger.info("Found 0 results")

        return results

    def get_stats(self) -> Dict[str, Any]:
        stats = {
            "num_documents": len(self.documents),
            "avg_doc_length": (
                sum(len(tokens) for tokens in self.tokenized_corpus) / len(self.tokenized_corpus)
                if self.tokenized_corpus
                else 0
            ),
        }

        tickers = set()
        for doc in self.documents:
            tickers.update(doc["metadata"]["tickers"])

        stats["unique_tickers"] = len(tickers)
        stats["tickers"] = sorted(list(tickers))

        return stats

    def save(self, path: Optional[str] = DATA_PATH / "bm25_store.pkl") -> None:
        save_data = {
            "documents": self.documents,
            "tokenized_corpus": self.tokenized_corpus,
            "bm25_index": self.bm25_index,
        }

        with open(path, "wb") as f:
            pickle.dump(save_data, f)

        logger.info(f"Saved BM25 store to {path} ({len(self.documents)} documents)")

    @classmethod
    def load(cls, path: Optional[str] = DATA_PATH / "bm25_store.pkl") -> "BM25DocumentStore":
        logger.info(f"Loading BM25 store from {path}")
        store = cls()

        with open(path, "rb") as f:
            save_data = pickle.load(f)

        store.documents = save_data["documents"]
        store.tokenized_corpus = save_data["tokenized_corpus"]
        store.bm25_index = save_data["bm25_index"]

        logger.info(f"Loaded {len(store.documents)} documents")
        return store
