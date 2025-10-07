#!/usr/bin/env python3
"""Terminal chat interface for ENTROPY."""

import os
import sys
import asyncio
import threading
import time
import readline
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich import box

load_dotenv()

# Add project root to path if needed
PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", Path(__file__).resolve().parent.parent.parent))
sys.path.insert(0, str(PROJECT_ROOT))

from entropy.contexts.generation import Orchestrator
from entropy.utils.loader import LOADER_FRAMES
from entropy.utils.logging import configure_cli_logging

# Configure logging not to print to console
configure_cli_logging("cli_session")

console = Console()


class EntropyChat:
    """Terminal chat interface."""

    def __init__(self):
        self.session_id = f"terminal_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.orchestrator = None
        self.total_cost = 0.0
        self.loader_active = False
        self.loader_thread = None
        self._setup_readline()

    def _setup_readline(self):
        """Enable command history with up/down arrows."""
        history_file = Path.home() / ".entropy_history"
        if history_file.exists():
            try:
                readline.read_history_file(history_file)
            except:
                pass
        readline.set_history_length(1000)
        import atexit
        atexit.register(readline.write_history_file, history_file)

    def show_banner(self):
        """Display ENTROPY banner."""
        banner_path = PROJECT_ROOT / "banner.txt"
        try:
            with open(banner_path, 'r') as f:
                console.print(f.read(), style="cyan")
        except FileNotFoundError:
            console.print("[bold cyan]ENTROPY[/bold cyan]")
            console.print("[dim]Financial Intelligence System[/dim]\n")
        console.print("[dim]Type 'help' for commands, 'quit' to exit[/dim]\n")

    def show_help(self):
        """Display help."""
        help_table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
        help_table.add_column("Command", style="green")
        help_table.add_column("Description")
        help_table.add_row("/help", "Show this help message")
        help_table.add_row("/quit, /exit", "Exit the chat")
        help_table.add_row("/clear", "Clear conversation history")
        help_table.add_row("/cost", "Show total cost for this session")
        help_table.add_row("/session", "Show session information")

        console.print("\n[bold]Commands:[/bold]")
        console.print(help_table)
        console.print("\n[bold]Example Queries:[/bold]")
        for example in ["• What is AAPL's current price?", "• Show me NVDA's RSI and MACD indicators",
                       "• Compare AAPL vs MSFT performance this week", "• What moved Tesla today?",
                       "• Which tech stocks are undervalued?"]:
            console.print(f"  [dim]{example}[/dim]")
        console.print()

    def show_status(self, agent: str, cost: float):
        """Show agent and cost info."""
        status_table = Table.grid(padding=(0, 2))
        status_table.add_column(style="dim")
        status_table.add_column(style="dim cyan")
        status_table.add_row("Agent:", agent)
        status_table.add_row("Query cost:", f"${cost:.4f}")
        status_table.add_row("Total cost:", f"${self.total_cost:.4f}")
        console.print(status_table, style="dim")

    def _run_loader(self, frame_delay=0.05):
        """Loader animation thread."""
        start_time = time.time()
        i = 0
        while self.loader_active:
            loader_frame = LOADER_FRAMES[i % len(LOADER_FRAMES)]
            print(f"\rThinking {loader_frame}   {time.time() - start_time:.1f}s", end="", flush=True)
            time.sleep(frame_delay)
            i += 1
        print("\r" + " " * 50 + "\r", end="", flush=True)

    def start_loader(self):
        self.loader_active = True
        self.loader_thread = threading.Thread(target=self._run_loader, daemon=True)
        self.loader_thread.start()

    def stop_loader(self):
        self.loader_active = False
        if self.loader_thread:
            self.loader_thread.join(timeout=1)

    async def process_query(self, query: str):
        """Process query through orchestrator."""
        self.start_loader()
        try:
            result = await self.orchestrator.process_query(query=query, session_id=self.session_id)
            self.stop_loader()
            self.total_cost += result['cost_usd']

            console.print()
            console.print(Panel(Markdown(result['response']), title="[bold green]ENTROPY[/bold green]",
                              border_style="green", box=box.ROUNDED))
            self.show_status(result['agent'], result['cost_usd'])
            if result.get('prefetch_active', False):
                console.print("[dim]⚡ Pre-fetching specialist for instant follow-up[/dim]")
            console.print()
        except Exception as e:
            self.stop_loader()
            raise e

    async def run(self):
        """Interactive chat loop."""
        self.show_banner()
        console.print("[cyan]Initializing ENTROPY...[/cyan]")
        max_workers = int(os.getenv("SPECIALIST_MAX_WORKERS", "4"))
        self.orchestrator = Orchestrator(max_workers=max_workers)
        console.print(f"[green]✓[/green] Orchestrator ready with {max_workers} workers\n")
        self.show_help()

        try:
            while True:
                console.print("[bold cyan]You:[/bold cyan]", end=" ")
                try:
                    query = input().strip()
                    if query and (readline.get_current_history_length() == 0 or
                                query != readline.get_history_item(readline.get_current_history_length())):
                        readline.add_history(query)
                except (EOFError, KeyboardInterrupt):
                    console.print("\n[yellow]Goodbye![/yellow]")
                    break

                if not query:
                    continue

                if query.lower() in ['/quit', '/exit', 'quit', 'exit']:
                    console.print("[yellow]Goodbye![/yellow]")
                    break
                elif query.lower() in ['/help', 'help']:
                    self.show_help()
                    continue
                elif query.lower() in ['/clear', 'clear']:
                    self.session_id = f"terminal_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    console.print(f"[green]✓[/green] Conversation cleared (new session: {self.session_id})\n")
                    continue
                elif query.lower() in ['/cost', 'cost']:
                    console.print(f"\n[cyan]Total cost:[/cyan] ${self.total_cost:.4f}\n")
                    continue
                elif query.lower() in ['/session', 'session']:
                    info_table = Table(show_header=False, box=box.SIMPLE)
                    info_table.add_column(style="cyan")
                    info_table.add_column()
                    info_table.add_row("Session ID:", self.session_id)
                    info_table.add_row("Total cost:", f"${self.total_cost:.4f}")
                    info_table.add_row("Workers:", str(max_workers))
                    console.print()
                    console.print(info_table)
                    console.print()
                    continue

                try:
                    await self.process_query(query)
                except Exception as e:
                    console.print(f"\n[red]Error:[/red] {e}\n", style="bold red")
        finally:
            if self.orchestrator:
                console.print("\n[cyan]Shutting down...[/cyan]")
                self.orchestrator.shutdown()
                console.print("[green]✓[/green] Shutdown complete")


def main():
    """Entry point for terminal chat."""
    chat = EntropyChat()
    asyncio.run(chat.run())


if __name__ == "__main__":
    main()
