"""
memory/memory_manager.py
────────────────────────────────────────────────
Agent Memory System — stores short-term and long-term context.

Demonstrates:
  • Short-term memory  : sliding window of recent messages (in-context)
  • Long-term memory   : JSON-persisted facts and research notes
  • Session history    : full conversation log for current session
Part of: AI Research Agent - Module 5
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


MEMORY_DIR = Path(__file__).parent / "data"
MEMORY_DIR.mkdir(exist_ok=True)
LONGTERM_FILE = MEMORY_DIR / "longterm_memory.json"
SESSIONS_DIR = MEMORY_DIR / "sessions"
SESSIONS_DIR.mkdir(exist_ok=True)


class MemoryManager:
    """
    Manages agent memory across three layers:
    1. short_term  – last N messages kept in context window
    2. long_term   – persistent JSON store of key facts / research notes
    3. session_log – full conversation transcript for current session
    """

    def __init__(self, max_short_term: int = 10):
        self.max_short_term = max_short_term
        self.short_term: list[dict] = []          # [{role, content, timestamp}]
        self.long_term: dict = self._load_longterm()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_log: list[dict] = []

    # ── Short-term memory ────────────────────────────────────────────────────

    def add_message(self, role: str, content: str) -> None:
        """Add a message to short-term memory and session log."""
        entry = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.short_term.append(entry)
        self.session_log.append(entry)

        # Evict oldest if over limit
        if len(self.short_term) > self.max_short_term * 2:
            self.short_term = self.short_term[-self.max_short_term * 2:]

    def get_context_window(self) -> list[dict]:
        """Return the last N messages for LLM context (role + content only)."""
        recent = self.short_term[-self.max_short_term * 2:]
        return [{"role": m["role"], "parts": [m["content"]]} for m in recent]

    def clear_short_term(self) -> None:
        """Clear short-term memory (start fresh conversation)."""
        self.short_term.clear()

    # ── Long-term memory ─────────────────────────────────────────────────────

    def remember(self, key: str, value: str) -> None:
        """
        Store a fact in long-term memory.

        Args:
            key: Short identifier (e.g., 'user_name', 'research_topic')
            value: The fact or note to remember
        """
        self.long_term[key] = {
            "value": value,
            "saved_at": datetime.now().isoformat()
        }
        self._save_longterm()

    def recall(self, key: str) -> Optional[str]:
        """Retrieve a fact from long-term memory by key."""
        entry = self.long_term.get(key)
        return entry["value"] if entry else None

    def recall_all(self) -> dict:
        """Return all long-term memory entries as {key: value}."""
        return {k: v["value"] for k, v in self.long_term.items()}

    def forget(self, key: str) -> bool:
        """Delete a long-term memory entry."""
        if key in self.long_term:
            del self.long_term[key]
            self._save_longterm()
            return True
        return False

    def get_memory_context(self) -> str:
        """Format long-term memory as a string to inject into system prompt."""
        if not self.long_term:
            return ""
        lines = ["📚 **Remembered Facts:**"]
        for k, v in self.long_term.items():
            lines.append(f"  • {k}: {v['value']}")
        return "\n".join(lines)

    # ── Session log ──────────────────────────────────────────────────────────

    def save_session(self) -> Path:
        """Persist the current session log to disk."""
        session_file = SESSIONS_DIR / f"session_{self.session_id}.json"
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "session_id": self.session_id,
                    "started_at": self.session_log[0]["timestamp"] if self.session_log else None,
                    "messages": self.session_log,
                    "long_term_snapshot": self.recall_all()
                },
                f, indent=2, ensure_ascii=False
            )
        return session_file

    def get_stats(self) -> dict:
        """Return memory statistics."""
        return {
            "short_term_messages": len(self.short_term),
            "long_term_entries": len(self.long_term),
            "session_messages": len(self.session_log),
            "session_id": self.session_id
        }

    # ── Private helpers ──────────────────────────────────────────────────────

    def _load_longterm(self) -> dict:
        if LONGTERM_FILE.exists():
            try:
                with open(LONGTERM_FILE, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_longterm(self) -> None:
        with open(LONGTERM_FILE, "w", encoding="utf-8") as f:
            json.dump(self.long_term, f, indent=2, ensure_ascii=False)
