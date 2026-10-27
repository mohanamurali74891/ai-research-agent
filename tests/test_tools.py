"""
tests/test_tools.py
────────────────────────────────────────────────
Unit tests for all agent tools.
Run with: pytest tests/ -v

Part of: AI Research Agent - Module 5
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from tools.calculator import calculate, unit_convert
from tools.summarizer import chunk_text, clean_text
from tools.web_search import format_search_results


# ── Calculator Tests ──────────────────────────────────────────────────────────

class TestCalculator:
    def test_basic_arithmetic(self):
        result = calculate("2 + 2")
        assert "4" in result

    def test_power(self):
        result = calculate("2 ** 10")
        assert "1024" in result

    def test_sqrt(self):
        result = calculate("sqrt(144)")
        assert "12" in result

    def test_pi(self):
        result = calculate("pi * 2")
        assert "6.28" in result

    def test_division_by_zero(self):
        result = calculate("1 / 0")
        assert "zero" in result.lower() or "error" in result.lower()

    def test_disallowed_identifier(self):
        result = calculate("__import__('os').system('ls')")
        assert "Error" in result or "Disallowed" in result

    def test_complex_expression(self):
        result = calculate("sqrt(16) + log10(1000) * 2")
        assert "10.0" in result or "10" in result


class TestUnitConvert:
    def test_km_to_miles(self):
        result = unit_convert(100, "km", "miles")
        assert "62.1" in result

    def test_celsius_to_fahrenheit(self):
        result = unit_convert(100, "celsius", "fahrenheit")
        assert "212" in result

    def test_kg_to_pounds(self):
        result = unit_convert(1, "kg", "pounds")
        assert "2.2" in result

    def test_unsupported_unit(self):
        result = unit_convert(1, "parsec", "lightyear")
        assert "not supported" in result.lower()


# ── Summarizer Tests ──────────────────────────────────────────────────────────

class TestSummarizer:
    def test_chunk_short_text(self):
        text = "Hello world."
        chunks = chunk_text(text, max_chars=1000)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_long_text(self):
        # Create text that is definitely over 100 chars when split
        paragraphs = [f"Paragraph {i}: " + "x" * 50 for i in range(10)]
        text = "\n\n".join(paragraphs)
        chunks = chunk_text(text, max_chars=200)
        assert len(chunks) > 1

    def test_clean_text_removes_extra_whitespace(self):
        text = "Hello   world\n\n\n\nFoo"
        result = clean_text(text)
        assert "   " not in result
        assert "\n\n\n" not in result


# ── Web Search Format Tests ───────────────────────────────────────────────────

class TestWebSearchFormat:
    def test_format_empty(self):
        result = format_search_results([])
        assert "No results" in result

    def test_format_results(self):
        mock = [
            {"title": "AI News", "href": "https://example.com", "body": "Latest AI developments"}
        ]
        result = format_search_results(mock)
        assert "AI News" in result
        assert "https://example.com" in result
        assert "Latest AI developments" in result

    def test_format_multiple_results(self):
        mock = [
            {"title": f"Result {i}", "href": f"https://example{i}.com", "body": f"Body {i}"}
            for i in range(3)
        ]
        result = format_search_results(mock)
        assert "[1]" in result
        assert "[2]" in result
        assert "[3]" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
