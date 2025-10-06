"""ENTROPY FastAPI multi-agent financial intelligence API."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from dotenv import load_dotenv

from entropy.contexts.generation import Orchestrator, MarketDataTools, RetrievalTools
from .schemas import ChatRequest, ChatResponse, HealthResponse, ErrorResponse

# Load environment variables
load_dotenv()

# Global orchestrator instance
orchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """App lifecycle: startup/shutdown."""
    global orchestrator
    logger.info("Starting ENTROPY API")
    max_workers = int(os.getenv("SPECIALIST_MAX_WORKERS", "4"))
    orchestrator = Orchestrator(max_workers=max_workers)
    logger.info(f"Orchestrator: {max_workers} workers")
    yield
    logger.info("Shutting down")
    if orchestrator:
        orchestrator.shutdown()


app = FastAPI(title="ENTROPY", description="Financial Intelligence Multi-Agent System", version="0.1.0", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:*", "http://127.0.0.1:*"],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled: {exc}")
    return JSONResponse(status_code=500, content=ErrorResponse(error=type(exc).__name__, detail=str(exc)).model_dump())


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """Process query through multi-agent system."""
    try:
        logger.info(f"Query: '{request.query[:50]}...' ({request.session_id})")
        result = await orchestrator.process_query(query=request.query, session_id=request.session_id)
        logger.info(f"{result['agent']}: ${result['cost_usd']:.4f}")
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    """Health check."""
    return HealthResponse(status="ok", version="0.1.0")


@app.get("/diagnostic/{query}", tags=["Diagnostic"])
async def diagnostic(query: str):
    """Diagnostic: data flow through retrieval, market data, generation contexts."""
    flow_trace = {}

    try:
        news_results = RetrievalTools().search_news(query, k=3)
        tickers_found = list(set(t for a in news_results for t in a.get("tickers", [])))
        flow_trace["retrieval"] = {
            "success": True, "num_results": len(news_results), "tickers_found": tickers_found,
            "sample_titles": [a.get("title", "")[:50] for a in news_results[:2]]
        }
    except Exception as e:
        flow_trace["retrieval"] = {"success": False, "error": str(e), "error_type": type(e).__name__}

    try:
        ticker = _extract_first_ticker(query)
        if ticker:
            price_result = MarketDataTools().get_price(ticker)
            flow_trace["market_data"] = {
                "success": price_result is not None, "ticker_extracted": ticker,
                "current_price": price_result["current_price"] if price_result else None
            }
        else:
            flow_trace["market_data"] = {"success": False, "ticker_extracted": None, "message": "No ticker found"}
    except Exception as e:
        flow_trace["market_data"] = {"success": False, "error": str(e), "error_type": type(e).__name__}

    try:
        flow_trace["generation"] = {
            "orchestrator_ready": orchestrator is not None,
            "specialist_pool_active": orchestrator and hasattr(orchestrator, 'specialist_pool') and orchestrator.specialist_pool is not None
        }
    except Exception as e:
        flow_trace["generation"] = {"success": False, "error": str(e), "error_type": type(e).__name__}

    return {"query": query, "flow_trace": flow_trace}


def _extract_first_ticker(query: str) -> str | None:
    """Extract ticker from query: $AAPL or AAPL patterns."""
    import re
    for pattern in [r'\$([A-Z]{1,5})\b', r'\b([A-Z]{2,5})\b']:
        match = re.search(pattern, query.upper())
        if match:
            return match.group(1)
    return None


@app.get("/", tags=["Root"])
async def root():
    """API information."""
    return {
        "name": "ENTROPY", "version": "0.1.0",
        "endpoints": {"chat": "/chat (POST)", "health": "/health (GET)", "diagnostic": "/diagnostic/{query} (GET)",
                     "docs": "/docs", "redoc": "/redoc"}
    }
