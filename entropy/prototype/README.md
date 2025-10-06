# ENTROPY Prototype

Three standalone prototypes for rapid experimentation with LLM chat and RAG (Retrieval-Augmented Generation) for financial data.

## Files

1. **[simple_chat.py](simple_chat.py)** - Basic LLM chat interface implemented for local CPU usage (yes, it will be slow)
2. **[ingest_documents.py](ingest_documents.py)** - Document ingestion and embedding storage, specifically for `yfinance`
3. **[rag_chat.py](rag_chat.py)** - RAG-enhanced financial chatbot implemented for OpenAI API usage

## Setup

```bash
# Install dependencies
make install

# Set up environment variables in .env
echo "OPENAI_API_KEY=your-key-here" >> .env
echo "PROJECT_ROOT=$(pwd)/" >> .env
echo "PROTOTYPE_PATH=$(pwd)/entropy/prototype/" >> .env
```

## Usage

### 1. Simple Chat

Basic chatbot with no RAG. Supports API mode (OpenAI) or local mode (TinyLlama).

```bash
# Run with OpenAI API (recommended)
python -m entropy.prototype.simple_chat
# Run locally (very slow, you might not have enough memory)
python -m entropy.prototype.simple_chat --local
```

Example:
```
You: What is machine learning?

Assistant: Assistant: Machine learning is a subset of artificial intelligence (AI) that focuses on ...
```

### 2. Document Ingestion

Fetches stock news and data from yfinance, creates searchable embeddings with FAISS.

```bash
python -m entropy.prototype.ingest_documents
```

Creates:
- `data/processed/doc_store.pkl` - Document metadata
- `data/processed/doc_store.faiss` - Vector index
- `data/processed/stock_data.json` - Structured stock data

### 3. RAG Chat

Financial chatbot with multi-channel retrieval (news articles + structured price/company data).

```bash
# Run the document ingestion first
# Then start RAG chat
python -m entropy.prototype.rag_chat
```

Example:
```
You: What's the current price of Apple?
Assistant: According to AAPL data, the current price is $178.50...

You: What's the news about Tesla?
Assistant: Based on recent TSLA articles:
1. Tesla announces Gigafactory expansion...
```

Commands:
- `/norag` - Toggle retrieval on/off

## Simple vs RAG 

Simple
```
You: What is the current price of Apple?

Assistant: I don't have real-time data access to provide current stock prices. You can check the latest price of Apple (AAPL) on financial news websites, stock market apps, or through brokerage platforms.
```

RAG
```
You: What is the current price of Apple?

Assistant: The current price of Apple (AAPL) is $258.02.
```


## Architecture

**simple_chat.py**: Minimal working version of a chatbot

**ingest_documents.py**:
- Fetches yfinance news/data for 10 tech stocks
- Generates embeddings with `all-MiniLM-L6-v2`
- Indexes vectors in FAISS for similarity search

**rag_chat.py**:
- Intent classification (price, news, history, company info)
- Multi-channel retrieval (vector search + structured data)
- Context-grounded generation with `gpt-4o-mini`

## Full Workflow

```bash
make install
echo "OPENAI_API_KEY=your-key" >> .env
echo "PROJECT_ROOT=$(pwd)/" >> .env
echo "PROTOTYPE_PATH=$(pwd)/entropy/prototype/" >> .env

python -m entropy.prototype.ingest_documents
python -m entropy.prototype.rag_chat
```

## Notes

- Re-run ingestion periodically for fresh data
- yfinance reliability varies; handle errors in production
- Default model: `gpt-4o-mini` for cost efficiency
