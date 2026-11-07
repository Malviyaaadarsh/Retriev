"""DOCX extraction using python-docx."""

from pathlib import Path

from docx import Document

from ..base.extractor import BaseExtractor
from ..base.models import DocumentUnit
from ..cleaner import clean_text


class DocxExtractor(BaseExtractor):
    """Extract non-empty paragraphs in their source order."""

    def extract(self, file_path: Path) -> list[DocumentUnit]:
        document = Document(file_path)
        paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
        content = clean_text("\n".join(paragraphs))
        return [
            DocumentUnit(
                content=content,
                metadata={"file_name": file_path.name, "file_type": "docx"},
            )
        ] if content else []
