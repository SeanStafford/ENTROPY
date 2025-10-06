"""Agent implementations for ENTROPY financial intelligence system."""

from typing import Dict, Any, List, Optional
from loguru import logger

from .llm_client import LLMClient, ModelFactory
from .prompts import GENERALIST_SYSTEM_PROMPT, MARKET_DATA_SPECIALIST_PROMPT, NEWS_SPECIALIST_PROMPT
from .tools import MarketDataTools, RetrievalTools, DocumentationTools
from .context_manager import ContextManager


class BaseAgent:
    """Base class for all agents."""

    def __init__(self, name: str, llm_client: LLMClient, system_prompt: str, temperature: float = 0.4):
        self.name = name
        self.client = llm_client
        self.system_prompt = system_prompt
        self.temperature = temperature
        logger.debug(f"Initialized {name} agent")

    def generate(self, messages: List[Dict[str, str]], enable_caching: bool = True) -> Dict[str, Any]:
        """Generate response from LLM."""
        return self.client.generate(
            messages=messages,
            temperature=self.temperature,
            max_tokens=1024,
            system=self.system_prompt,
            enable_caching=enable_caching
        )


class GeneralistAgent(BaseAgent):
    """Primary front-facing agent with full RAG and tool capabilities."""

    def __init__(self):
        super().__init__(
            name="Generalist",
            llm_client=ModelFactory.create_generalist(),
            system_prompt=GENERALIST_SYSTEM_PROMPT,
            temperature=0.4
        )
        self.market_tools = MarketDataTools()
        self.retrieval_tools = RetrievalTools()
        self.doc_tools = DocumentationTools()

    def process_query(self, query: str, conversation_history: List[Dict[str, str]],
                     enable_caching: bool = True) -> Dict[str, Any]:
        """Process user query with full context and tool access."""
        messages = conversation_history + [{"role": "user", "content": query}]
        result = self.generate(messages, enable_caching=enable_caching)
        logger.info(f"Generalist response: {result['content'][:100]}... (cost: ${result['cost_usd']:.4f})")
        return result

    def search_news(self, query: str, k: int = 5, tickers: Optional[List[str]] = None) -> List[Dict]:
        """Search news using hybrid retrieval."""
        return self.retrieval_tools.search_news(query, k=k, tickers=tickers)

    def get_price(self, ticker: str) -> Optional[Dict]:
        """Get current price for ticker."""
        return self.market_tools.get_price(ticker)

    def get_documentation(self, section: Optional[str] = None) -> str:
        """Retrieve ENTROPY documentation."""
        return self.doc_tools.get_documentation(section)


class MarketDataSpecialist(BaseAgent):
    """Specialist for deep quantitative analysis and technical indicators."""

    def __init__(self):
        super().__init__(
            name="MarketDataSpecialist",
            llm_client=ModelFactory.create_market_specialist(),
            system_prompt=MARKET_DATA_SPECIALIST_PROMPT,
            temperature=0.1
        )
        self.tools = MarketDataTools()

    def execute_task(self, minimal_context: List[Dict[str, str]], task: str) -> Dict[str, Any]:
        """Execute market data analysis task."""
        system, messages = ContextManager.prepare_specialist_context(
            conversation_history=minimal_context,
            system_prompt=self.system_prompt,
            task=task,
            window_size=3
        )

        result = self.client.generate(
            messages=messages,
            temperature=self.temperature,
            max_tokens=1536,
            system=system,
            enable_caching=False
        )

        logger.info(f"Market Data Specialist executed: {result['content'][:100]}... (cost: ${result['cost_usd']:.4f})")
        return result


class NewsSpecialist(BaseAgent):
    """Specialist for deep news analysis and narrative synthesis."""

    def __init__(self):
        super().__init__(
            name="NewsSpecialist",
            llm_client=ModelFactory.create_news_specialist(),
            system_prompt=NEWS_SPECIALIST_PROMPT,
            temperature=0.6
        )
        self.retrieval_tools = RetrievalTools()

    def execute_task(self, minimal_context: List[Dict[str, str]], task: str) -> Dict[str, Any]:
        """Execute news analysis task."""
        system, messages = ContextManager.prepare_specialist_context(
            conversation_history=minimal_context,
            system_prompt=self.system_prompt,
            task=task,
            window_size=3
        )

        result = self.client.generate(
            messages=messages,
            temperature=self.temperature,
            max_tokens=1536,
            system=system,
            enable_caching=False
        )

        logger.info(f"News Specialist executed: {result['content'][:100]}... (cost: ${result['cost_usd']:.4f})")
        return result


class AgentFactory:
    """Factory for creating agent instances."""

    @staticmethod
    def create_generalist() -> GeneralistAgent:
        return GeneralistAgent()

    @staticmethod
    def create_market_specialist() -> MarketDataSpecialist:
        return MarketDataSpecialist()

    @staticmethod
    def create_news_specialist() -> NewsSpecialist:
        return NewsSpecialist()
