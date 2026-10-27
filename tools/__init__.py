"""
tools/__init__.py
────────────────────────────────────────────────
Exports all tool functions and the Gemini tool declarations.
Part of: AI Research Agent - Module 5
"""

from tools.web_search import web_search, format_search_results
from tools.wikipedia_tool import get_wikipedia_summary, get_wikipedia_sections
from tools.calculator import calculate, unit_convert
from tools.summarizer import chunk_text, clean_text

# ── Gemini Function Declarations ─────────────────────────────────────────────
# These are passed to the model so it knows what tools it can call.

TOOL_DECLARATIONS = [
    {
        "name": "web_search",
        "description": (
            "Search the web using DuckDuckGo. Use this to find current news, "
            "recent events, technical documentation, or any live information."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to look up"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results (default 5, max 10)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_wikipedia_summary",
        "description": (
            "Fetch an authoritative summary from Wikipedia for a given topic. "
            "Best for established concepts, historical facts, scientific topics."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The Wikipedia article title or topic name"
                },
                "sentences": {
                    "type": "integer",
                    "description": "Number of summary sentences to return (default 5)"
                }
            },
            "required": ["topic"]
        }
    },
    {
        "name": "get_wikipedia_sections",
        "description": "List all sections in a Wikipedia article to decide which part to read.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The Wikipedia article title"
                }
            },
            "required": ["topic"]
        }
    },
    {
        "name": "calculate",
        "description": (
            "Evaluate a mathematical expression safely. "
            "Supports standard math operators and functions like sqrt, log, sin, cos, pi, etc."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The math expression to evaluate (e.g. '2**10 + sqrt(144)')"
                }
            },
            "required": ["expression"]
        }
    },
    {
        "name": "unit_convert",
        "description": (
            "Convert between common units of measurement: km/miles, kg/pounds, "
            "celsius/fahrenheit, meters/feet, liters/gallons."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "value": {
                    "type": "number",
                    "description": "The numeric value to convert"
                },
                "from_unit": {
                    "type": "string",
                    "description": "Source unit (e.g. 'km', 'celsius', 'kg')"
                },
                "to_unit": {
                    "type": "string",
                    "description": "Target unit (e.g. 'miles', 'fahrenheit', 'pounds')"
                }
            },
            "required": ["value", "from_unit", "to_unit"]
        }
    }
]

# Dispatcher: maps tool name -> callable
TOOL_MAP = {
    "web_search": lambda args: format_search_results(
        web_search(args["query"], args.get("max_results", 5))
    ),
    "get_wikipedia_summary": lambda args: get_wikipedia_summary(
        args["topic"], sentences=args.get("sentences", 5)
    ),
    "get_wikipedia_sections": lambda args: get_wikipedia_sections(args["topic"]),
    "calculate": lambda args: calculate(args["expression"]),
    "unit_convert": lambda args: unit_convert(
        args["value"], args["from_unit"], args["to_unit"]
    ),
}

__all__ = [
    "TOOL_DECLARATIONS", "TOOL_MAP",
    "web_search", "format_search_results",
    "get_wikipedia_summary", "get_wikipedia_sections",
    "calculate", "unit_convert",
    "chunk_text", "clean_text",
]
