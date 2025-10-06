"""LLM client wrapper for Anthropic Claude with prompt caching."""

import os
from typing import List, Dict, Optional, Any
from anthropic import Anthropic
from loguru import logger


class LLMClient:
    """Anthropic Claude API wrapper with prompt caching support."""

    COSTS = {
        "claude-sonnet-4-20250514": {
            "input": 3.0, "output": 15.0,
            "cache_write": 3.75, "cache_read": 0.30,
        },
        "claude-opus-4-20250514": {
            "input": 15.0, "output": 75.0,
            "cache_write": 18.75, "cache_read": 1.50,
        },
    }

    def __init__(self, model: str = "claude-sonnet-4-20250514", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        self.client = Anthropic(api_key=self.api_key)
        logger.debug(f"Initialized LLM client with model {model}")

    def generate(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.4,
        max_tokens: int = 1024,
        system: Optional[str] = None,
        enable_caching: bool = True
    ) -> Dict[str, Any]:
        """Generate response from LLM with optional prompt caching."""
        try:
            if enable_caching and system:
                system = [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]

            response = self.client.messages.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                system=system if system else None
            )

            usage = response.usage
            cost = self._calculate_cost(
                usage.input_tokens,
                usage.output_tokens,
                getattr(usage, 'cache_creation_input_tokens', 0),
                getattr(usage, 'cache_read_input_tokens', 0)
            )

            logger.debug(
                f"LLM: {usage.input_tokens}i+{usage.output_tokens}o tokens, "
                f"cache: {getattr(usage, 'cache_read_input_tokens', 0)}r/"
                f"{getattr(usage, 'cache_creation_input_tokens', 0)}w, ${cost:.4f}"
            )

            return {
                "content": response.content[0].text,
                "usage": {
                    "input_tokens": usage.input_tokens,
                    "output_tokens": usage.output_tokens,
                    "cache_creation_tokens": getattr(usage, 'cache_creation_input_tokens', 0),
                    "cache_read_tokens": getattr(usage, 'cache_read_input_tokens', 0),
                },
                "cost_usd": cost,
                "model": self.model,
            }
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise

    def _calculate_cost(self, input_tokens: int, output_tokens: int,
                       cache_creation_tokens: int, cache_read_tokens: int) -> float:
        """Calculate cost in USD for token usage."""
        costs = self.COSTS.get(self.model, self.COSTS["claude-sonnet-4-20250514"])
        regular_input = input_tokens - cache_read_tokens
        input_cost = (regular_input * costs["input"]) / 1_000_000
        cache_write_cost = (cache_creation_tokens * costs["cache_write"]) / 1_000_000
        cache_read_cost = (cache_read_tokens * costs["cache_read"]) / 1_000_000
        output_cost = (output_tokens * costs["output"]) / 1_000_000
        return input_cost + cache_write_cost + cache_read_cost + output_cost


class ModelFactory:
    """Factory for creating model-specific LLM clients."""

    @staticmethod
    def create_generalist() -> LLMClient:
        return LLMClient(model="claude-sonnet-4-20250514")

    @staticmethod
    def create_market_specialist() -> LLMClient:
        return LLMClient(model="claude-opus-4-20250514")

    @staticmethod
    def create_news_specialist() -> LLMClient:
        return LLMClient(model="claude-sonnet-4-20250514")
