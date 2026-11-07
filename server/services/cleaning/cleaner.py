"""Deterministic text cleaner."""

from .models import CleaningResult
from .rules import (
    collapse_spaces,
    compress_blank_lines,
    normalize_newlines,
    remove_null_chars,
    trim_edges,
)


class TextCleaner:
    """Apply the version-one cleaning rules in a fixed order."""

    def clean_with_result(self, text: str | None) -> tuple[str, CleaningResult]:
        original = text if isinstance(text, str) else ""
        cleaned = remove_null_chars(original)
        cleaned = normalize_newlines(cleaned)
        cleaned = collapse_spaces(cleaned)
        cleaned = compress_blank_lines(cleaned)
        cleaned = trim_edges(cleaned)
        result = CleaningResult(
            original_length=len(original),
            cleaned_length=len(cleaned),
            characters_removed=len(original) - len(cleaned),
        )
        return cleaned, result

    def clean(self, text: str | None) -> str:
        """Return normalized text; malformed or empty input becomes empty text."""
        return self.clean_with_result(text)[0]
