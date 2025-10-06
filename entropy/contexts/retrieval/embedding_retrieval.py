import os
import pickle
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

load_dotenv()
DATA_PATH = Path(os.getenv("DATA_PROCESSED_PATH"))


class EmbeddingDocumentStore:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dimension = 384  # all-MiniLM-L6-v2 embedding size
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents: List[Dict[str, Any]] = []
        logger.debug(f"Initialized EmbeddingDocumentStore with model {model_name}")

    def add_documents(self, texts: List[str], metadata_list: List[Dict[str, Any]]) -> None:
        if len(texts) != len(metadata_list):
            raise ValueError(f"Length mismatch: {len(texts)} texts vs {len(metadata_list)} metadata")

        logger.info(f"Adding {len(texts)} documents to embedding store")

        embeddings = self.model.encode(texts, show_progress_bar=False)
        self.index.add(np.array(embeddings).astype("float32"))

        for text, metadata in zip(texts, metadata_list):
            self.documents.append({"text": text, "metadata": metadata})

        logger.info(f"Embedding store now contains {len(self.documents)} documents")

    def search(
        self, query: str, k: int = 3, filter_ticker: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        
        if self.index.ntotal == 0:
            logger.warning("Embedding index is empty, returning no results")
            return []

        logger.debug(f"Searching: '{query}' (k={k}, filter={filter_ticker})")

        query_embedding = np.array(self.model.encode([query])).astype("float32")
        distances, indices = self.index.search(query_embedding, k if not filter_ticker else len(self.documents))

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if filter_ticker and self.documents[idx]["metadata"].get("ticker") != filter_ticker:
                continue
            results.append({"document": self.documents[idx], "score": float(dist)})
            if len(results) == k:
                break

        if results:
            logger.info(f"Found {len(results)} results (top score: {results[0]['score']:.4f})")
        else:
            logger.info("Found 0 results")

        return results

    def get_stats(self) -> Dict[str, Any]:
        stats = {"num_documents": len(self.documents)}

        tickers = {doc["metadata"].get("ticker") for doc in self.documents if doc["metadata"].get("ticker")}
        stats["unique_tickers"] = len(tickers)
        stats["tickers"] = sorted(list(tickers))

        return stats

    def save(self, path: Optional[str] = DATA_PATH / "embedding_store.pkl") -> None:
        faiss_path = str(path).replace(".pkl", ".faiss")

        faiss.write_index(self.index, faiss_path)

        save_data = {"documents": self.documents, "model_name": self.model.model_card_data.base_model}

        with open(path, "wb") as f:
            pickle.dump(save_data, f)

        logger.info(f"Saved embedding store to {path} ({len(self.documents)} documents)")

    @classmethod
    def load(cls, path: Optional[str] = DATA_PATH / "embedding_store.pkl") -> "EmbeddingDocumentStore":
        logger.info(f"Loading embedding store from {path}")

        with open(path, "rb") as f:
            save_data = pickle.load(f)

        store = cls(model_name=save_data["model_name"])
        store.documents = save_data["documents"]

        faiss_path = str(path).replace(".pkl", ".faiss")
        store.index = faiss.read_index(faiss_path)

        logger.info(f"Loaded {len(store.documents)} documents")
        return store
