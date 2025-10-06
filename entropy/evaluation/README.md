# Evaluation Framework

Retrieval quality assessment using IR metrics and LLM-as-judge validation.

## Overview

Testing framework for evaluating retrieval systems:

- **Standard IR Metrics**: Precision@K, Recall@K, NDCG@K, MRR
- **Test Suite**: 15 queries across 8 categories
- **Two Methods**: Heuristic (ticker-matching) and LLM-as-judge

## Components

- **`metrics.py`** - IR metrics implementation
- **`test_queries.py`** - Test query suite with ground truth
- **`llm_judge.py`** - GPT-4o-mini based relevance evaluator
- **`run_evaluation.py`** - Full evaluation orchestration

## Quick Start

### Run Heuristic Evaluation

```bash
python -m entropy.evaluation.run_evaluation
```

Outputs to `outs/evaluation/` as JSON.

### Run LLM-as-Judge Evaluation

```python
from entropy.evaluation.llm_judge import LLMJudge, evaluate_with_llm_judge
from entropy.evaluation.test_queries import get_test_suite
from entropy.contexts.retrieval import EmbeddingDocumentStore

judge = LLMJudge(model="gpt-4o-mini")
store = EmbeddingDocumentStore.load("data/processed/embedding_store_20stocks.pkl")
queries = get_test_suite()[:5]  # First 5 queries

results = evaluate_with_llm_judge(store, queries, judge, k=5)
print(f"NDCG@5: {results['aggregated_metrics']['ndcg@5']:.3f}")
print(f"Cost: ${results['llm_stats']['total_cost_usd']:.3f}")
```

Cost: ~$0.001 for 25 judgments (5 queries × 5 docs).

### Use Metrics Standalone

```python
from entropy.evaluation.metrics import calculate_all_metrics

relevance_scores = [2, 1, 0, 2, 0, 1, 0, 0, 0, 0]  # 0-2 scale
total_relevant = 3

metrics = calculate_all_metrics(relevance_scores, total_relevant, k_values=[3, 5, 10])
print(f"NDCG@5: {metrics['ndcg@5']:.3f}")
```

## Evaluation Methods

### Heuristic (Ticker-Matching)
- ✅ Fast, free, deterministic
- ❌ Judges ticker presence, not content
- **Use**: Comparative analysis, quick iteration

### LLM-as-Judge
- ✅ Content-aware, honest relevance
- ❌ Costs ~$0.001 per 25 judgments, slower
- **Use**: Validation, architecture decisions

## Test Query Categories

- **exact_ticker** (2): "AAPL stock price"
- **semantic_concept** (4): "electric vehicle manufacturers"
- **temporal** (2): "Latest TSLA developments"
- **analytical** (2): "Undervalued healthcare stocks"
- **multi_stock** (2): "Tech stocks performance"
- **exact_company** (1): "Tesla news"
- **ambiguous** (1): "apple"
- **misspelling** (1): "microsft"

## See Also

- **README_internal.md** - Complete API reference and examples
- **SCOPE.md** - Architecture boundaries and responsibilities
- **docs/Hybrid_Retrieval_Strategy.md** - LLM-as-judge findings

## License

Part of ENTROPY project for Chaos Labs take-home assignment.
