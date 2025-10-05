import json
import os

from dotenv import load_dotenv
from ingest_documents import SimpleDocumentStore
from openai import OpenAI

load_dotenv()
PROTOTYPE_ROOT = os.getenv("PROTOTYPE_PATH")


class RAGChat:
    def __init__(
        self,
        doc_store_path=PROTOTYPE_ROOT + "data/processed/doc_store.pkl",
        stock_data_path=PROTOTYPE_ROOT + "data/processed/stock_data.json",
    ):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"
        self.doc_store = SimpleDocumentStore.load(doc_store_path)
        with open(stock_data_path, "r") as f:
            self.stock_data = json.load(f)
        self.company_map = {
            "APPLE": "AAPL",
            "MICROSOFT": "MSFT",
            "GOOGLE": "GOOGL",
            "ALPHABET": "GOOGL",
            "TESLA": "TSLA",
            "NVIDIA": "NVDA",
        }
        self.history = []

    def _classify_intent(self, query):
        query_lower = query.lower()
        intents = []
        if any(word in query_lower for word in ["price", "cost", "trading", "$", "worth"]):
            intents.append("price")

        if any(word in query_lower for word in ["news", "article", "headlines", "happening"]):
            intents.append("news")

        if any(
            word in query_lower for word in ["change", "gain", "loss", "performance", "history"]
        ):
            intents.append("history")

        if any(word in query_lower for word in ["company", "sector", "industry", "business"]):
            intents.append("info")

        return intents or ["news"]  # news is default

    def _extract_ticker(self, query):
        query_upper = query.upper()
        for ticker in self.stock_data.keys():
            if ticker in query_upper:
                return ticker
        for name, ticker in self.company_map.items():
            if name in query_upper:
                return ticker
        return None

    def _format_stock_info(self, ticker, intents):
        if ticker not in self.stock_data:
            return f"No data for {ticker}"
        data = self.stock_data[ticker]
        info, history = data["info"], data["history"]
        context_parts = []
        if "info" in intents:
            context_parts.append(
                f"**{ticker} Info:** Sector: {info.get('sector')}, Industry: {info.get('industry')}, Summary: {info.get('longBusinessSummary', '')[:300]}"
            )
        if "price" in intents:
            context_parts.append(
                f"**{ticker} Price:** Current: ${info.get('currentPrice')}, Open: ${info.get('open')}, High: ${info.get('dayHigh')}, Low: ${info.get('dayLow')}, Market Cap: ${info.get('marketCap')}"
            )
        if "history" in intents:
            context_parts.append(
                f"**{ticker} History:** {chr(10).join(history[:5])}\n50-Day Avg: ${info.get('fiftyDayAverage')}, 52-Week Range: ${info.get('fiftyTwoWeekLow')} - ${info.get('fiftyTwoWeekHigh')}"
            )
        return "\n".join(context_parts)

    def retrieve_context(self, query, k=3):
        intents = self._classify_intent(query)
        ticker = self._extract_ticker(query)
        context_parts = []

        if "news" in intents or not ticker:
            news_results = self.doc_store.search(query, k=k)
            if news_results:
                news_context = self._format_news_context(news_results)
                context_parts.append(news_context)

        if ticker and any(intent in intents for intent in ["price", "history", "info"]):
            financial_context = self._format_stock_info(ticker, intents)
            context_parts.append(financial_context)

        return (
            "\n\n---\n\n".join(context_parts) if context_parts else "No relevant information found."
        )

    def _format_news_context(self, results):
        if not results:
            return ""
        context_parts = ["**Recent News Articles:**\n"]
        for i, result in enumerate(results, 1):
            document = result["document"]
            ticker = document["metadata"]["ticker"]
            text = document["text"]
            context_parts.append(f"{i}. [{ticker}] {text}")
        return "\n".join(context_parts)

    def generate(self, user_message, use_retrieval=True):
        if use_retrieval:
            # print("DEBUGGING MODE\nContext:\n" + "="*40 + f"\n{context}\n" + "="*40)

            context = self.retrieve_context(user_message)
            system_prompt = (
                """You are a helpful financial assistant. Use the provided context to answer questions about stocks.
- Only use information from the context provided
- If the context doesn't contain relevant information, say "I don't have enough information about that"
- Cite which stock ticker the information comes from
- Never provide investment advice
Context:
"""
                + context
            )
        else:
            system_prompt = "You are a helpful assistant."

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.history)
        messages.append({"role": "user", "content": user_message})

        response = self.client.chat.completions.create(
            model=self.model, messages=messages, temperature=0.15, max_tokens=500
        )

        assistant_message = response.choices[0].message.content
        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": assistant_message})
        return assistant_message


def main():
    print()
    print("RAG chat prototype")
    print("Toggle retrieval on/off with /norag")
    print()

    chat = RAGChat()
    use_rag = True

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue

        if user_input == "/norag":
            use_rag = not use_rag
            print(f"Retrieval {'enabled' if use_rag else 'disabled'}")
            continue

        response = chat.generate(user_input, use_retrieval=use_rag)
        print(f"\nAssistant: {response}")


if __name__ == "__main__":
    main()
