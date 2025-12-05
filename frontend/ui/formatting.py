"""Utility functions for parsing currency values and sanitizing AI text responses."""
from typing import Optional
import re


def parse_brl_amount(raw: str) -> Optional[float]:
    """Parses a BRL-formatted string into a numeric float value."""
    text = raw.strip().replace("R$", "").replace(" ", "")
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")

    try:
        value = float(text)
        if value <= 0:
            return None
        return value
    except ValueError:
        return None


def sanitize_ai_reply(text: str) -> str:
    """Removes formatting artifacts, Markdown, HTML tags, and list symbols from AI responses."""
    if not isinstance(text, str):
        text = str(text)

    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

    text = text.replace("`", "")

    text = re.sub(r"<[^>]+>", "", text)

    text = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)

    lines = []
    for line in text.splitlines():
        line = re.sub(r"^\s*[-*]\s+", "", line)
        lines.append(line)
    text = "\n".join(lines)

    text = re.sub(r"[ ]{2,}", " ", text)

    return text.strip()
