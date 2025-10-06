# ENTROPY FastAPI Endpoint

Thin HTTP wrapper around the multi-agent orchestration system.

## Quick Start

### Start the Server

```bash
# Option 1: Using the convenience script
./scripts/run_api.sh

# Option 2: Direct uvicorn
uvicorn entropy.api.main:app --reload --port 8000
```

Server will start at: **http://localhost:8000**

## Endpoints

### POST /chat

Process user query through the agent system.

**Request:**
```json
{
  "query": "What is AAPL's current price?",
  "session_id": "user123"
}
```

**Response:**
```json
{
  "response": "AAPL is trading at $258.02, up 2.3% today.",
  "cost_usd": 0.0023,
  "agent": "generalist",
  "session_id": "user123",
  "prefetch_active": false
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What moved TSLA today?",
    "session_id": "demo"
  }'
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

### GET /docs

Interactive Swagger UI documentation.

### GET /redoc

ReDoc API documentation.

## Testing

```bash
# Run the test script
python scripts/test_api.py
```

Tests will verify:
1. Health check
2. Simple query (generalist only)
3. Technical query (specialist invocation)
4. Multi-turn conversation

## Agent Routing

The API automatically routes queries to appropriate agents:

- **Simple queries** → Generalist agent (fast, cached)
  - "What is AAPL's price?"
  - "Tell me about Microsoft"

- **Technical queries** → Market Data Specialist
  - "Show me AAPL's RSI and MACD"
  - "Compare performance of AAPL vs MSFT"

- **Deep news** → News Specialist
  - User explicitly asks for more detail
  - Follow-up questions after brief responses

## Configuration

Set in `.env`:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional
SPECIALIST_MAX_WORKERS=4  # Number of concurrent specialist processes
```

## Architecture

```
HTTP Request
    ↓
FastAPI (/chat endpoint)
    ↓
Orchestrator.process_query()
    ↓
├─ Generalist Agent (80-90% of queries)
└─ Specialist Agents (10-20% of queries)
    ├─ Market Data Specialist
    └─ News Specialist
```

## Files

- `main.py` - FastAPI app with lifecycle management (136 lines)
- `schemas.py` - Pydantic request/response models (90 lines)
- `__init__.py` - Public exports (16 lines)

**Total**: 242 lines exposing 2,258 lines of agent orchestration.

## Development

The API is a **thin wrapper** - all intelligence is in the generation context:
- No business logic in FastAPI layer
- No agent coordination in API layer
- Simple request validation and error translation

This keeps the API layer maintainable and focused on HTTP concerns.
