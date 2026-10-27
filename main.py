"""
main.py
────────────────────────────────────────────────
CLI entry point for the AI Research Agent.

Features:
  • Rich terminal UI with colors and panels
  • Real-time tool call / result display
  • Special commands: /memory, /remember, /forget, /save, /reset, /help, /exit
  • Multi-turn conversation with persistent memory

Usage:
    python main.py

Part of: AI Research Agent - Module 5
"""

import sys
import os
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
from rich import print as rprint
from rich.rule import Rule
from rich.spinner import Spinner
from rich.live import Live
import time

from src.agent import ResearchAgent

console = Console()


# ── Banner ────────────────────────────────────────────────────────────────────

BANNER = """
[bold cyan]╔══════════════════════════════════════════════════════════╗[/]
[bold cyan]║[/]  [bold white]🤖  AI RESEARCH AGENT[/]  [dim]| Module 5: AI Agents & Automation[/]  [bold cyan]║[/]
[bold cyan]╠══════════════════════════════════════════════════════════╣[/]
[bold cyan]║[/]  [dim]Powered by Google Gemini 1.5 Flash + Tool Calling[/]          [bold cyan]║[/]
[bold cyan]║[/]  [dim]Tools: Web Search · Wikipedia · Calculator · Units[/]         [bold cyan]║[/]
[bold cyan]╚══════════════════════════════════════════════════════════╝[/]
"""

HELP_TEXT = """
[bold]Available Commands:[/]
  [cyan]/help[/]                    Show this help message
  [cyan]/memory[/]                  Show all long-term memory entries
  [cyan]/remember <key> <value>[/]  Store a fact in long-term memory
  [cyan]/forget <key>[/]            Delete a memory entry
  [cyan]/stats[/]                   Show memory statistics
  [cyan]/save[/]                    Save current session to disk
  [cyan]/reset[/]                   Clear conversation history (keep long-term memory)
  [cyan]/exit[/] or [cyan]/quit[/]           Exit the agent

[bold]Example Queries:[/]
  [green]What is quantum computing and how does it work?[/]
  [green]Search for the latest AI news in 2024[/]
  [green]Calculate 2^32 + sqrt(1024)[/]
  [green]Convert 100 km to miles[/]
  [green]Compare Python and JavaScript for web development[/]
"""


# ── Tool call display callbacks ───────────────────────────────────────────────

def on_tool_call(tool_name: str, args: dict) -> None:
    """Display tool invocation to the user."""
    args_str = ", ".join(f"{k}={repr(v)}" for k, v in args.items())
    console.print(f"  [bold yellow]⚡ Tool:[/] [cyan]{tool_name}[/]([dim]{args_str}[/])")


def on_tool_result(tool_name: str, result: str) -> None:
    """Display tool result summary."""
    preview = result[:120].replace("\n", " ")
    if len(result) > 120:
        preview += "..."
    console.print(f"  [bold green]✓ Result:[/] [dim]{preview}[/]")


# ── Command handlers ──────────────────────────────────────────────────────────

def handle_memory_command(agent: ResearchAgent) -> None:
    """Display all long-term memory."""
    entries = agent.memory.recall_all()
    if not entries:
        console.print("[dim]No long-term memory entries yet.[/]")
        return
    table = Table(title="📚 Long-Term Memory", border_style="cyan")
    table.add_column("Key", style="bold cyan")
    table.add_column("Value", style="white")
    for k, v in entries.items():
        table.add_row(k, v)
    console.print(table)


def handle_remember_command(agent: ResearchAgent, parts: list) -> None:
    """Store a fact: /remember key value"""
    if len(parts) < 3:
        console.print("[red]Usage: /remember <key> <value>[/]")
        return
    key = parts[1]
    value = " ".join(parts[2:])
    agent.remember(key, value)
    console.print(f"[green]✓ Remembered:[/] [cyan]{key}[/] = {value}")


def handle_forget_command(agent: ResearchAgent, parts: list) -> None:
    """Delete a memory entry: /forget key"""
    if len(parts) < 2:
        console.print("[red]Usage: /forget <key>[/]")
        return
    key = parts[1]
    success = agent.memory.forget(key)
    if success:
        console.print(f"[green]✓ Forgot:[/] [cyan]{key}[/]")
    else:
        console.print(f"[red]Key not found:[/] {key}")


def handle_stats_command(agent: ResearchAgent) -> None:
    """Display memory statistics."""
    stats = agent.get_memory_stats()
    table = Table(title="📊 Memory Statistics", border_style="magenta")
    table.add_column("Metric", style="bold")
    table.add_column("Value", style="cyan")
    for k, v in stats.items():
        table.add_row(k.replace("_", " ").title(), str(v))
    console.print(table)


# ── Main loop ─────────────────────────────────────────────────────────────────

def main():
    console.print(BANNER)

    # Initialize agent
    try:
        agent = ResearchAgent()
    except ValueError as e:
        console.print(f"[bold red]❌ Error:[/] {e}")
        console.print("\n[dim]Steps to fix:[/]")
        console.print("  1. Copy [cyan].env.example[/] to [cyan].env[/]")
        console.print("  2. Add your Gemini API key from [link=https://aistudio.google.com/app/apikey]https://aistudio.google.com/app/apikey[/link]")
        sys.exit(1)

    console.print("[dim]Type your question or use /help for commands. Press Ctrl+C to exit.[/]\n")

    while True:
        try:
            # Prompt
            user_input = Prompt.ask("[bold green]You[/]").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue

        # ── Handle slash commands ──────────────────────────────────────────
        parts = user_input.split()
        cmd = parts[0].lower()

        if cmd in ("/exit", "/quit"):
            break
        elif cmd == "/help":
            console.print(Panel(HELP_TEXT, title="Help", border_style="cyan"))
            continue
        elif cmd == "/memory":
            handle_memory_command(agent)
            continue
        elif cmd == "/remember":
            handle_remember_command(agent, parts)
            continue
        elif cmd == "/forget":
            handle_forget_command(agent, parts)
            continue
        elif cmd == "/stats":
            handle_stats_command(agent)
            continue
        elif cmd == "/save":
            path = agent.save_session()
            console.print(f"[green]✓ Session saved to:[/] [dim]{path}[/]")
            continue
        elif cmd == "/reset":
            agent.reset_conversation()
            console.print("[green]✓ Conversation reset. Long-term memory preserved.[/]")
            continue

        # ── Send to agent ──────────────────────────────────────────────────
        console.print()
        console.rule("[dim]Researching...[/]", style="dim")

        start_time = time.time()

        try:
            response = agent.chat(
                user_input,
                on_tool_call=on_tool_call,
                on_tool_result=on_tool_result
            )
        except Exception as e:
            console.print(f"[bold red]❌ Agent error:[/] {e}")
            continue

        elapsed = time.time() - start_time
        console.print()
        console.print(Panel(
            Markdown(response),
            title=f"[bold cyan]🤖 Agent[/] [dim]({elapsed:.1f}s)[/]",
            border_style="cyan",
            padding=(1, 2)
        ))
        console.print()

    # Cleanup
    console.print()
    console.rule("[dim]Session ended[/]", style="dim")
    save = Prompt.ask(
        "[dim]Save session before exit? (y/n)[/]",
        default="n",
        show_default=True
    )
    if save.lower() == "y":
        path = agent.save_session()
        console.print(f"[green]✓ Saved to:[/] [dim]{path}[/]")

    console.print("[bold cyan]Goodbye! 👋[/]")


if __name__ == "__main__":
    main()
