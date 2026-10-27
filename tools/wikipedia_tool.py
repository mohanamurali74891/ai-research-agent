"""
tools/wikipedia_tool.py
────────────────────────────────────────────────
Tool: Wikipedia lookup for authoritative summaries
Part of: AI Research Agent - Module 5
"""

import wikipediaapi


def get_wikipedia_summary(topic: str, lang: str = "en", sentences: int = 5) -> str:
    """
    Fetch a Wikipedia summary for a given topic.

    Args:
        topic: The topic to search on Wikipedia
        lang: Language code (default 'en')
        sentences: Number of summary sentences to return

    Returns:
        Summary string or error message
    """
    wiki = wikipediaapi.Wikipedia(
        user_agent="AIResearchAgent/1.0 (module5-project)",
        language=lang
    )
    page = wiki.page(topic)

    if not page.exists():
        return f"No Wikipedia article found for '{topic}'."

    # Return first N sentences of the summary
    summary = page.summary
    sentences_list = summary.split(". ")
    truncated = ". ".join(sentences_list[:sentences])
    if not truncated.endswith("."):
        truncated += "."

    return f"**Wikipedia: {page.title}**\nURL: {page.fullurl}\n\n{truncated}"


def get_wikipedia_sections(topic: str) -> str:
    """
    List available sections in a Wikipedia article.

    Args:
        topic: Wikipedia article title

    Returns:
        String listing all top-level sections
    """
    wiki = wikipediaapi.Wikipedia(
        user_agent="AIResearchAgent/1.0 (module5-project)",
        language="en"
    )
    page = wiki.page(topic)

    if not page.exists():
        return f"No Wikipedia article found for '{topic}'."

    sections = [s.title for s in page.sections]
    return f"Sections in '{page.title}':\n" + "\n".join(f"• {s}" for s in sections)
