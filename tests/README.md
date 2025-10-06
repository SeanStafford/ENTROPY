# ENTROPY Test Suite

Comprehensive test suite for the ENTROPY financial intelligence system, validating retrieval methods, evaluation metrics, and market data tools.

## Overview

This test suite validates the core deliverable (BM25 vs Embeddings comparison) and demonstrates production engineering practices for the Chaos Labs take-home assignment.

**Key Principles:**
- ✅ **No network calls** - All external APIs mocked (yfinance, etc.)
- ✅ **Fast execution** - Full suite runs in ~2 seconds
- ✅ **Critical path coverage** - Focus on evaluation methodology and retrieval systems
- ✅ **Production hygiene** - Error handling, edge cases, proper mocking

## Configuration

Test configuration is located in **`pyproject.toml`** under `[tool.pytest.ini_options]`:
- Test discovery patterns
- Default options (verbose, skip slow tests, etc.)
- Markers for categorization
- Coverage configuration under `[tool.coverage.run]`

## Test Structure

```
tests/
├── fixtures/
│   ├── conftest.py          # Pytest fixtures (stores, temp dirs, mock data)
│   └── mock_data.py         # Mock yfinance responses (no network calls)
├── unit/
│   ├── test_metrics.py      # Evaluation metrics (20 tests)
│   ├── test_bm25_retrieval.py      # BM25 retrieval (16 tests)
│   ├── test_embedding_retrieval.py # Embedding retrieval (20 tests)
│   ├── test_market_data.py  # Market data tools (10 tests)
│   └── test_models.py       # Data structures (13 tests)
├── integration/             # Integration tests (future)
└── README.md               # This file
```

## Running Tests

### Run All Tests

```bash
# Run all unit tests
pytest tests/unit -v

# Run with coverage report
pytest tests/unit --cov=entropy --cov-report=term

# Run with detailed output
pytest tests/unit -vv --tb=short
```

### Run Specific Test Categories

```bash
# Evaluation metrics only (critical for validating BM25 vs Embeddings)
pytest -m metrics -v

# Market data tools (demonstrates mocking practices)
pytest -m market_data -v

# Retrieval systems
pytest -m retrieval -v

# Run specific test file
pytest tests/unit/test_metrics.py -v
```

### Run Fast Tests Only

```bash
# Skip slow tests (marked with @pytest.mark.slow)
pytest tests/unit -v  # (default behavior from pytest.ini)

# Include slow tests
pytest tests/unit -v -m "not slow or slow"
```

## Test Categories

### 1. Evaluation Metrics (`test_metrics.py`) - **CRITICAL**

Validates the methodology used to compare BM25 vs Embeddings retrieval.

**Tests 20 cases:**
- Precision@K: Perfect, none relevant, partial relevant, edge cases
- Recall@K: Found all, found partial, zero total relevant
- NDCG@K: Perfect ranking, reverse ranking, all zeros, DCG calculation
- MRR: First position, third position, no relevant documents
- Aggregation: Calculate all metrics, aggregate across queries
- Edge cases: k larger than results, k=0, empty lists

**Why Critical:** If these metrics are wrong, the entire evaluation is invalid.

**Run:** `pytest tests/unit/test_metrics.py -v`

### 2. BM25 Retrieval (`test_bm25_retrieval.py`)

Tests sparse lexical retrieval system.

**Tests 16 cases:**
- Initialization: Empty store, verbose flag
- Indexing: Add documents, length mismatch, ticker prepending
- Search: Basic search, ticker filtering, relevance ordering, empty store
- Stats: Corpus statistics, empty store stats
- Persistence: Save/load roundtrip, empty store persistence
- Tokenization: Lowercase, whitespace splitting
- Multi-ticker documents: Indexing, filtering

**Key Feature Tested:** Ticker prepending (e.g., "AAPL" prepended to text for better matching)

**Run:** `pytest tests/unit/test_bm25_retrieval.py -v`

### 3. Embedding Retrieval (`test_embedding_retrieval.py`)

Tests dense semantic retrieval system.

**Tests 20 cases:**
- Initialization: Empty store, custom model
- Indexing: Add documents, embedding dimensions (384-dim), length mismatch
- Search: Basic search, ticker filtering, semantic similarity, empty store
- Stats: Corpus statistics, embedding dimensions
- Persistence: Save/load (pickle + FAISS), empty store
- Backward compatibility: Old `ticker` (string) vs new `tickers` (list)
- Quality: Embedding normalization, different queries produce different embeddings
- Multi-ticker documents: Indexing, filtering

**Key Feature Tested:** Semantic understanding (e.g., "electric cars" matches Tesla/Ford articles)

**Run:** `pytest tests/unit/test_embedding_retrieval.py -v`

### 4. Market Data Tools (`test_market_data.py`) - **DEMONSTRATES MOCKING**

Shows production hygiene with mocked external APIs.

**Tests 10 cases:**
- Get current price: Success, invalid ticker, network error
- Get stock fundamentals: Success, invalid ticker
- Calculate price change: Calculation correctness
- Analytics: Compare performance across tickers
- Technical indicators: SMA calculation, insufficient data
- Error handling: yfinance exceptions caught, technical indicator errors

**Mocking Pattern:**
```python
@patch("yfinance.Ticker")
def test_success(self, mock_ticker_class):
    mock_ticker = MagicMock()
    mock_ticker.info = get_mock_ticker_info("AAPL")
    mock_ticker_class.return_value = mock_ticker

    result = get_current_price("AAPL")
    assert result.current_price == 150.25
```

**Run:** `pytest tests/unit/test_market_data.py -v`

### 5. Data Models (`test_models.py`)

Tests dataclasses and domain models.

**Tests 13 cases:**
- StockPrice: Creation, optional fields
- PriceChange: Positive/negative changes
- NewsArticle: Creation, has_sentiment(), primary_ticker()
- SentimentScore: Creation, probability sum validation
- TickerSentiment: Aggregated sentiment, dominant_sentiment_score()
- PriceHistory: Multiple price points

**Run:** `pytest tests/unit/test_models.py -v`

## Fixtures

### Available Fixtures (from `conftest.py`)

**`temp_data_dir`** - Temporary directory for save/load tests
```python
def test_save_and_load(populated_bm25_store, temp_data_dir):
    save_path = temp_data_dir / "test.pkl"
    populated_bm25_store.save(save_path)
```

**`mock_news_articles`** - 5 sample articles (AAPL, TSLA, MSFT/AMZN, F, NVDA)
```python
def test_indexing(mock_news_articles):
    texts = [article["text"] for article in mock_news_articles]
    store.add_documents(texts, ...)
```

**`populated_bm25_store`** - Pre-populated BM25DocumentStore
```python
def test_search(populated_bm25_store):
    results = populated_bm25_store.search("Apple iPhone", k=3)
```

**`populated_embedding_store`** - Pre-populated EmbeddingDocumentStore
```python
def test_semantic_search(populated_embedding_store):
    results = populated_embedding_store.search("electric vehicles", k=5)
```

### Mock Data Functions (from `mock_data.py`)

**`get_mock_ticker_info(ticker: str)`** - Mock yfinance ticker.info
```python
mock_ticker.info = get_mock_ticker_info("AAPL")
# Returns: {"currentPrice": 150.25, "marketCap": 2.4T, ...}
```

**`get_mock_price_history(ticker: str, period: str)`** - Mock yfinance ticker.history()
```python
history_data = get_mock_price_history("AAPL", period="1mo")
# Returns: List of OHLCV dicts for 30 days
```

## Test Markers

Tests are categorized with pytest markers for selective execution:

- `@pytest.mark.unit` - Unit tests (fast, mocked dependencies)
- `@pytest.mark.metrics` - Evaluation metrics tests
- `@pytest.mark.retrieval` - BM25 and embedding retrieval tests
- `@pytest.mark.market_data` - Market data tools tests
- `@pytest.mark.slow` - Tests that take >1 second (skipped by default)

**Example usage:**
```bash
pytest -m "metrics and unit" -v
pytest -m "not slow" -v  # Default behavior
```

## Coverage

Run with coverage reporting:

```bash
# Terminal report
pytest tests/unit --cov=entropy --cov-report=term

# HTML report
pytest tests/unit --cov=entropy --cov-report=html
open htmlcov/index.html

# Coverage by module
pytest tests/unit --cov=entropy --cov-report=term-missing
```

**Target Coverage:**
- Evaluation metrics: >95% (critical path)
- Retrieval systems: >85% (BM25, embeddings)
- Market data tools: >80% (core functions)
- Overall: >80% for non-internal files

## Writing New Tests

### Test Class Structure

```python
@pytest.mark.unit
@pytest.mark.your_category
class TestYourFeature:
    """Test description."""

    def test_success_case(self):
        """Test the happy path."""
        result = your_function("valid_input")
        assert result == expected_value

    def test_edge_case(self):
        """Test boundary conditions."""
        result = your_function(None)
        assert result is None
```

### Mocking External APIs

```python
from unittest.mock import MagicMock, patch

@patch("yfinance.Ticker")
def test_with_mock(self, mock_ticker_class):
    # Setup mock
    mock_ticker = MagicMock()
    mock_ticker.info = {"currentPrice": 150.25}
    mock_ticker_class.return_value = mock_ticker

    # Call function (will use mock, not real API)
    result = get_current_price("AAPL")

    # Verify
    assert result.current_price == 150.25
```

### Using Fixtures

```python
def test_with_fixture(populated_bm25_store):
    """Fixture automatically injected by pytest."""
    results = populated_bm25_store.search("query", k=5)
    assert len(results) <= 5
```

## Common Issues

### PyTorch Version Error

**Error:** `AttributeError: module 'torch' has no attribute 'compiler'`

**Cause:** Older PyTorch version (1.12.1) incompatible with newer sentence-transformers

**Solution:** Either:
1. Upgrade PyTorch: `pip install torch>=2.1`
2. Skip retrieval tests: `pytest tests/unit/test_metrics.py tests/unit/test_market_data.py tests/unit/test_models.py`

**Tests affected:** `test_bm25_retrieval.py`, `test_embedding_retrieval.py`

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'entropy'`

**Solution:** Install package in development mode:
```bash
pip install -e .
```

### Slow Tests

**Issue:** Some tests run slowly due to model loading

**Solution:** Marked with `@pytest.mark.slow` and skipped by default:
```bash
pytest tests/unit -v  # Skips slow tests (default)
pytest tests/unit -v -m "slow"  # Run only slow tests
```

## CI/CD Integration

For GitHub Actions or similar CI systems:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -e .[dev]
      - run: pytest tests/unit --cov=entropy --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Assignment Context

These tests validate the core deliverable for the Chaos Labs take-home assignment:

**What's Being Evaluated:**
- BM25 vs Embeddings retrieval comparison
- Production code quality and testing practices
- Error handling and edge case coverage
- Ability to mock external dependencies

**What the Tests Demonstrate:**
- ✅ No network calls (all yfinance mocked)
- ✅ Systematic evaluation methodology (metrics validated)
- ✅ Production hygiene (error handling, edge cases)
- ✅ Engineering maturity (fixtures, markers, clear structure)

## Additional Resources

- **pytest docs:** https://docs.pytest.org/
- **unittest.mock:** https://docs.python.org/3/library/unittest.mock.html
- **pytest-cov:** https://pytest-cov.readthedocs.io/

## Questions?

For test-related questions or issues:
1. Check this README
2. Review existing tests for patterns
3. Check pytest.ini for configuration
4. Run with `-vv --tb=short` for detailed output
