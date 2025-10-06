"""Conversation context management for agents."""

from typing import List, Dict, Any, Optional
from loguru import logger


class ContextManager:
    """Manages conversation context for different agent types."""

    @staticmethod
    def prepare_generalist_context(conversation_history: List[Dict[str, str]],
                                   system_prompt: str,
                                   enable_caching: bool = True) -> tuple[Optional[str], List[Dict[str, str]]]:
        """Prepare full context for generalist agent."""
        return system_prompt if enable_caching else None, conversation_history

    @staticmethod
    def prepare_specialist_context(conversation_history: List[Dict[str, str]],
                                   system_prompt: str, task: str,
                                   window_size: int = 3) -> tuple[str, List[Dict[str, str]]]:
        """Prepare minimal context for specialist agent."""
        recent_context = ContextManager.get_recent_context(conversation_history, max_turns=window_size)

        specialist_message = {
            "role": "user",
            "content": f"""Recent conversation context:
{recent_context}

---

Your task:
{task}

Execute this task using your available tools and provide a comprehensive response."""
        }

        return system_prompt, [specialist_message]

    @staticmethod
    def get_recent_context(conversation_history: List[Dict[str, str]],
                          max_turns: int = 3) -> str:
        """Extract recent conversation context as formatted string."""
        if not conversation_history:
            return "No prior conversation"

        recent = conversation_history[-(max_turns * 2):]
        context_lines = []
        for msg in recent:
            role = msg.get('role', 'unknown').title()
            content = msg.get('content', '')
            if len(content) > 300:
                content = content[:300] + "..."
            context_lines.append(f"{role}: {content}")

        return '\n'.join(context_lines)

    @staticmethod
    def add_message(conversation_history: List[Dict[str, str]],
                   role: str, content: str) -> List[Dict[str, str]]:
        """Add message to conversation history."""
        conversation_history.append({"role": role, "content": content})
        return conversation_history


class SessionManager:
    """Manages user sessions and conversation state."""

    def __init__(self):
        self.sessions = {}

    def create_session(self, session_id: str) -> Dict[str, Any]:
        """Create new session."""
        session = {
            'id': session_id,
            'conversation_history': [],
            'query_count': 0,
            'specialist_cache': {},
            'created_at': None
        }
        self.sessions[session_id] = session
        logger.debug(f"Created session {session_id}")
        return session

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get existing session or create new one."""
        if session_id not in self.sessions:
            return self.create_session(session_id)
        return self.sessions[session_id]

    def update_session(self, session_id: str,
                      conversation_history: List[Dict[str, str]],
                      increment_query: bool = True) -> None:
        """Update session with new conversation state."""
        session = self.get_session(session_id)
        session['conversation_history'] = conversation_history
        if increment_query:
            session['query_count'] += 1
        logger.debug(f"Updated session {session_id}: {len(conversation_history)} messages, "
                    f"{session['query_count']} queries")

    def get_user_profile(self, session_id: str) -> Dict[str, Any]:
        """Get user profile for decision logic."""
        session = self.get_session(session_id)
        return {'query_count': session['query_count'], 'session_id': session_id}

    def clear_session(self, session_id: str) -> None:
        """Clear session data."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.debug(f"Cleared session {session_id}")
