# 🤖 AI Research Agent
### Module 5: AI Agents, Tools & Automation | Day 21–25

A fully functional **ReAct-style AI Agent** powered by Google Gemini 1.5 Flash with multi-tool calling, persistent memory, and multi-step research workflows.

---

## 🏗️ Architecture

```
User Input
    │
    ▼
[Understand Task]  ◄── System Prompt + Long-Term Memory
    │
    ▼
[Decide Action]    ◄── Gemini 1.5 Flash (Function Calling)
    │
    ▼
[Use Tool]         ◄── web_search | wikipedia | calculator | unit_convert
    │
    ▼
[Process Result]   ◄── Tool output fed back into context
    │
    ▼
[Respond]          ◄── Grounded, cited final answer
```

**The agent loops** through Decide → Use Tool → Process Result until it has enough information to give a complete answer (max 5 iterations for safety).

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Web Search** | DuckDuckGo search (no API key needed) |
| 📖 **Wikipedia** | Authoritative summaries + section navigation |
| 🧮 **Calculator** | Safe mathematical expression evaluator |
| 📐 **Unit Converter** | km/miles, celsius/fahrenheit, kg/pounds, etc. |
| 🧠 **Short-term Memory** | Sliding window of recent messages for context |
| 💾 **Long-term Memory** | JSON-persisted facts across sessions |
| 📝 **Session Logging** | Full conversation transcript saved to disk |
| 🎨 **Rich CLI** | Beautiful terminal UI with colors and panels |

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd ai-research-agent
pip install -r requirements.txt
```

### 2. Set Up API Key

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your Gemini API key
# Get it free at: https://aistudio.google.com/app/apikey
```

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-1.5-flash
```

### 3. Run the Agent

```bash
# Interactive chat
python main.py

# Scripted demo (no API interaction needed for viewing)
python demos/demo_agent.py
```

---

## 💬 Usage

```
You> What is quantum computing and how does it work?
  ⚡ Tool: get_wikipedia_summary(topic='Quantum computing')
  ✓ Result: Wikipedia: Quantum computing | URL: https://en.wikipedia.org/...

╭─ 🤖 Agent (2.3s) ─────────────────────────────────╮
│                                                      │
│  ## Quantum Computing                                │
│  Quantum computing uses quantum mechanical...        │
│                                                      │
╰──────────────────────────────────────────────────────╯
```

### Special Commands

| Command | Description |
|---|---|
| `/help` | Show all commands |
| `/memory` | View all long-term memory |
| `/remember <key> <value>` | Store a fact permanently |
| `/forget <key>` | Delete a memory entry |
| `/stats` | Show memory statistics |
| `/save` | Save session transcript |
| `/reset` | Clear conversation (keep memory) |
| `/exit` | Quit the agent |

---

## 🧪 Running Tests

```bash
# Install pytest
pip install pytest

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_tools.py -v
pytest tests/test_memory.py -v
```

---

## 📁 Project Structure

```
ai-research-agent/
├── main.py                    # CLI entry point
├── requirements.txt           # Dependencies
├── .env.example               # Environment template
│
├── src/
│   └── agent.py               # Core ReAct agent loop
│
├── tools/
│   ├── __init__.py            # Tool registry + Gemini declarations
│   ├── web_search.py          # DuckDuckGo web search
│   ├── wikipedia_tool.py      # Wikipedia API integration
│   ├── calculator.py          # Safe math evaluator + unit converter
│   └── summarizer.py          # Text chunking utilities
│
├── memory/
│   ├── memory_manager.py      # Short-term + long-term memory system
│   ├── data/
│   │   ├── longterm_memory.json   # Persisted facts (auto-created)
│   │   └── sessions/              # Session transcripts (auto-created)
│
├── demos/
│   └── demo_agent.py          # Scripted demo for showcasing
│
└── tests/
    ├── test_tools.py          # Tool unit tests
    └── test_memory.py         # Memory system tests
```

---

## 🧠 Concepts Demonstrated (Module 5 Checklist)

- [x] **Chatbots vs Agents** — Agent autonomously decides tool usage vs passive chatbot response
- [x] **Function / Tool Calling** — Gemini function declarations with type-safe schemas
- [x] **External API Integration** — DuckDuckGo, Wikipedia, math libraries
- [x] **Multi-step Workflows** — ReAct loop chains multiple tools per query
- [x] **Agent Memory & State** — Short-term (sliding window) + Long-term (JSON persistence)
- [x] **Agent Frameworks** — Custom ReAct implementation (manual loop control)
- [x] **Agent Safety** — Iteration limits, safe eval, input sanitization
- [x] **Working AI Agent** — Full Understand → Decide → Tool → Process → Respond pipeline

---

## 🔒 Safety & Limitations

- **Calculator**: Uses a whitelist-only eval — no imports, no builtins, only `math` functions
- **Tool iteration limit**: Max 5 tool calls per query to prevent infinite loops
- **API costs**: Gemini 1.5 Flash has a generous free tier (15 RPM, 1M tokens/day)
- **Web search**: DuckDuckGo has rate limits — avoid rapid consecutive searches

---

## 📊 Tech Stack

| Component | Technology |
|---|---|
| LLM | Google Gemini 1.5 Flash |
| Tool Calling | Gemini Function Declarations API |
| Web Search | DuckDuckGo Search (duckduckgo-search) |
| Wikipedia | wikipedia-api |
| CLI UI | Rich |
| Environment | python-dotenv |
| Testing | pytest |

---

## 🔗 Submission

- **GitHub**: [Add your repository link here]
- **LinkedIn**: [Add your post link here]

---

*Built for Module 5: AI Agents, Tools & Automation (Day 21–25)*
