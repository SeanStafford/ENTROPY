"""
Shared utilities for Huddle agents.

Extracted from rag_chat.py to avoid duplication.
"""

import os
import json
from ingest_documents import SimpleDocumentStore

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PROTOTYPE_ROOT = os.getenv("PROJECT_ROOT") + "entropy/prototype/"

class DataAccess:
    """Shared data access layer for all Huddle agents."""

    def __init__(
        self,
        doc_store_path=PROTOTYPE_ROOT + "data/processed/doc_store.pkl",
        stock_data_path= PROTOTYPE_ROOT + "data/processed/stock_data.json"
    ):
        """Initialize data access layer."""
        print("Loading data access layer...")

        # Load document store for news
        self.doc_store = SimpleDocumentStore.load(doc_store_path)

        # Load structured stock data
        with open(stock_data_path, 'r') as f:
            self.stock_data = json.load(f)

        # Company name to ticker mapping
        self.company_map = {
            'APPLE': 'AAPL',
            'MICROSOFT': 'MSFT',
            'GOOGLE': 'GOOGL',
            'ALPHABET': 'GOOGL',
            'TESLA': 'TSLA',
            'NVIDIA': 'NVDA'
        }

    def extract_ticker(self, query):
        """Extract ticker symbol from query text."""
        query_upper = query.upper()

        # Check for explicit ticker symbols
        for ticker in self.stock_data.keys():
            if ticker in query_upper:
                return ticker

        # Check for company names
        for name, ticker in self.company_map.items():
            if name in query_upper:
                return ticker

        return None

    def get_stock_info(self, ticker, include_history=False):
        """Get structured stock data for a ticker."""
        if ticker not in self.stock_data:
            return None

        data = self.stock_data[ticker]
        info = data['info']

        result = {
            'ticker': ticker,
            'current_price': info.get('currentPrice'),
            'previous_close': info.get('previousClose'),
            'day_high': info.get('dayHigh'),
            'day_low': info.get('dayLow'),
            'market_cap': info.get('marketCap'),
            'sector': info.get('sector'),
            'industry': info.get('industry'),
            'fifty_day_avg': info.get('fiftyDayAverage'),
            'two_hundred_day_avg': info.get('twoHundredDayAverage'),
        }

        if include_history:
            result['history'] = data['history']

        return result

    def search_news(self, query, k=3):
        """Search for relevant news articles."""
        results = self.doc_store.search(query, k=k)

        # Format results
        articles = []
        for result in results:
            doc = result['document']
            articles.append({
                'ticker': doc['metadata']['ticker'],
                'title': doc['metadata']['title'],
                'text': doc['text'],
                'score': result['score']
            })

        return articles
