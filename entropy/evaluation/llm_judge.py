"""LLM-as-judge for retrieval quality evaluation."""

import os
import json
from typing import List, Dict, Any
from openai import OpenAI
from loguru import logger

from entropy.evaluation.metrics import calculate_all_metrics, aggregate_metrics


class LLMJudge:
    """Judge document relevance using OpenAI LLM."""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        self.client = OpenAI(api_key=api_key)
        logger.debug(f"LLMJudge init: {model}")

    def judge_relevance(self, query: str, doc_title: str, doc_text: str) -> Dict[str, Any]:
        """Judge document relevance: 0 (not), 1 (partial), 2 (highly relevant)."""
        doc_snippet = doc_text[:800] + ("..." if len(doc_text) > 800 else "")

        prompt = f"""You are evaluating retrieval quality for a financial Q&A system.

Query: "{query}"

Document Title: {doc_title}
Document Text:
{doc_snippet}

Rate how well this document answers the query:
- 2 (Highly Relevant): Directly answers the query with specific, useful information
- 1 (Partially Relevant): Related to the query but incomplete, tangential, or only partially helpful
- 0 (Not Relevant): Unrelated to the query or contains no useful information for answering it

Return ONLY valid JSON with no markdown formatting:
{{"score": <0 or 1 or 2>, "reasoning": "<brief 1-sentence explanation>"}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0,
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content.strip())
            cost_usd = (response.usage.prompt_tokens * 0.15 + response.usage.completion_tokens * 0.60) / 1_000_000
            return {"score": result["score"], "reasoning": result["reasoning"], "cost_usd": cost_usd}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from LLM: {e}")
            raise
        except Exception as e:
            logger.error(f"Judgment failed: {e}")
            raise


def evaluate_with_llm_judge(retriever, test_queries: List[Dict[str, Any]], judge: LLMJudge, k: int = 5) -> Dict[str, Any]:
    """Evaluate retriever using LLM judgments."""
    logger.info(f"LLM evaluation: {len(test_queries)} queries")

    query_results = []
    total_cost = 0.0
    total_judgments = 0

    for i, query_data in enumerate(test_queries, 1):
        query = query_data["query"]
        logger.info(f"[{i}/{len(test_queries)}] {query}")

        results = retriever.search(query, k=k)
        llm_scores = []
        judgments = []

        for result in results:
            doc = result["document"]
            judgment = judge.judge_relevance(query, doc["metadata"]["title"], doc["text"])
            llm_scores.append(judgment["score"])
            total_cost += judgment["cost_usd"]
            total_judgments += 1
            judgments.append({
                "doc_title": doc["metadata"]["title"],
                "doc_tickers": doc["metadata"]["tickers"],
                "llm_score": judgment["score"],
                "llm_reasoning": judgment["reasoning"],
            })

        metrics = calculate_all_metrics(llm_scores, len(query_data["expected_tickers"]), k_values=[3, 5, 10])
        query_results.append({
            "query": query,
            "category": query_data["category"],
            "expected_tickers": query_data["expected_tickers"],
            "judgments": judgments,
            "metrics": metrics,
        })

    aggregated = aggregate_metrics([qr["metrics"] for qr in query_results])
    logger.info(f"Complete: {total_judgments} judgments, ${total_cost:.3f}")

    return {
        "query_results": query_results,
        "aggregated_metrics": aggregated,
        "llm_stats": {"total_cost_usd": total_cost, "num_judgments": total_judgments},
    }
