"""
Pydantic schemas for ENTROPY FastAPI endpoints.

Defines request/response models for type-safe API interactions.
"""

from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request schema for /chat endpoint."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User query about stocks",
        example="What is AAPL's current price?"
    )
    session_id: str = Field(
        default="default",
        description="Session identifier for conversation continuity",
        example="user123"
    )
    retrieval_method: Optional[str] = Field(
        default=None,
        description="Override retrieval method (bm25, embeddings, hybrid)",
        example="hybrid"
    )


class ChatResponse(BaseModel):
    """Response schema for /chat endpoint."""

    response: str = Field(
        ...,
        description="Agent's response to the query",
        example="AAPL is trading at $258.02, up 2.3% today."
    )
    cost_usd: float = Field(
        ...,
        description="Cost of this query in USD",
        example=0.0023
    )
    agent: str = Field(
        ...,
        description="Which agent(s) handled the query",
        example="generalist"
    )
    session_id: str = Field(
        ...,
        description="Session identifier used",
        example="user123"
    )
    prefetch_active: bool = Field(
        default=False,
        description="Whether background specialist pre-fetch occurred",
        example=False
    )


class HealthResponse(BaseModel):
    """Response schema for /health endpoint."""

    status: str = Field(
        ...,
        description="Service health status",
        example="ok"
    )
    version: str = Field(
        ...,
        description="ENTROPY version",
        example="0.1.0"
    )


class ErrorResponse(BaseModel):
    """Response schema for error responses."""

    error: str = Field(
        ...,
        description="Error type",
        example="ValidationError"
    )
    detail: str = Field(
        ...,
        description="Error details",
        example="Query must be between 1 and 1000 characters"
    )
