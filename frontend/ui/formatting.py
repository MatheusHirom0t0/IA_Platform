"""TODO"""
from typing import Optional
import re


def parse_brl_amount(raw: str) -> Optional[float]:
    """TODO"""
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
    """TODO"""
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
