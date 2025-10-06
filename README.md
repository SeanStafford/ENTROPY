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
│  ENTROPY is a production-ready financial intelligence system that answers    │
│  free-text questions about U.S. equities by retrieving and synthesizing      │
│  real-time market signals and news from Yfinance through RAG architecture    │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## Installation

```bash
# 1. Create and activate virtual environment
make venv
source .venv/bin/activate

# 2. Install dependencies (venv creation happens automatically if needed)
make install

# For development (includes testing and evaluation tools)
make install-dev
```

**Note**:
> All `make install*` targets will automatically create the `.venv` directory if it doesn't exist, but you still need to activate it manually with `source .venv/bin/activate` before installation.

## Project Organization

```
ENTROPY/
├── Makefile                
├── README.md               
├── pyproject.toml          
├── banner.txt              
├── configs/
├── data/
│   ├── raw/               
│   └── processed/         
├── entropy/
│   ├── contexts/
│   │   ├── market_data/                  # Stock prices and signals
│   │   ├── news_analysis/                # News processing
│   │   ├── retrieval/                    # RAG implementations
│   │   │   ├── bm25_retrieval.py
│   │   │   ├── embedding_retrieval.py
│   │   │   └── yfinance_fetcher.py
│   │   └── generation/                   # LLM response synthesis
│   ├── prototype/
│   │   ├── ingest_documents.py
│   │   ├── rag_chat.py
│   │   └── simple_chat.py
│   ├── evaluation/
│   └── utils/            
├── notebooks/
└── outs/
    ├── logs/
    └── results/      
```

## Architecture

ENTROPY follows domain-driven design principles, organizing code around financial analysis contexts:

- **Market Data Context**: Handles quantitative stock information
- **News Analysis Context**: Processes qualitative information from news articles
- **Retrieval Context**: Implements RAG
- **Generation Context**: Manages generation

## Formatting

```bash
# Format code
make format

# Check linting
make lint

# Clean cache files
make clean
```