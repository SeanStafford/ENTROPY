import os
import yfinance as yf
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import json
from dotenv import load_dotenv

load_dotenv()
PROTOTYPE_ROOT = os.getenv("PROJECT_ROOT") + "entropy/prototype/"

class SimpleDocumentStore:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dimension = 384 # all-MiniLM-L6-v2 embedding size
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []

    def add_documents(self, texts, metadata_list):

        embeddings = self.model.encode(texts, show_progress_bar=False)
        
        self.index.add(np.array(embeddings).astype('float32'))
        
        # include metadata with stored documents
        for text, metadata in zip(texts, metadata_list):
            self.documents.append({'text': text, 'metadata': metadata})

    def search(self, query, k=3):
        query_embedding = np.array(self.model.encode([query])).astype('float32')
        
        # find k documents with smallest distance in embedding space
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            results.append({'document': self.documents[idx], 'score': dist})
        return results

    def save(self, path=PROTOTYPE_ROOT + "data/processed/doc_store.pkl"):
        os.makedirs(os.path.dirname(path), exist_ok=True) # to initialize
        faiss_path =  path.replace('.pkl', '.faiss')
        
        print(f"Saving document store in {path} and {faiss_path}...")
        faiss.write_index(self.index, faiss_path)
        with open(path, 'wb') as f:
            pickle.dump(self.documents, f)

    @classmethod
    def load(cls, path=PROTOTYPE_ROOT + "data/processed/doc_store.pkl", model_name="all-MiniLM-L6-v2"):
        store = cls(model_name=model_name)

        faiss_path =  path.replace('.pkl', '.faiss')
        store.index = faiss.read_index(faiss_path)
        with open(path, 'rb') as f:
            store.documents = pickle.load(f)
        return store

def fetch_stock_news(tickers):
    all_texts = []
    all_metadata = []
    for ticker_symbol in tickers:
        print(f"\nFetching news for {ticker_symbol}...")
        try:
            ticker = yf.Ticker(ticker_symbol)
            news = ticker.news

            if not news:
                print("  Nothing found.")
                continue
            
            for entry in news:
                article = entry.get('content', {})
                text = f"\n# {article.get('title', '')}\n\n{article.get('summary', '')}\n"

                metadata = {
                    'ticker': ticker_symbol,
                    'title': article.get('title', ''),
                    'publisher': article.get('provider', 'Unknown').get("displayName", "Unknown"),
                    'link': article.get('canonicalUrl', 'Unavailable').get("url", "Unavailable"),
                    'published': article.get('pubDate', 0)
                }

                all_texts.append(text)
                all_metadata.append(metadata)

            print(f"  Added {len(news)} articles")

        except Exception as e:
            print(f"  Error fetching {ticker_symbol}: {e}")

    return all_texts, all_metadata


def fetch_stock_data(tickers):
    stock_data = {}
    info_fields = [
        "industry", "sector", "longBusinessSummary", "fullTimeEmployees", "currentPrice", "open", "dayLow", "dayHigh", "previousClose", "fiftyDayAverage", "fiftyTwoWeekLow", "fiftyTwoWeekHigh", "twoHundredDayAverage", "marketCap", "bookValue", "priceToBook", "dividendRate", "dividendYield"
    ]
    for ticker_symbol in tickers:
        print(f"\nFetching structured data for {ticker_symbol}...")
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            ticker_data = {'ticker': ticker_symbol, 'info': {}}

            for field in info_fields:
                ticker_data['info'][field] = info.get(field, 'N/A')

            # price history for 1 month
            hist = ticker.history(period='1mo')

            history_entries = []
            for date, row in hist.iterrows():
                # Format as text for RAG prototype
                entry = f"On {date.strftime('%Y-%m-%d')}, {ticker_symbol} closed at ${row['Close']:.2f}. "
                history_entries.append(entry)

            ticker_data['history'] = history_entries
            stock_data[ticker_symbol] = ticker_data
            print(f"  Added {len(history_entries)} days of price history")

        except Exception as e:
            print(f"  Error fetching {ticker_symbol}: {e}")

    output_path = PROTOTYPE_ROOT + "data/processed/stock_data.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True) # for initialization

    with open(output_path, 'w') as f:
        json.dump(stock_data, f, indent=2)
    return stock_data


if __name__ == "__main__":
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'JPM', 'NKE']

    print()
    print("RAG document ingestion for prototype")
    print()

    store = SimpleDocumentStore()

    print("Fetching from yfinance...")
    texts, metadata = fetch_stock_news(tickers)

    store.add_documents(texts, metadata)
    store.save()

    # Demo search
    print()
    print("RAG demo:")
    print()


    test_query = "What's happening with Tesla?"
    print(f"Query: {test_query}")
    results = store.search(test_query, k=3)

    for i, result in enumerate(results, 1):
        print(f"\n{i}. [{result['document']['metadata']['ticker']}] {result['document']['metadata']['title']}")
        print(f"   Score: {result['score']:.4f}")