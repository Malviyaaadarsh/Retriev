"""Shared text cleaning for extracted content."""

import re


def clean_text(text: str) -> str:
    """Normalize line endings, nulls, horizontal whitespace, and blank lines."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in normalized.split("\n")]

    cleaned_lines: list[str] = []
    blank_seen = False
    for line in lines:
        if line:
            cleaned_lines.append(line)
            blank_seen = False
        elif not blank_seen:
            cleaned_lines.append("")
            blank_seen = True

    return "\n".join(cleaned_lines).strip()
