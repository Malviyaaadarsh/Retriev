"""Markdown extraction that retains Markdown syntax."""

from pathlib import Path

from ..base.extractor import BaseExtractor
from ..base.models import DocumentUnit
from ..cleaner import clean_text


class MarkdownExtractor(BaseExtractor):
    """Read Markdown as text without interpreting or stripping its syntax."""

    def extract(self, file_path: Path) -> list[DocumentUnit]:
        content = clean_text(file_path.read_text(encoding="utf-8-sig"))
        return [
            DocumentUnit(
                content=content,
                metadata={"file_name": file_path.name, "file_type": "md"},
            )
        ] if content else []
