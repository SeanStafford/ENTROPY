># ENTROPY Generation Context

Multi-agent orchestration system with intelligent specialist routing and predictive pre-fetching.

## Architecture Overview

### Core Pattern: Handoff Orchestration with Selective Concurrency

The generation context implements a sophisticated agent architecture:

1. **Generalist Agent** (front-facing)
   - Full conversation context with prompt caching
   - Direct RAG capabilities (hybrid retrieval)
   - Basic market data tools
   - Handles 80-90% of queries independently

2. **Specialist Agents** (on-demand)
   - **Market Data Specialist**: Technical analysis, indicators, comparisons
   - **News Specialist**: Deep news retrieval and narrative synthesis
   - Minimal context (2-3 turn window)
   - Expensive models justified by focused context

3. **Multi-Process Execution**
   - `ProcessPoolExecutor` for true parallelism
   - Background pre-fetching for instant follow-ups
   - Cached results with TTL

## Key Features

### ✅ Cost Optimization

**Generalist Queries** (80-90% of traffic):
- Model: Claude Sonnet 4.5
- Prompt caching: 90% savings on repeated context
- Cost: ~$0.002 per query

**Specialist Invocation** (10-20% of traffic):
- Model: Claude Opus 4 (market data) or Sonnet 4.5 (news)
- Minimal context: No caching needed
- Cost: $0.015-0.030 per invocation
- **Only triggered when**: Technical jargon, explicit depth request, or user dissatisfaction

### ✅ Intelligent Routing

**Specialist Invocation Triggers**:
1. Technical jargon detected (`RSI`, `MACD`, `golden cross`, etc.)
2. Explicit depth request (`detailed analysis`, `comprehensive report`)
3. User dissatisfaction (`not enough detail`, `tell me more`, `why?`)
4. Power user analytical query (>10 queries in session)

**Conservative Pre-fetching** (only when >80% confidence):
- "What moved X?" queries with brief responses → 85% chance of "why?" follow-up
- Established user pattern of asking follow-ups
- Power users asking about news with brief responses

### ✅ Predictive Intelligence

The system anticipates user needs:

```
User: "What moved AAPL today?"
└─ Generalist: "AAPL up 2.3% to $258.02"
   └─ Background: Pre-fetch News Specialist (85% chance user asks "why?")

[30 seconds later]
User: "Why did it move?"
└─ Generalist: Instant response using cached specialist report
```

## File Structure

```
entropy/contexts/generation/
├── __init__.py                 # Public exports
├── llm_client.py               # Anthropic API wrapper with caching
├── prompts.py                  # System prompts for each agent
├── agents.py                   # Agent implementations
├── decision_logic.py           # Specialist invocation logic
├── orchestrator.py             # Main orchestrator + specialist pool
├── context_manager.py          # Context windowing and sessions
├── tools.py                    # Market data and retrieval wrappers
├── demo.py                     # Demonstration script
└── README.md                   # This file
```

## Usage

### Basic Usage

```python
from entropy.contexts.generation import Orchestrator

# Initialize
orchestrator = Orchestrator(max_workers=4)

# Process query
result = await orchestrator.process_query(
    query="What's AAPL's current price?",
    session_id="user123"
)

print(result['response'])
print(f"Cost: ${result['cost_usd']:.4f}")
print(f"Agent: {result['agent']}")
```

### Response Format

```python
{
    'response': "AAPL is trading at $258.02...",
    'cost_usd': 0.0023,
    'agent': 'generalist',  # or 'generalist+market_data'
    'prefetch_active': False,
    'session_id': 'user123'
}
```

### With Specialist

```python
# Technical query triggers specialist
result = await orchestrator.process_query(
    query="Show me AAPL's RSI and MACD indicators",
    session_id="user123"
)

# Response includes specialist breakdown
{
    'response': "AAPL's RSI is at 58...",
    'cost_usd': 0.0247,
    'agent': 'generalist+market_data',
    'specialist_cost': 0.0225,
    'synthesis_cost': 0.0022,
    'session_id': 'user123'
}
```

## Agent Details

### Generalist Agent

**Model**: Claude Sonnet 4.5
**Temperature**: 0.4
**Context**: Full conversation history with caching

**Capabilities**:
- Hybrid retrieval (BM25 + embeddings) for news
- Basic market data tools (price, fundamentals, history)
- Intent classification and routing
- Response synthesis

**Tools Available**:
- `search_news(query, k, tickers)` - Hybrid news retrieval
- `get_price(ticker)` - Current price data
- `get_fundamentals(ticker)` - Company fundamentals

### Market Data Specialist

**Model**: Claude Opus 4
**Temperature**: 0.1 (deterministic)
**Context**: 2-3 turn rolling window

**Tools Available**:
- All core market data tools (price, fundamentals, history, changes)
- Analytics tools (compare_performance, find_top_performers, calculate_returns)
- Technical indicators (SMA, EMA, RSI, MACD, golden cross detection)

**Invoked When**:
- Query contains technical jargon (`RSI`, `MACD`, `moving average`)
- User requests detailed technical analysis
- Cross-stock analytical comparisons

### News Specialist

**Model**: Claude Sonnet 4.5
**Temperature**: 0.6 (creative synthesis)
**Context**: 2-3 turn rolling window

**Tools Available**:
- Hybrid retrieval with advanced filtering
- Multi-document synthesis
- Sentiment analysis

**Invoked When**:
- User requests comprehensive news analysis
- Deep narrative synthesis needed
- User dissatisfied with generalist news summary

## Decision Logic Details

### Specialist Invocation Decision Tree

```
Query arrives
    ↓
Contains technical jargon (RSI, MACD, etc.)?
├─ YES → Invoke Market Data Specialist immediately
└─ NO
    ↓
Follow-up expressing dissatisfaction?
├─ YES → Invoke appropriate specialist (context-dependent)
└─ NO
    ↓
Power user (10+ queries) with analytical query?
├─ YES → Invoke Market Data Specialist
└─ NO
    ↓
Generalist handles alone (DEFAULT)
```

### Pre-fetch Decision Tree

```
Generalist answered query
    ↓
"What moved X?" with brief response?
├─ YES → Pre-fetch News Specialist (85% confidence)
└─ NO
    ↓
User has follow-up pattern (last 2 queries were follow-ups)?
├─ YES → Pre-fetch Market Data Specialist (80% confidence)
└─ NO
    ↓
Power user news query with brief response?
├─ YES → Pre-fetch News Specialist (80% confidence)
└─ NO → Don't pre-fetch (DEFAULT)
```

## Multi-Process Architecture

### Specialist Pool

Uses `concurrent.futures.ProcessPoolExecutor` for true parallelism:

```python
class SpecialistPool:
    def __init__(self, max_workers: int = 4):
        self.executor = ProcessPoolExecutor(max_workers=max_workers)
        self.cache = {}  # Results cache with TTL

    def submit_task(self, specialist_type, context, task, session_id):
        """Submit task to worker (non-blocking)."""
        future = self.executor.submit(
            run_specialist_worker,
            specialist_type=specialist_type,
            minimal_context=context[-6:],  # Last 3 turns
            task=task
        )
        # Cache future for retrieval
        return future

    def get_result(self, specialist_type, task, session_id, timeout=0.1):
        """Retrieve result if available (non-blocking)."""
        # Check cache, return None if not ready
        ...
```

### Worker Function

Runs in separate process:

```python
def run_specialist_worker(specialist_type, minimal_context, task):
    """Worker executing in separate process."""
    from entropy.contexts.generation.agents import AgentFactory

    # Create specialist
    if specialist_type == 'market_data':
        agent = AgentFactory.create_market_specialist()
    elif specialist_type == 'news':
        agent = AgentFactory.create_news_specialist()

    # Execute task with minimal context
    result = agent.execute_task(minimal_context, task)

    return {
        'specialist_type': specialist_type,
        'content': result['content'],
        'cost_usd': result['cost_usd'],
    }
```

## Context Management Strategy

### Generalist (Full Context with Caching)

```python
messages = [
    {
        "role": "system",
        "content": GENERALIST_SYSTEM_PROMPT,
        "cache_control": {"type": "ephemeral"}  # 5min cache
    },
    *conversation_history,  # ALL previous turns
    {"role": "user", "content": current_query}
]
```

**Cost Optimization**:
- First query: System prompt cached ($0.003)
- Subsequent queries: 90% savings on cached prompt ($0.0003)
- Caching pays for itself after 2-3 queries

### Specialist (Minimal Context, No Cache)

```python
messages = [
    {
        "role": "system",
        "content": SPECIALIST_SYSTEM_PROMPT
        # NO cache_control
    },
    {
        "role": "user",
        "content": f"""Recent context (last 2-3 turns):
{recent_context_summary}

Task: {specific_task}

Execute using your tools."""
    }
]
```

**Cost Optimization**:
- No caching overhead (single-use tasks)
- Minimal context reduces input tokens
- Justifies expensive model (Opus) through focused use

## Cost Analysis

### Example: 100 Queries

**Breakdown**:
- 80 simple queries (generalist only): 80 × $0.002 = $0.160
- 15 specialist invocations: 15 × $0.025 = $0.375
- 5 pre-fetches: 5 × $0.020 = $0.100

**Total**: $0.635 for 100 queries ($0.00635 per query average)

**vs. Naive Approach** (specialist for everything):
- 100 × $0.025 = $2.50 (**4x more expensive**)

### Per-Query Cost Estimates

| Query Type | Agent(s) | Cost |
|-----------|----------|------|
| Simple price query | Generalist | $0.002 |
| Basic news query | Generalist | $0.002 |
| Technical analysis | Generalist + Market Data | $0.025 |
| Deep news analysis | Generalist + News | $0.020 |
| Follow-up (cached) | Generalist | $0.002 |

## Session Management

```python
from entropy.contexts.generation import SessionManager

session_mgr = SessionManager()

# Get or create session
session = session_mgr.get_session("user123")

# Access session data
conversation_history = session['conversation_history']
query_count = session['query_count']

# User profile for decision logic
user_profile = session_mgr.get_user_profile("user123")
# Returns: {'query_count': 5, 'session_id': 'user123'}
```

## Running the Demo

```bash
# Set environment variable
export ANTHROPIC_API_KEY="your_key_here"

# Run demo
cd entropy/contexts/generation
python demo.py
```

**Demo Scenarios**:
1. Simple price query (generalist only)
2. Technical analysis (immediate specialist)
3. Pre-fetch pattern (instant follow-up)
4. Dissatisfaction trigger (specialist after feedback)

## Integration with FastAPI

```python
from fastapi import FastAPI
from entropy.contexts.generation import Orchestrator

app = FastAPI()
orchestrator = Orchestrator(max_workers=4)

@app.post("/chat")
async def chat(query: str, session_id: str = "default"):
    result = await orchestrator.process_query(query, session_id)
    return {
        "response": result['response'],
        "cost": result['cost_usd'],
        "agent": result['agent']
    }

@app.on_event("shutdown")
async def shutdown():
    orchestrator.shutdown()
```

## Performance Characteristics

**Latency**:
- Generalist only: ~1-2 seconds
- With specialist (sync): ~3-5 seconds
- Follow-up (cached): ~1-2 seconds

**Throughput**:
- Max workers: 4 concurrent specialists
- Generalist: Can handle many queries (stateless LLM calls)

**Memory**:
- Session data: ~1KB per session
- Specialist cache: ~10KB per cached result
- ProcessPool overhead: ~50MB per worker

## Design Decisions

### Why Not Multi-Conversation (Huddle V2)?

**V2 Issues**:
- ❌ Cross-conversation information asymmetry
- ❌ Added complexity without clear benefits
- ❌ Harder to debug and maintain

**Single-Conversation Benefits**:
- ✅ All agents see same context (no asymmetry)
- ✅ Simpler implementation
- ✅ Sufficient for assignment scope
- ✅ Easy to upgrade later if needed

### Why Minimal Context for Specialists?

**Rationale**:
- Justifies using expensive models (Opus)
- Reduces token costs significantly
- Forces focused, task-oriented responses
- Prevents scope creep and over-delivery

**Comparison**:
- Full context specialist: $0.040 per invocation
- Minimal context specialist: $0.025 per invocation
- **37.5% cost savings** per specialist call

### Why ProcessPoolExecutor (not threads)?

**Rationale**:
- True parallelism (Python GIL bypass)
- Process isolation (specialists can't interfere)
- No microservices complexity (same codebase)
- Built-in future/promise pattern

## Limitations and Future Work

**Current Limitations**:
- No streaming responses (would require async refactor)
- Session data in-memory (would use Redis for production)
- Pre-fetch cache eviction is time-based (could use LRU)
- No inter-specialist communication (not needed for current use cases)

**Future Enhancements**:
- Streaming specialist responses
- Redis-backed session storage
- Adaptive pre-fetch thresholds based on user behavior
- Multi-specialist coordination for complex queries
- Cost tracking and budget management per user

## License

Part of ENTROPY project for Chaos Labs take-home assignment.
