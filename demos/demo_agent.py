"""
demos/demo_agent.py
────────────────────────────────────────────────
Scripted demo showing the agent's capabilities without interactive input.
Useful for screenshots, LinkedIn posts, and showcasing the project.

Run with:
    python demos/demo_agent.py

Part of: AI Research Agent - Module 5
"""

import sys
import time
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.rule import Rule

from src.agent import ResearchAgent

console = Console()

DEMO_QUERIES = [
    {
        "label": "Demo 1 — Wikipedia Lookup + Summarization",
        "query": "What is Retrieval-Augmented Generation (RAG) and why is it important for AI?"
    },
    {
        "label": "Demo 2 — Web Search for Recent Info",
        "query": "What are the most popular AI agent frameworks in 2024?"
    },
    {
        "label": "Demo 3 — Math Calculation",
        "query": "If a model has 7 billion parameters and each parameter uses 4 bytes, how many GB of VRAM does it need? Show the calculation."
    },
    {
        "label": "Demo 4 — Multi-Tool Chained Research",
        "query": "Compare GPT-4 and Gemini 1.5 Pro. What are the key differences in context window size and capabilities?"
    },
]


def run_demo():
    console.print(Panel(
        "[bold cyan]🤖 AI Research Agent — Demo Run[/]\n"
        "[dim]Module 5: AI Agents, Tools & Automation[/]",
        border_style="cyan"
    ))

    try:
        agent = ResearchAgent()
    except ValueError as e:
        console.print(f"[bold red]Error:[/] {e}")
        return

    # Pre-load some long-term memory
    agent.remember("user_interest", "AI and machine learning")
    agent.remember("preferred_format", "concise with bullet points")

    for demo in DEMO_QUERIES:
        console.print()
        console.rule(f"[bold yellow]{demo['label']}[/]")
        console.print(f"[bold green]Query:[/] {demo['query']}\n")

        tool_calls_log = []

        def log_tool_call(name, args):
            tool_calls_log.append(name)
            console.print(f"  [yellow]⚡ Calling tool:[/] [cyan]{name}[/]")

        def log_tool_result(name, result):
            preview = result[:100].replace("\n", " ")
            console.print(f"  [green]✓[/] Got result from [cyan]{name}[/]: [dim]{preview}...[/]")

        start = time.time()
        response = agent.chat(
            demo["query"],
            on_tool_call=log_tool_call,
            on_tool_result=log_tool_result
        )
        elapsed = time.time() - start

        console.print()
        console.print(Panel(
            Markdown(response),
            title=f"[cyan]Agent Response[/] [dim]({elapsed:.1f}s | tools: {tool_calls_log})[/]",
            border_style="green",
            padding=(1, 2)
        ))
        time.sleep(1)

    # Save the demo session
    path = agent.save_session()
    console.print(f"\n[green]✓ Demo session saved:[/] [dim]{path}[/]")
    console.print("\n[bold cyan]Demo complete! 🎉[/]")


if __name__ == "__main__":
    run_demo()
