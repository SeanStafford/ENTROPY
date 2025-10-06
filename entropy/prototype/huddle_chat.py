"""
Huddle Chat - Multi-agent collaboration prototype (v1).

Simple turn-based group discussion with Analyst, News Agent, and Moderator.
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
from huddle_utils import DataAccess

load_dotenv()


class Agent:
    """Base agent class."""

    def __init__(self, name, system_prompt, client, data_access, temperature):
        self.name = name
        self.system_prompt = system_prompt
        self.client = client
        self.data = data_access
        self.temperature = temperature

    def speak(self, context, user_query):
        """Generate agent's contribution to the discussion."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Context: {context}\n\nUser question: {user_query}"}
        ]

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=self.temperature,
            max_tokens=400
        )

        return response.choices[0].message.content


class Analyst(Agent):
    """Agent specializing in quantitative stock analysis."""

    def __init__(self, client, data_access, temperature=0.1):
        system_prompt = """You are a quantitative stock analyst. Your role is to:
- Identify which stock ticker or tickers are being discussed
- Access current price, historical data, and financial metrics
- Perform calculations (price changes, percentage moves, comparisons to averages)
- Provide clear, numerical insights
- You care about just the facts, not the distracting narrative

Be concise and data-driven. Format numbers clearly (e.g., "$123.45", "up 5.2%"). If you have not received specific ticker info, state that you cannot provide analyysis without a more specific request. You never make up data that you are unsure of.
"""
        super().__init__("Analyst", system_prompt, client, data_access, temperature=temperature)

    def speak(self, context, user_query):
        """Analyst contribution with data lookup."""
        # Extract ticker and get data
        ticker = self.data.extract_ticker(user_query)

        if ticker:
            stock_info = self.data.get_stock_info(ticker, include_history=True)

            if stock_info:
                # Build data context
                data_context = f"""
Stock Data for {ticker}:
- Current Price: ${stock_info['current_price']}
- Previous Close: ${stock_info['previous_close']}
- Day High: ${stock_info['day_high']}, Day Low: ${stock_info['day_low']}
- 50-Day Average: ${stock_info['fifty_day_avg']}
- 200-Day Average: ${stock_info['two_hundred_day_avg']}
- Market Cap: ${stock_info['market_cap']:,}
- Sector: {stock_info['sector']}

Recent Price History:
{chr(10).join(stock_info['history'][-5:])}
"""
                full_context = f"{context}\n\nAvailable Data:\n{data_context}"
            else:
                full_context = f"{context}\n\nNote: Could not find data for {ticker}"
        else:
            full_context = f"{context}\n\nNote: Could not identify specific ticker symbol"

        return super().speak(full_context, user_query)


class NewsAgent(Agent):
    """Agent specializing in news analysis."""

    def __init__(self, client, data_access, temperature=0.95):
        system_prompt = """You are a seasoned financial news analyst with a sharp eye for market-moving stories and a passion for conveying big ideas clearly. Think of yourself as a Wall Street veteran who's seen it all - from dot-com bubbles to meme stock mania. You aren't one of those quants, obsessessed with numbers, missing the forest for the trees. You understand what really matters: stories. You speak the language of the people. For this reason, you avoid citing numbers. If folks want numbers, they go to the numbers guy (the Analyst).

Your role is to:
- Hunt down relevant news articles about the stock in question like a detective following leads
- Synthesize recent events and developments into clear, actionable insights
- Read between the lines to identify sentiment shifts and emerging narratives
- Connect the dots between news events and potential stock movements and, if appropriate, use idioms to make complex financial topics easier to understand for lay folk

You speak with confidence but always back it up with evidence. You never make up news. You're direct and don't sugarcoat bad news, but you're not cynical - you recognize opportunity where others see chaos. You present your findings in spoken dialogue. You keep it short, usually under 150 words, but no more than 250 for more complex topics. You never use markdown or bullet points - just clear, engaging prose.
"""
        super().__init__("News Agent", system_prompt, client, data_access, temperature)

    def speak(self, context, user_query):
        """News agent contribution with article retrieval."""
        # Search for relevant news
        articles = self.data.search_news(user_query, k=3)

        if articles:
            news_context = "Relevant News Articles:\n\n"
            for i, article in enumerate(articles, 1):
                news_context += f"{i}. [{article['ticker']}] {article['title']}\n"
                news_context += f"   {article['text'][:200]}...\n\n"

            full_context = f"{context}\n\n{news_context}"
        else:
            full_context = f"{context}\n\nNote: No relevant news articles found"

        return super().speak(full_context, user_query)


class Moderator(Agent):
    """Agent that facilitates discussion and synthesizes answers."""

    def __init__(self, client, data_access, temperature=0.3):
        system_prompt = """You are a financial advisory moderator. Your role is to:
- Synthesize inputs from the Analyst (number-obsessed) and News Agent (narrative-obsessed) to present a single cohesive summary
- Present the balanced, comprehensive answer to the client
- Highlight key insights from both perspectives
- Be clear about limitations (what we don't know)
- Never provide investment advice - only informational analysis

Format your response in a clear, professional spoken form. Do not use markdown or bullet points. Keep your answer to 400 words or less. 
"""
        super().__init__("Moderator", system_prompt, client, data_access, temperature)


class HuddleChat:
    """Multi-agent huddle discussion system (v1 - single conversation)."""

    def __init__(self):
        # Setup OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")

        self.client = OpenAI(api_key=api_key)

        # Load data access layer
        self.data = DataAccess()

        # Initialize agents
        print("Initializing agents...")
        self.analyst = Analyst(self.client, self.data)
        self.news_agent = NewsAgent(self.client, self.data)
        self.moderator = Moderator(self.client, self.data)

        print("Huddle ready!\n")

    def run_huddle(self, user_query):
        """Run one round of huddle discussion."""
        print("=" * 60)
        print("HUDDLE DISCUSSION")
        print("=" * 60)
        print(f"\n[CLIENT QUESTION]: {user_query}\n")

        # Build context progressively
        context = "Huddle discussion started. Provide your analysis based on the user's question."

        # 1. Analyst speaks first
        print("[ANALYST] Analyzing data...\n")
        analyst_input = self.analyst.speak(context, user_query)
        print(f"{analyst_input}\n")
        print("-" * 60)

        # 2. News Agent speaks
        context += f"\n\nAnalyst's input: {analyst_input}"
        print("\n[NEWS AGENT] Reviewing recent news...\n")
        news_input = self.news_agent.speak(context, user_query)
        print(f"{news_input}\n")
        print("-" * 60)

        # 3. Moderator synthesizes
        context += f"\n\nNews Agent's input: {news_input}"
        print("\n[MODERATOR] Synthesizing findings...\n")
        final_answer = self.moderator.speak(context, user_query)
        print(f"{final_answer}\n")
        print("=" * 60)

        return {
            'analyst': analyst_input,
            'news': news_input,
            'answer': final_answer
        }


def main():
    """Interactive huddle chat."""
    print("=" * 60)
    print("Huddle Chat - Multi-Agent Stock Analysis (v1)")
    print("=" * 60)
    print("\nCommands:")
    print("  /quit - Exit")
    print("=" * 60 + "\n")

    huddle = HuddleChat()

    while True:
        user_input = input("Your question: ").strip()

        if not user_input:
            continue

        if user_input in ["/quit", "/exit"]:
            print("Goodbye!")
            break

        # Run huddle discussion
        try:
            result = huddle.run_huddle(user_input)
            # print(f"\n[FINAL ANSWER FOR CLIENT]:\n{result['answer']}\n")

        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
