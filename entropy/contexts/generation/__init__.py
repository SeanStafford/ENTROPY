"""
ENTROPY Generation Context - Multi-Agent Orchestration System.

Provides intelligent agent-based response generation with:
- Generalist agent (front-facing, full RAG capabilities)
- Specialist agents (market data, news analysis) with minimal context
- Multi-process execution for parallelism
- Predictive pre-fetching for instant follow-ups
- Conservative specialist invocation for cost optimization

Example usage:
    >>> from entropy.contexts.generation import Orchestrator
    >>> orchestrator = Orchestrator(max_workers=4)
    >>> result = await orchestrator.process_query("What's AAPL's price?", session_id="user123")
    >>> print(result['response'])
"""

# Main orchestrator
from .orchestrator import Orchestrator, SpecialistPool

# Agent classes
from .agents import (
    GeneralistAgent,
    MarketDataSpecialist,
    NewsSpecialist,
    AgentFactory,
)

# LLM client
from .llm_client import LLMClient, ModelFactory

# Decision logic
from .decision_logic import SpecialistInvoker

# Context management
from .context_manager import ContextManager, SessionManager

# Tools
from .tools import MarketDataTools, RetrievalTools

__all__ = [
    # Main entry point
    "Orchestrator",
    "SpecialistPool",

    # Agents
    "GeneralistAgent",
    "MarketDataSpecialist",
    "NewsSpecialist",
    "AgentFactory",

    # Infrastructure
    "LLMClient",
    "ModelFactory",
    "SpecialistInvoker",
    "ContextManager",
    "SessionManager",

    # Tools
    "MarketDataTools",
    "RetrievalTools",
]
