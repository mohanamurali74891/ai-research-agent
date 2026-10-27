"""
tests/test_memory.py
────────────────────────────────────────────────
Unit tests for the MemoryManager.
Run with: pytest tests/ -v

Part of: AI Research Agent - Module 5
"""

import sys
import json
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from memory.memory_manager import MemoryManager, MEMORY_DIR


@pytest.fixture
def mem():
    """Create a fresh MemoryManager for each test (isolated)."""
    manager = MemoryManager(max_short_term=5)
    yield manager
    # Cleanup: remove test data
    for f in MEMORY_DIR.glob("*.json"):
        try:
            f.unlink()
        except Exception:
            pass


class TestShortTermMemory:
    def test_add_and_retrieve(self, mem):
        mem.add_message("user", "Hello")
        mem.add_message("assistant", "Hi there!")
        ctx = mem.get_context_window()
        assert len(ctx) == 2
        assert ctx[0]["role"] == "user"
        assert ctx[1]["role"] == "assistant"

    def test_sliding_window(self, mem):
        for i in range(15):
            mem.add_message("user", f"Message {i}")
        ctx = mem.get_context_window()
        # Should not exceed 2 * max_short_term
        assert len(ctx) <= 10

    def test_clear_short_term(self, mem):
        mem.add_message("user", "Test")
        mem.clear_short_term()
        assert len(mem.get_context_window()) == 0


class TestLongTermMemory:
    def test_remember_and_recall(self, mem):
        mem.remember("favorite_topic", "machine learning")
        result = mem.recall("favorite_topic")
        assert result == "machine learning"

    def test_recall_missing_key(self, mem):
        result = mem.recall("nonexistent_key")
        assert result is None

    def test_forget(self, mem):
        mem.remember("temp_key", "temp_value")
        success = mem.forget("temp_key")
        assert success is True
        assert mem.recall("temp_key") is None

    def test_forget_nonexistent(self, mem):
        success = mem.forget("does_not_exist")
        assert success is False

    def test_recall_all(self, mem):
        mem.remember("key1", "val1")
        mem.remember("key2", "val2")
        all_entries = mem.recall_all()
        assert "key1" in all_entries
        assert "key2" in all_entries

    def test_memory_context_format(self, mem):
        mem.remember("user_name", "Alice")
        ctx = mem.get_memory_context()
        assert "user_name" in ctx
        assert "Alice" in ctx

    def test_empty_memory_context(self, mem):
        ctx = mem.get_memory_context()
        assert ctx == ""


class TestSessionLog:
    def test_session_log_grows(self, mem):
        mem.add_message("user", "Hello")
        mem.add_message("assistant", "Hi")
        assert len(mem.session_log) == 2

    def test_stats(self, mem):
        mem.add_message("user", "Test")
        mem.remember("key", "val")
        stats = mem.get_stats()
        assert stats["short_term_messages"] == 1
        assert stats["long_term_entries"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
