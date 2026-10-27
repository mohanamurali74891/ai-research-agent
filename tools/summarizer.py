"""
tools/summarizer.py
────────────────────────────────────────────────
Tool: Text summarization helper (used internally by the agent)
Part of: AI Research Agent - Module 5
"""

import re


def chunk_text(text: str, max_chars: int = 3000) -> list[str]:
    """
    Split long text into manageable chunks.

    Args:
        text: Input text to chunk
        max_chars: Max characters per chunk

    Returns:
        List of text chunks
    """
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) < max_chars:
            current += para + "\n\n"
        else:
            if current:
                chunks.append(current.strip())
            current = para + "\n\n"

    if current:
        chunks.append(current.strip())

    return chunks if chunks else [text]


def clean_text(text: str) -> str:
    """Remove excessive whitespace and normalize line endings."""
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def extract_key_points(text: str) -> str:
    """
    Heuristically extract sentence fragments that look like key statements.
    This is a lightweight pre-pass — the LLM does the real summarization.
    """
    sentences = re.split(r"(?<=[.!?])\s+", text)
    # Prefer longer, informative sentences
    key = [s for s in sentences if len(s) > 40][:10]
    return " ".join(key)
