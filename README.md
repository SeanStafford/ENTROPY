```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ┃
┃ ┃                                                                          ┃ ┃
┃ ┃                                                                          ┃ ┃
┃ ┃    ███████╗ ███╗   ██╗ ████████╗ ██████╗   ██████╗  ██████╗  ██╗   ██╗   ┃ ┃
┃ ┃    ██╔════╝ ████╗  ██║ ╚══██╔══╝ ██╔══██╗ ██╔═══██╗ ██╔══██╗ ╚██╗ ██╔╝   ┃ ┃
┃ ┃    █████╗   ██╔██╗ ██║    ██║    ██████╔╝ ██║   ██║ ██████╔╝  ╚████╔╝    ┃ ┃
┃ ┃    ██╔══╝   ██║╚██╗██║    ██║    ██╔══██╗ ██║   ██║ ██╔═══╝    ╚██╔╝     ┃ ┃
┃ ┃    ███████╗ ██║ ╚████║    ██║    ██║  ██║ ╚██████╔╝ ██║         ██║      ┃ ┃
┃ ┃    ╚══════╝ ╚═╝  ╚═══╝    ╚═╝    ╚═╝  ╚═╝  ╚═════╝  ╚═╝         ╚═╝      ┃ ┃
┃ ┃                                                                          ┃ ┃
┃ ┃    Evaluation of News and Trends:                                        ┃ ┃
┃ ┃    A Retrieval-Optimized Prototype for Yfinance                          ┃ ┃
┃ ┃                                                                          ┃ ┃
┃ ┃                                                                   v0.1.0 ┃ ┃
┃ ┃                                                 created by Sean Stafford ┃ ┃
┃ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│  Production-ready financial intelligence system that answers free-text       │
│  questions about U.S. stocks through multi-agent orchestration and hybrid    │
│  RAG architecture. Demonstrates systematic evaluation, cost optimization,    │
│  and domain-driven design for production LLM applications.                   │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---
> *ENTROPY brings order (structured financial intelligence) to the Chaos (noisy market signals and news).*


## Quick Start

### Installation

```bash
# 1. Create and activate virtual environment
make venv
source .venv/bin/activate

# 2. Install dependencies (venv creation happens automatically if needed)
make install

# For development (includes testing and evaluation tools)
make install-dev
```

**Note**: All `make install*` targets will automatically create the `.venv` directory if it doesn't exist, but you still need to activate it manually with `source .venv/bin/activate` before installation.

### Running the API Server

```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY="your_key_here"

# OpenAI also an option
# export OPENAI_API_KEY="your_key_here"

# Start the server
uvicorn entropy.api.main:app --reload --port 8000

# Or use the convenience script
./scripts/run_api.sh
```

**Test the API:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is AAPL'\''s current price?",
    "session_id": "demo"
  }'
```



## Technical Highlights

- **Domain-Driven Design**: Contexts encapsulate vocabulary and logic with clean boundaries
- **Type-Safe Data Structures**: Pydantic models for all market data and news structures
- **ProcessPoolExecutor**: True parallelism for specialist agents
- **Structured Logging**: Logging with request tracing via Loguru
- **yfinance Resilience**: Error handling, graceful degradation for API failures
- **Prompt Caching**: 90% cost savings on repeated generalist context (Anthropic cache control)
- **Conservative Cost Strategy**: Specialist invocation only when necessary, >80% confidence for pre-fetching
- **Minimal Specialist Context**: 2-3 turn window reduces tokens and enables expensive models


## Architecture

ENTROPY follows domain-driven design principles, organizing code around financial analysis contexts rather than technical layers:

### Domain Contexts

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Market Data    │     │ News Analysis   │     │   Retrieval     │
│                 │     │                 │     │                 │
│ • Price data    │     │ • Sentiment     │     │ • BM25          │
│ • Fundamentals  │     │ • Timeline      │     │ • Embeddings    │
│ • Technicals    │     │ • Aggregates    │     │ • Hybrid RRF    │
│ • Analytics     │     │ • Processing    │     │ • yfinance      │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────────────────┴───────────────────────┘
                                 │
                     ┌───────────▼───────────┐
                     │    Generation         │
                     │                       │
                     │  Multi-Agent System   │
                     │  • Generalist         │
                     │  • Market Specialist  │
                     │  • News Specialist    │
                     │  • Orchestrator       │
                     │  • Decision Logic     │
                     └───────────┬───────────┘
                                 │
                                 │
                                 │          
                         ┌───────▼────────┐ 
                         │    FastAPI     │ 
                         │   (RESTful)    │ 
                         └────────────────┘ 
```

### Multi-Agent Orchestration Pattern

**Handoff Orchestration with Selective Concurrency**

1. **Generalist Agent** (front-facing)
   - Full conversation context with prompt caching
   - Direct RAG capabilities (hybrid retrieval)
   - Basic market data tools
   - Handles 80-90% of queries independently

2. **Specialist Agents** (on-demand)
   - Market Data Specialist: Deep technical analysis, indicators, comparisons
   - News Specialist: Comprehensive narrative synthesis, multi-document analysis
   - Minimal context (2-3 turn window) reduces cost, justifies expensive models
   - **ProcessPoolExecutor**: True parallelism for background pre-fetching

3. **Decision Logic**
   - Conservative specialist invocation (minimize cost)
   - Predictive pre-fetching (>80% confidence threshold)
   - User profile tracking (power users, follow-up patterns)
   - Context-aware specialist selection

**Example Flow:**
```
User: "What moved AAPL today?"
  └─ Generalist: "AAPL up 2.3% to $258.02"
     └─ [Background] Pre-fetch News Specialist (85% confidence)

[30 seconds later]
User: "Why did it move?"
  └─ Generalist: Instant response using cached specialist report
```

### Hybrid Retrieval Strategy

**Weighted Reciprocal Rank Fusion (RRF)**

Based on systematic LLM-as-judge evaluation showing embeddings dominant performance:
- **Embeddings (NDCG@5: 0.979)**: Semantic understanding, conceptual queries
- **BM25 (NDCG@5: 0.606)**: Exact ticker matching, keyword precision
- **Fusion**: 2:1 embeddings:BM25 weighting reflects 61% performance advantage
- **RRF Constant (k=60)**: Standard parameter from literature

This hybrid approach plays to both strengths:
- BM25 ensures precision on exact ticker symbols (`AAPL`, `NVDA`, `TSLA`)
- Embeddings handle semantic concepts (`cloud providers`, `undervalued stocks`)
- RRF fusion combines rankings for optimal relevance

## Evaluation Results

Systematic comparison using LLM-as-judge on comprehensive test query suite:

| Retrieval Method | NDCG@5 | Precision@5 | Recall@5 | MRR  |
|-----------------|--------|-------------|----------|------|
| **Embeddings**  | 0.979  | 0.850       | 0.720    | 0.891|
| **BM25**        | 0.606  | 0.520       | 0.450    | 0.623|
| **Hybrid (2:1)**| 0.967  | 0.840       | 0.710    | 0.883|

**Key Insights:**
- Embeddings excel at semantic queries (`cloud computing growth`, `AI chip makers`)
- BM25 excels at exact ticker matches (`NVDA stock`, `TSLA earnings`)
- Hybrid fusion combines strengths with minimal performance penalty
- 2:1 weighting empirically determined from evaluation results

**Test Query Categories:**
- Exact ticker matching (direct ticker symbols)
- Semantic concepts (industry categories, abstract qualities)
- Multi-stock comparisons (sector-wide queries)
- Temporal queries (time-bounded questions)
- Analytical queries (domain knowledge + analysis)
- Edge cases (ambiguity, misspellings)

## Project Organization

```
ENTROPY/
├── Makefile                               # Build automation
├── README.md                              
├── pyproject.toml                         # Dependencies and project config
├── banner.txt                             
├── .env.example                           # Environment variable template
├── data/
│   └── processed/                         # BM25/embedding stores (*.pkl, *.faiss)
├── entropy/
│   ├── api/                               # FastAPI REST server
│   │   ├── main.py                        # App with lifecycle management
│   │   └── schemas.py                     # Pydantic request/response models
│   ├── contexts/                          # Domain-driven design contexts
│   │   ├── market_data/                   # Quantitative stock data
│   │   │   ├── analytics.py               # Performance comparisons, rankings
│   │   │   ├── data_structures.py         # Type-safe Pydantic models
│   │   │   ├── signals.py                 # Technical indicators (RSI, MACD, SMA)
│   │   │   └── tools.py                   # yfinance wrappers
│   │   ├── news_analysis/                 # Qualitative news processing
│   │   │   ├── aggregates.py              # Timeline analytics, sentiment trends
│   │   │   ├── constants.py               # Sentiment thresholds, FinBERT config
│   │   │   ├── models.py                  # NewsArticle, SentimentScore models
│   │   │   ├── processor.py               # Text cleaning, deduplication
│   │   │   └── sentiment.py               # FinBERT sentiment analysis
│   │   ├── retrieval/                     # Information discovery methods
│   │   │   ├── bm25_retrieval.py          # BM25 document store
│   │   │   ├── embedding_retrieval.py     # FAISS vector store
│   │   │   ├── hybrid_retrieval.py        # Weighted RRF fusion
│   │   │   ├── ingest_20_stocks.py        # Data ingestion script
│   │   │   └── yfinance_fetcher.py        # yfinance fetching
│   │   └── generation/                    # Multi-agent LLM orchestration
│   │       ├── agents.py                  # Generalist, Market/News specialists
│   │       ├── context_manager.py         # Session and conversation state
│   │       ├── decision_logic.py          # Specialist invocation triggers
│   │       ├── llm_client.py              # Anthropic API with caching
│   │       ├── orchestrator.py            # Main orchestrator + specialist pool
│   │       ├── prompts.py                 # System prompts for each agent
│   │       └── tools.py                   # Cross-context tool wrappers
│   ├── evaluation/                        # Systematic retrieval comparison
│   │   ├── llm_judge.py                   # OpenAI-based relevance judgments
│   │   ├── metrics.py                     # Precision@K, Recall@K, NDCG, MRR
│   │   ├── run_evaluation.py              # Main evaluation orchestrator
│   │   └── test_queries.py                # Test query suite (6 categories)
│   ├── prototype/                         # Early prototypes
│   └── utils/                    
├── scripts/                               
│   ├── run_api.sh                         # Start FastAPI server
│   └── test_api.py                        # API integration tests
├── tests/                                 # Test suite
│   ├── fixtures/                          # Data and mocks
│   ├── integration/                       # Domain boundary, full pipeline tests
│   │   ├── test_domain_boundaries.py
│   │   └── test_full_pipeline.py
│   └── unit/                              # Unit tests with mocked dependencies
│       ├── test_bm25_retrieval.py
│       ├── test_embedding_retrieval.py
│       ├── test_market_data.py
│       ├── test_metrics.py
│       └── test_models.py
└── outs/                        
    ├── logs/                              # Structured logging output
    └── evaluation/                        # Evaluation results (JSON)
```


## Core Features

### Multi-Agent Orchestration with Cost Optimization

- **Generalist Agent**: Handles 80-90% of queries independently with full RAG capabilities
  - Model: Claude Sonnet 4.5
  - Prompt caching: 90% cost savings on repeated context
  - Average cost: **$0.002 per query**

- **Specialist Agents**: Invoked selectively for deep analysis
  - **Market Data Specialist**: Technical indicators (RSI, MACD), cross-stock analytics (Claude Opus 4)
  - **News Specialist**: Deep narrative synthesis and sentiment analysis (Claude Sonnet 4.5)
  - Minimal context (2-3 turn window) justifies expensive models
  - Average cost: **$0.015-0.030 per invocation**

- **Intelligent Routing**: Conservative specialist invocation based on:
  - Technical jargon detection (`RSI`, `MACD`, `golden cross`)
  - Explicit depth requests (`detailed analysis`, `comprehensive report`)
  - User dissatisfaction (`not enough detail`, `tell me more`)
  - Power user analytical queries (>10 queries in session)

- **Predictive Pre-fetching**: Background specialist execution when >80% confidence
  - "What moved AAPL?" → Pre-fetch News Specialist (85% chance of "why?" follow-up)
  - Established follow-up patterns → Pre-fetch for instant responses
  - Cached results with 5-minute TTL

### Hybrid Retrieval (BM25 + Embeddings)

Weighted Reciprocal Rank Fusion combining:
- **BM25**: Exact keyword/ticker matching (NDCG@5: 0.606)
- **Embeddings**: Semantic similarity (NDCG@5: 0.979)
- **Fusion Strategy**: 2:1 embeddings:BM25 weighting based on systematic evaluation
- **Coverage**: 20 U.S. stocks across diverse sectors (tech, finance, energy, healthcare, consumer, industrial)

### Systematic Evaluation Framework

- **LLM-as-Judge**: OpenAI GPT-4o-mini for honest (query, document) relevance judgments
- **Test Query Suite**: 6 categories (exact_ticker, semantic_concept, multi_stock, temporal, analytical, edge_cases)
- **IR Metrics**: Precision@K, Recall@K, NDCG@K, MRR
- **Performance Tracking**: Latency statistics (mean, p50, p95, p99), cost per query

### Market Data & News Analysis

- **Quantitative Analysis**: Real-time prices, fundamentals, technical indicators (SMA, EMA, RSI, MACD, golden cross detection)
- **Cross-Stock Analytics**: Performance comparisons, top performers, returns calculations
- **News Processing**: FinBERT sentiment analysis, timeline aggregates, volume spike detection
- **Temporal Intelligence**: Sentiment trends, recent shifts, daily breakdowns

## Development

### Formatting and Linting

```bash
# Format code with black
make format

# Check linting
make lint

# Clean cache files
make clean
```

### Testing

```bash
# Run unit tests (fast, mocked dependencies)
make test

# Run all tests including integration
make test-all

# Run specific test
pytest tests/unit/test_market_data.py::test_price_fetching -v
```

**Test Organization:**
- **Unit tests**: Fast, mocked external dependencies (yfinance, Anthropic API)
- **Integration tests**: Domain boundary verification, full pipeline tests
- **Evaluation suite**: Systematic BM25 vs embeddings comparison with LLM-as-judge

### Running Evaluation

```bash
# Compare BM25 vs embeddings on full test query suite
python entropy/evaluation/run_evaluation.py

# Results saved to outs/evaluation/
# - bm25_results_{run_id}.json
# - embedding_results_{run_id}.json
# - comparison_{run_id}.json (aggregated metrics, category breakdown)
```

## Coverage

**20 U.S. Stocks Across Diverse Sectors:**

| Sector | Tickers |
|--------|---------|
| **Technology** | AAPL, MSFT, GOOGL, NVDA, META, AMZN |
| **Finance** | JPM, V, BRK-B |
| **Energy** | XOM, CVX |
| **Healthcare** | JNJ, UNH |
| **Consumer Goods** | PG, KO, NKE |
| **Industrial** | BA, GE |
| **Automotive** | TSLA, F |
