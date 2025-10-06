"""
Manually test embeddings using saved index (bypass import issues).
"""

import os
import sys
import pickle
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

load_dotenv()
PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT"))
DATA_PATH = Path(os.getenv("DATA_PROCESSED_PATH"))
LOGS_PATH = PROJECT_ROOT / "outs" / "logs"
LOGS_PATH.mkdir(parents=True, exist_ok=True)

log_file = LOGS_PATH / "llm_judge_embeddings_test.log"

logger.remove()
logger.add(sys.stdout, level="INFO", format="<level>{level: <8}</level> | <level>{message}</level>")
logger.add(log_file, level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}")

logger.info(f"Logging to: {log_file.relative_to(PROJECT_ROOT)}")

# Load embeddings store data directly
import faiss

emb_pkl_path = DATA_PATH / "embedding_store_20stocks.pkl"
emb_faiss_path = DATA_PATH / "embedding_store_20stocks.faiss"

logger.info("Loading embedding store data...")
with open(emb_pkl_path, "rb") as f:
    emb_data = pickle.load(f)

documents = emb_data['documents']
index = faiss.read_index(str(emb_faiss_path))

logger.info(f"Loaded {len(documents)} documents")

# Import sentence transformers for encoding queries only
from sentence_transformers import SentenceTransformer
model = SentenceTransformer(emb_data['model_name'])

logger.info(f"Loaded model: {emb_data['model_name']}")

# Manual search function
def search_embeddings(query, k=5):
    query_embedding = np.array(model.encode([query])).astype("float32")
    distances, indices = index.search(query_embedding, k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        results.append({
            'document': documents[idx],
            'score': float(dist)
        })
    return results

# Import LLM judge
from entropy.evaluation.llm_judge import LLMJudge

judge = LLMJudge(model="gpt-4o-mini")

# Test queries
test_queries = [
    {
        "query": "AAPL stock price",
        "category": "exact_ticker",
        "expected_tickers": ["AAPL"],
    },
    {
        "query": "electric vehicle manufacturers",
        "category": "semantic_concept",
        "expected_tickers": ["TSLA", "F"],
    },
    {
        "query": "Latest TSLA developments",
        "category": "temporal",
        "expected_tickers": ["TSLA"],
    },
    {
        "query": "Undervalued healthcare stocks",
        "category": "analytical",
        "expected_tickers": ["JNJ", "UNH"],
    },
    {
        "query": "apple",
        "category": "ambiguous",
        "expected_tickers": ["AAPL"],
    },
]

logger.info(f"\n{'='*70}")
logger.info("LLM-as-Judge Evaluation: 5 Queries on EMBEDDINGS")
logger.info(f"{'='*70}\n")

# Manual evaluation
from entropy.evaluation.metrics import calculate_all_metrics, aggregate_metrics

query_results = []
total_cost = 0.0
total_judgments = 0

for i, query_data in enumerate(test_queries, 1):
    query = query_data["query"]
    logger.info(f"[{i}/{len(test_queries)}] Judging: '{query}'")

    # Search
    results = search_embeddings(query, k=5)

    # Judge each document
    llm_scores = []
    judgments = []

    for result in results:
        doc = result['document']
        doc_text = doc['text']
        doc_meta = doc['metadata']

        judgment = judge.judge_relevance(query, doc_meta['title'], doc_text)

        llm_scores.append(judgment['score'])
        total_cost += judgment['cost_usd']
        total_judgments += 1

        judgments.append({
            'doc_title': doc_meta['title'],
            'doc_tickers': doc_meta['tickers'],
            'llm_score': judgment['score'],
            'llm_reasoning': judgment['reasoning']
        })

    # Calculate metrics
    total_relevant = len(query_data['expected_tickers'])
    metrics = calculate_all_metrics(llm_scores, total_relevant, k_values=[3, 5, 10])

    query_results.append({
        'query': query,
        'category': query_data['category'],
        'expected_tickers': query_data['expected_tickers'],
        'judgments': judgments,
        'metrics': metrics
    })

# Aggregate
all_metrics = [qr['metrics'] for qr in query_results]
aggregated = aggregate_metrics(all_metrics)

# Log results
logger.info(f"\n{'='*70}")
logger.info("RESULTS SUMMARY")
logger.info(f"{'='*70}")
logger.info(f"Total cost: ${total_cost:.3f}")
logger.info(f"Judgments: {total_judgments}")
logger.info(f"\nMetrics:")
logger.info(f"  NDCG@5: {aggregated['ndcg@5']:.3f}")
logger.info(f"  Precision@5: {aggregated['precision@5']:.3f}")
logger.info(f"  MRR: {aggregated['mrr']:.3f}")

logger.info(f"\n{'='*70}")
logger.info("DETAILED JUDGMENTS")
logger.info(f"{'='*70}\n")

for qr in query_results:
    logger.info(f"Query: '{qr['query']}' [{qr['category']}]")
    logger.info(f"Expected tickers: {qr['expected_tickers']}")
    logger.info(f"Metrics: NDCG@5={qr['metrics']['ndcg@5']:.3f}, P@5={qr['metrics']['precision@5']:.3f}")
    logger.info("Documents:")

    for i, j in enumerate(qr['judgments'], 1):
        logger.info(f"  {i}. {j['doc_title'][:70]}...")
        logger.info(f"     Tickers: {j['doc_tickers']} | Score: {j['llm_score']}")
        logger.info(f"     Reasoning: {j['llm_reasoning']}")
    logger.info("")

logger.success(f"\nEvaluation complete! Full details in: {log_file.relative_to(PROJECT_ROOT)}")
