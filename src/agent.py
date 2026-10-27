"""
src/agent.py
────────────────────────────────────────────────
Core ReAct Agent Loop (Reason → Act → Observe → Respond)

Uses the new `google-genai` SDK (v2+) which replaces the deprecated
`google-generativeai` package.

Architecture:
  ┌─────────────────────────────────────────────────┐
  │                  ResearchAgent                   │
  │                                                  │
  │  User Input                                      │
  │      ↓                                           │
  │  [Understand Task]  ← system prompt + memory    │
  │      ↓                                           │
  │  [Decide Action]    ← Gemini function calling   │
  │      ↓                                           │
  │  [Use Tool]         ← web_search / wikipedia /  │
  │      ↓               calculator / unit_convert  │
  │  [Process Result]   ← tool output fed back      │
  │      ↓                                           │
  │  [Respond]          ← final grounded answer     │
  └─────────────────────────────────────────────────┘

Part of: AI Research Agent - Module 5
"""

import os
from typing import Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv

from memory.memory_manager import MemoryManager
from tools import TOOL_DECLARATIONS, TOOL_MAP

load_dotenv()

# ── Configuration ─────────────────────────────────────────────────────────────

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")
MAX_TOOL_ITERATIONS = 5   # safety limit on agentic loops

SYSTEM_PROMPT = """You are an intelligent AI Research Agent. Your goal is to help users 
understand topics deeply by researching, summarizing, and reasoning about information.

## Your Capabilities:
- **web_search**: Search the web for current information and news
- **get_wikipedia_summary**: Get authoritative summaries from Wikipedia
- **get_wikipedia_sections**: Explore Wikipedia article structure
- **calculate**: Evaluate mathematical expressions
- **unit_convert**: Convert between units of measurement

## Your Behavior:
1. **Understand the task** — identify what the user wants to know
2. **Decide your action** — choose the best tool(s) to gather information
3. **Use tools** — call tools to collect data; you can chain multiple tools
4. **Process results** — synthesize the gathered information
5. **Respond clearly** — provide a well-structured, cited answer

## Rules:
- Always cite your sources (URLs, Wikipedia article names)
- If one search isn't enough, do a follow-up search
- Be transparent about what tools you used
- For math questions, always verify with the calculator tool
- Keep responses concise but complete

{memory_context}
"""


def _build_tool_declarations() -> list[types.FunctionDeclaration]:
    """Convert our JSON tool declarations to google-genai FunctionDeclaration objects."""
    type_map = {
        "string": "STRING",
        "integer": "INTEGER",
        "number": "NUMBER",
        "boolean": "BOOLEAN",
        "array": "ARRAY",
        "object": "OBJECT",
    }

    declarations = []
    for t in TOOL_DECLARATIONS:
        properties = {}
        for prop_name, prop_def in t["parameters"]["properties"].items():
            properties[prop_name] = types.Schema(
                type=type_map.get(prop_def["type"], "STRING"),
                description=prop_def.get("description", ""),
            )

        declarations.append(
            types.FunctionDeclaration(
                name=t["name"],
                description=t["description"],
                parameters=types.Schema(
                    type="OBJECT",
                    properties=properties,
                    required=t["parameters"].get("required", []),
                ),
            )
        )
    return declarations


class ResearchAgent:
    """
    A ReAct-style AI Research Agent powered by Google Gemini.

    The agent autonomously decides which tools to use, calls them,
    observes results, and iterates until it can give a complete answer.
    """

    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY not set. "
                "Copy .env.example to .env and add your key from https://aistudio.google.com/app/apikey"
            )

        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.memory = MemoryManager(max_short_term=10)
        self.tools = types.Tool(function_declarations=_build_tool_declarations())
        self.config = types.GenerateContentConfig(
            system_instruction=self._build_system_prompt(),
            tools=[self.tools],
        )

    def _build_system_prompt(self) -> str:
        """Build system prompt with current long-term memory injected."""
        mem_ctx = self.memory.get_memory_context()
        return SYSTEM_PROMPT.format(memory_context=mem_ctx)

    def _execute_tool(self, tool_name: str, tool_args: dict) -> str:
        """Dispatch a tool call and return the result as a string."""
        if tool_name not in TOOL_MAP:
            return f"Unknown tool: {tool_name}"
        try:
            return TOOL_MAP[tool_name](tool_args)
        except Exception as e:
            return f"Tool error ({tool_name}): {str(e)}"

    def chat(self, user_message: str, on_tool_call=None, on_tool_result=None) -> str:
        """
        Process a user message through the ReAct loop.

        Args:
            user_message:   The user's input string
            on_tool_call:   Optional callback(tool_name, args) for UI updates
            on_tool_result: Optional callback(tool_name, result) for UI updates

        Returns:
            Final text response from the agent
        """
        # 1. Understand Task — record and build conversation history
        self.memory.add_message("user", user_message)

        # Build contents list from short-term memory
        contents: list[types.Content] = []
        for msg in self.memory.get_context_window():
            role = msg["role"] if msg["role"] in ("user", "model") else "user"
            # memory stores "assistant" role — map to "model" for Gemini
            if msg["role"] == "assistant":
                role = "model"
            contents.append(
                types.Content(role=role, parts=[types.Part(text=msg["parts"][0])])
            )

        # Refresh system instruction with latest memory
        config = types.GenerateContentConfig(
            system_instruction=self._build_system_prompt(),
            tools=[self.tools],
        )

        iterations = 0
        response = None

        # 2–4. Decide Action → Use Tool → Process Result (agentic loop)
        while iterations < MAX_TOOL_ITERATIONS:
            iterations += 1

            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=contents,
                config=config,
            )

            # Collect all function calls from this response
            tool_calls_made = False
            function_responses = []

            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.function_call:
                        tool_calls_made = True
                        tool_name = part.function_call.name
                        tool_args = dict(part.function_call.args)

                        # Notify UI
                        if on_tool_call:
                            on_tool_call(tool_name, tool_args)

                        # Execute tool
                        result = self._execute_tool(tool_name, tool_args)

                        if on_tool_result:
                            on_tool_result(tool_name, result)

                        function_responses.append(
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=tool_name,
                                    response={"result": result},
                                )
                            )
                        )

            if not tool_calls_made:
                # 5. Respond — model gave a final text answer
                break

            # Append model's tool-call turn
            contents.append(response.candidates[0].content)

            # If this is the last allowed iteration, instruct model to provide final answer directly
            if iterations >= MAX_TOOL_ITERATIONS:
                function_responses.append(
                    types.Part(text="Now synthesize all the tool results above and provide your final answer to the user's question.")
                )
                contents.append(
                    types.Content(role="user", parts=function_responses)
                )
                # Generate final answer without tools
                final_config = types.GenerateContentConfig(
                    system_instruction=self._build_system_prompt()
                )
                response = self.client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=contents,
                    config=final_config,
                )
                break
            else:
                contents.append(
                    types.Content(role="user", parts=function_responses)
                )

        # Extract final text safely
        final_text = ""
        if response and response.text:
            final_text = response.text
        elif response and response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            text_parts = [p.text for p in response.candidates[0].content.parts if p.text]
            final_text = "\n".join(text_parts)

        if not final_text:
            final_text = "I have researched the query and processed the results."

        # Record in memory (store as "assistant" internally)
        self.memory.add_message("assistant", final_text)
        return final_text

    def remember(self, key: str, value: str) -> None:
        """Store a fact in long-term memory."""
        self.memory.remember(key, value)

    def recall(self, key: str) -> Optional[str]:
        """Retrieve a fact from long-term memory."""
        return self.memory.recall(key)

    def get_memory_stats(self) -> dict:
        """Return current memory statistics."""
        return self.memory.get_stats()

    def save_session(self) -> str:
        """Save current session to disk and return file path."""
        path = self.memory.save_session()
        return str(path)

    def reset_conversation(self) -> None:
        """Clear short-term memory to start a new conversation."""
        self.memory.clear_short_term()
