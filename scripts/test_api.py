#!/usr/bin/env python3
"""
Test script for ENTROPY FastAPI endpoint.

Usage:
    python scripts/test_api.py
"""

import requests
import json
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()

BASE_URL = "http://localhost:8000"


def test_health():
    """Test /health endpoint."""
    console.print("\n[bold blue]Testing /health endpoint...[/bold blue]")
    response = requests.get(f"{BASE_URL}/health")

    if response.status_code == 200:
        console.print("[green]✅ Health check passed[/green]")
        console.print(Syntax(json.dumps(response.json(), indent=2), "json"))
    else:
        console.print(f"[red]❌ Health check failed: {response.status_code}[/red]")

    return response.status_code == 200


def test_chat(query: str, session_id: str = "test123"):
    """Test /chat endpoint."""
    console.print(f"\n[bold blue]Testing /chat with query:[/bold blue] '{query}'")

    payload = {
        "query": query,
        "session_id": session_id
    }

    response = requests.post(
        f"{BASE_URL}/chat",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        data = response.json()
        console.print(Panel(
            f"[green]{data['response']}[/green]",
            title=f"Agent: {data['agent']} | Cost: ${data['cost_usd']:.4f}",
            border_style="green"
        ))
        return True
    else:
        console.print(f"[red]❌ Chat request failed: {response.status_code}[/red]")
        console.print(response.text)
        return False


def main():
    """Run all tests."""
    console.print(Panel.fit(
        "[bold cyan]ENTROPY API Test Suite[/bold cyan]",
        border_style="cyan"
    ))

    # Test 1: Health check
    if not test_health():
        console.print("[red]❌ Health check failed. Is the server running?[/red]")
        console.print("   Run: ./scripts/run_api.sh")
        return

    # Test 2: Simple price query (generalist only)
    test_chat("What is AAPL's current price?", session_id="test_simple")

    # Test 3: Technical query (should invoke specialist)
    test_chat("Show me AAPL's RSI and MACD indicators", session_id="test_technical")

    # Test 4: Multi-turn conversation
    test_chat("What moved TSLA today?", session_id="test_multiturn")
    test_chat("Why did it move?", session_id="test_multiturn")

    console.print("\n[bold green]✅ All tests completed![/bold green]")
    console.print("\n[dim]View full API docs at: http://localhost:8000/docs[/dim]")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        console.print("[red]❌ Cannot connect to API server[/red]")
        console.print("   Start server with: ./scripts/run_api.sh")
    except KeyboardInterrupt:
        console.print("\n[yellow]Test interrupted[/yellow]")
