"""Small, deterministic cleaning rules used by TextCleaner."""

import re

def remove_null_chars(text: str) -> str:
    return text.replace("\x00", "")


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def collapse_spaces(text: str) -> str:
    """Collapse repeated spaces outside fenced code blocks."""
    parts = re.split(r"(```.*?```)", text, flags=re.DOTALL)
    for index in range(0, len(parts), 2):
        parts[index] = re.sub(r"[ \t]{2,}", " ", parts[index])
    return "".join(parts)


def compress_blank_lines(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text)


def trim_edges(text: str) -> str:
    return text.strip()
