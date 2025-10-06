"""
Standalone test script for LLM judge to avoid dependency issues.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Configure logging to file
load_dotenv()
PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT"))
LOGS_PATH = PROJECT_ROOT / "outs" / "logs"
LOGS_PATH.mkdir(parents=True, exist_ok=True)

log_file = LOGS_PATH / "llm_judge_test.log"

logger.remove()
logger.add(sys.stdout, level="INFO", format="<level>{level: <8}</level> | <level>{message}</level>")
logger.add(log_file, level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}")

logger.info(f"Logging to: {log_file.relative_to(PROJECT_ROOT)}")

# Import after logging setup
from entropy.evaluation.llm_judge import LLMJudge, evaluate_with_llm_judge

# Direct import to avoid __init__.py importing embeddings (which has broken torch dependency)
import importlib.util
spec = importlib.util.spec_from_file_location(
    "bm25_retrieval",
    PROJECT_ROOT / "entropy/contexts/retrieval/bm25_retrieval.py"
)
bm25_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bm25_module)
BM25DocumentStore = bm25_module.BM25DocumentStore

DATA_PATH = Path(os.getenv("DATA_PROCESSED_PATH"))

# Initialize
logger.info("Initializing LLM judge and BM25 retriever...")
judge = LLMJudge(model="gpt-4o-mini")
bm25_store = BM25DocumentStore.load(DATA_PATH / "bm25_store_20stocks.pkl")

# Test queries - 5 diverse examples
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
logger.info("LLM-as-Judge Evaluation: 5 Queries on BM25")
logger.info(f"{'='*70}\n")

# Run evaluation
results = evaluate_with_llm_judge(bm25_store, test_queries, judge, k=5)

# Log results
logger.info(f"\n{'='*70}")
logger.info("RESULTS SUMMARY")
logger.info(f"{'='*70}")
logger.info(f"Total cost: ${results['llm_stats']['total_cost_usd']:.3f}")
logger.info(f"Judgments: {results['llm_stats']['num_judgments']}")
logger.info(f"\nMetrics:")
logger.info(f"  NDCG@5: {results['aggregated_metrics']['ndcg@5']:.3f}")
logger.info(f"  Precision@5: {results['aggregated_metrics']['precision@5']:.3f}")
logger.info(f"  MRR: {results['aggregated_metrics']['mrr']:.3f}")

logger.info(f"\n{'='*70}")
logger.info("DETAILED JUDGMENTS")
logger.info(f"{'='*70}\n")

for qr in results["query_results"]:
    logger.info(f"Query: '{qr['query']}' [{qr['category']}]")
    logger.info(f"Expected tickers: {qr['expected_tickers']}")
    logger.info(f"Metrics: NDCG@5={qr['metrics']['ndcg@5']:.3f}, P@5={qr['metrics']['precision@5']:.3f}")
    logger.info("Documents:")

    for i, j in enumerate(qr["judgments"], 1):
        logger.info(f"  {i}. {j['doc_title'][:70]}...")
        logger.info(f"     Tickers: {j['doc_tickers']} | Score: {j['llm_score']}")
        logger.info(f"     Reasoning: {j['llm_reasoning']}")
    logger.info("")

logger.success(f"\nEvaluation complete! Full details in: {log_file.relative_to(PROJECT_ROOT)}")
