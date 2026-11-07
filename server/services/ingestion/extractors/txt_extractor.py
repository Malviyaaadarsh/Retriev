"""Plain-text extraction."""

from pathlib import Path

from ..base.extractor import BaseExtractor
from ..base.models import DocumentUnit
from ..cleaner import clean_text


class TXTExtractor(BaseExtractor):
    """Read UTF-8 text, falling back to a permissive legacy decoding."""

    def extract(self, file_path: Path) -> list[DocumentUnit]:
        try:
            content = file_path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            content = file_path.read_text(encoding="utf-8", errors="replace")

        content = clean_text(content)
        return [
            DocumentUnit(
                content=content,
                metadata={"file_name": file_path.name, "file_type": "txt"},
            )
        ] if content else []
