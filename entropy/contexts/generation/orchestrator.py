"""Orchestrator for multi-agent system with specialist pool."""

import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from concurrent.futures import ProcessPoolExecutor, Future
from loguru import logger

from .agents import AgentFactory, GeneralistAgent, MarketDataSpecialist, NewsSpecialist
from .decision_logic import SpecialistInvoker
from .context_manager import SessionManager, ContextManager


class SpecialistPool:
    """Manages specialist agent worker processes."""

    def __init__(self, max_workers: int = 4):
        self.executor = ProcessPoolExecutor(max_workers=max_workers)
        self.cache = {}
        self.cache_ttl = 300
        logger.info(f"Initialized SpecialistPool with {max_workers} workers")

    def submit_task(self, specialist_type: str, context: List[Dict[str, str]],
                   task: str, session_id: str) -> Future:
        """Submit specialist task to worker pool (non-blocking)."""
        task_hash = hashlib.md5(f"{specialist_type}:{task}".encode()).hexdigest()[:8]
        cache_key = f"{session_id}:{specialist_type}:{task_hash}"

        if cache_key in self.cache:
            logger.debug(f"Task already running: {cache_key}")
            return self.cache[cache_key]['future']

        future = self.executor.submit(
            run_specialist_worker,
            specialist_type=specialist_type,
            minimal_context=context[-6:],
            task=task
        )

        self.cache[cache_key] = {'future': future, 'timestamp': time.time(), 'ttl': self.cache_ttl}
        logger.info(f"Submitted {specialist_type} task to pool: {task_hash}")
        return future

    def get_result(self, specialist_type: str, task: str, session_id: str,
                  timeout: float = 0.1) -> Optional[Dict[str, Any]]:
        """Retrieve specialist result if available (non-blocking)."""
        task_hash = hashlib.md5(f"{specialist_type}:{task}".encode()).hexdigest()[:8]
        cache_key = f"{session_id}:{specialist_type}:{task_hash}"

        if cache_key not in self.cache:
            return None

        entry = self.cache[cache_key]

        if time.time() - entry['timestamp'] > entry['ttl']:
            del self.cache[cache_key]
            logger.debug(f"Cache expired: {cache_key}")
            return None

        future = entry['future']
        if future.done():
            try:
                result = future.result(timeout=timeout)
                logger.info(f"Retrieved cached result: {cache_key}")
                return result
            except Exception as e:
                logger.error(f"Error retrieving result: {e}")
                del self.cache[cache_key]
                return None
        return None

    def shutdown(self, wait: bool = True):
        """Shutdown worker pool."""
        self.executor.shutdown(wait=wait)
        logger.info("SpecialistPool shut down")


def run_specialist_worker(specialist_type: str, minimal_context: List[Dict[str, str]],
                         task: str) -> Dict[str, Any]:
    """Worker function executing in separate process."""
    from entropy.contexts.generation.agents import AgentFactory

    try:
        if specialist_type == 'market_data':
            agent = AgentFactory.create_market_specialist()
        elif specialist_type == 'news':
            agent = AgentFactory.create_news_specialist()
        else:
            raise ValueError(f"Unknown specialist type: {specialist_type}")

        result = agent.execute_task(minimal_context, task)

        return {
            'specialist_type': specialist_type,
            'content': result['content'],
            'cost_usd': result['cost_usd'],
            'usage': result['usage'],
        }
    except Exception as e:
        logger.error(f"Specialist worker failed: {e}")
        return {
            'specialist_type': specialist_type,
            'content': f"Error: {str(e)}",
            'cost_usd': 0.0,
            'error': str(e),
        }


class Orchestrator:
    """Main orchestrator for ENTROPY agent system."""

    def __init__(self, max_workers: int = 4):
        self.generalist = AgentFactory.create_generalist()
        self.specialist_pool = SpecialistPool(max_workers=max_workers)
        self.decision_logic = SpecialistInvoker()
        self.session_manager = SessionManager()
        logger.info("Orchestrator initialized")

    async def process_query(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        """Process user query through orchestrated agent system."""
        session = self.session_manager.get_session(session_id)
        conversation_history = session['conversation_history']
        user_profile = self.session_manager.get_user_profile(session_id)

        should_invoke, specialist_type, reason = self.decision_logic.should_invoke_specialist(
            query, conversation_history, user_profile
        )

        if should_invoke:
            logger.info(f"Immediate specialist invocation: {specialist_type} ({reason})")
            return await self._handle_with_specialist(query, specialist_type, session_id, conversation_history)

        logger.info("Generalist handling query")
        generalist_result = self.generalist.process_query(query, conversation_history, enable_caching=True)

        should_prefetch, prefetch_type, prefetch_reason = self.decision_logic.should_prefetch_specialist(
            query, generalist_result['content'], conversation_history
        )

        if should_prefetch:
            logger.info(f"Pre-fetching {prefetch_type} specialist ({prefetch_reason})")
            task = self.decision_logic.extract_specialist_task(query, conversation_history, prefetch_type)
            self.specialist_pool.submit_task(prefetch_type, conversation_history, task, session_id)

        updated_history = ContextManager.add_message(conversation_history, "user", query)
        updated_history = ContextManager.add_message(updated_history, "assistant", generalist_result['content'])
        self.session_manager.update_session(session_id, updated_history)

        return {
            'response': generalist_result['content'],
            'cost_usd': generalist_result['cost_usd'],
            'agent': 'generalist',
            'prefetch_active': should_prefetch,
            'session_id': session_id,
        }

    async def _handle_with_specialist(self, query: str, specialist_type: str, session_id: str,
                                     conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Handle query requiring immediate specialist."""
        task = self.decision_logic.extract_specialist_task(query, conversation_history, specialist_type)

        cached_result = self.specialist_pool.get_result(specialist_type, task, session_id, timeout=0.1)

        if cached_result:
            logger.info("Using pre-fetched specialist result")
            specialist_response = cached_result['content']
            specialist_cost = cached_result['cost_usd']
        else:
            logger.info(f"Running {specialist_type} specialist synchronously")
            future = self.specialist_pool.submit_task(specialist_type, conversation_history, task, session_id)
            specialist_result = future.result(timeout=30)
            specialist_response = specialist_result['content']
            specialist_cost = specialist_result['cost_usd']

        synthesis_prompt = f"""The {specialist_type} specialist provided this analysis:

{specialist_response}

Synthesize this into a clear, user-friendly response to the query: "{query}"
"""

        synthesis_history = conversation_history + [{"role": "user", "content": synthesis_prompt}]
        synthesis_result = self.generalist.process_query(synthesis_prompt, synthesis_history, enable_caching=False)

        updated_history = ContextManager.add_message(conversation_history, "user", query)
        updated_history = ContextManager.add_message(updated_history, "assistant", synthesis_result['content'])
        self.session_manager.update_session(session_id, updated_history)

        total_cost = specialist_cost + synthesis_result['cost_usd']

        return {
            'response': synthesis_result['content'],
            'cost_usd': total_cost,
            'agent': f'generalist+{specialist_type}',
            'specialist_cost': specialist_cost,
            'synthesis_cost': synthesis_result['cost_usd'],
            'session_id': session_id,
        }

    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get session statistics."""
        session = self.session_manager.get_session(session_id)
        return {
            'session_id': session_id,
            'query_count': session['query_count'],
            'message_count': len(session['conversation_history']),
        }

    def shutdown(self):
        """Shutdown orchestrator and cleanup resources."""
        self.specialist_pool.shutdown(wait=True)
        logger.info("Orchestrator shut down")
