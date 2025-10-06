"""
ENTROPY API - FastAPI REST interface.

Exposes the multi-agent orchestration system via HTTP endpoints.
"""

from .main import app
from .schemas import ChatRequest, ChatResponse, HealthResponse, ErrorResponse

__all__ = [
    "app",
    "ChatRequest",
    "ChatResponse",
    "HealthResponse",
    "ErrorResponse",
]
