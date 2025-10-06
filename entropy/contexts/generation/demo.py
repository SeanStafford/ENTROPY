"""
Demo script for ENTROPY generation context.

Demonstrates:
1. Simple generalist query (no specialist)
2. Technical query (immediate specialist invocation)
3. Follow-up query (using pre-fetched specialist)
4. Dissatisfaction trigger (specialist after feedback)
"""

import asyncio
import os
from dotenv import load_dotenv
from loguru import logger

from entropy.contexts.generation import Orchestrator


async def demo_simple_query(orchestrator: Orchestrator, session_id: str):
    """Demo 1: Simple query handled by generalist alone."""
    print("\n" + "=" * 70)
    print("DEMO 1: Simple Price Query (Generalist Only)")
    print("=" * 70)

    query = "What's AAPL's current price?"
    print(f"\nUser: {query}")

    result = await orchestrator.process_query(query, session_id=session_id)

    print(f"\nAssistant: {result['response']}")
    print(f"\n💰 Cost: ${result['cost_usd']:.4f}")
    print(f"🤖 Agent: {result['agent']}")

    return result


async def demo_technical_query(orchestrator: Orchestrator, session_id: str):
    """Demo 2: Technical query requiring immediate specialist."""
    print("\n" + "=" * 70)
    print("DEMO 2: Technical Analysis Query (Immediate Specialist)")
    print("=" * 70)

    query = "Show me AAPL's RSI and MACD indicators"
    print(f"\nUser: {query}")

    result = await orchestrator.process_query(query, session_id=session_id)

    print(f"\nAssistant: {result['response']}")
    print(f"\n💰 Cost: ${result['cost_usd']:.4f}")
    print(f"🤖 Agent: {result['agent']}")
    if 'specialist_cost' in result:
        print(f"   └─ Specialist: ${result['specialist_cost']:.4f}")
        print(f"   └─ Synthesis: ${result['synthesis_cost']:.4f}")

    return result


async def demo_prefetch_pattern(orchestrator: Orchestrator, session_id: str):
    """Demo 3: Query with pre-fetch and instant follow-up."""
    print("\n" + "=" * 70)
    print("DEMO 3: Pre-fetch Pattern (Instant Follow-up)")
    print("=" * 70)

    # First query - should trigger pre-fetch
    query1 = "What moved TSLA today?"
    print(f"\nUser: {query1}")

    result1 = await orchestrator.process_query(query1, session_id=session_id)

    print(f"\nAssistant: {result1['response']}")
    print(f"\n💰 Cost: ${result1['cost_usd']:.4f}")
    print(f"🤖 Agent: {result1['agent']}")
    if result1.get('prefetch_active'):
        print("🔄 Pre-fetching specialist in background...")

    # Wait a moment for pre-fetch
    await asyncio.sleep(2)

    # Follow-up query - should use cached specialist
    query2 = "Why did it move?"
    print(f"\nUser: {query2}")

    result2 = await orchestrator.process_query(query2, session_id=session_id)

    print(f"\nAssistant: {result2['response']}")
    print(f"\n💰 Cost: ${result2['cost_usd']:.4f}")
    print(f"🤖 Agent: {result2['agent']}")

    return result2


async def demo_dissatisfaction(orchestrator: Orchestrator, session_id: str):
    """Demo 4: Dissatisfaction triggers specialist."""
    print("\n" + "=" * 70)
    print("DEMO 4: Dissatisfaction Trigger")
    print("=" * 70)

    # Initial query
    query1 = "Tell me about NVDA"
    print(f"\nUser: {query1}")

    result1 = await orchestrator.process_query(query1, session_id=session_id)

    print(f"\nAssistant: {result1['response']}")
    print(f"\n💰 Cost: ${result1['cost_usd']:.4f}")

    # Express dissatisfaction
    query2 = "That's not enough detail, give me more"
    print(f"\nUser: {query2}")

    result2 = await orchestrator.process_query(query2, session_id=session_id)

    print(f"\nAssistant: {result2['response']}")
    print(f"\n💰 Cost: ${result2['cost_usd']:.4f}")
    print(f"🤖 Agent: {result2['agent']}")

    return result2


async def main():
    """Run all demos."""
    load_dotenv()

    # Initialize orchestrator
    print("\n🚀 Initializing ENTROPY Orchestrator...")
    orchestrator = Orchestrator(max_workers=4)

    session_id = "demo_session"

    try:
        # Run demos
        await demo_simple_query(orchestrator, session_id)
        await demo_technical_query(orchestrator, session_id)
        await demo_prefetch_pattern(orchestrator, session_id)
        await demo_dissatisfaction(orchestrator, session_id)

        # Show session stats
        print("\n" + "=" * 70)
        print("SESSION STATISTICS")
        print("=" * 70)
        stats = orchestrator.get_session_stats(session_id)
        print(f"Session ID: {stats['session_id']}")
        print(f"Total Queries: {stats['query_count']}")
        print(f"Total Messages: {stats['message_count']}")

    finally:
        # Cleanup
        print("\n🛑 Shutting down orchestrator...")
        orchestrator.shutdown()


if __name__ == "__main__":
    # Run async main
    asyncio.run(main())
