"""PDF extraction using PyMuPDF."""

from pathlib import Path

import fitz

from ..base.extractor import BaseExtractor
from ..base.models import DocumentUnit
from ..cleaner import clean_text


class PDFExtractor(BaseExtractor):
    """Extract one cleaned unit per non-empty PDF page."""

    def extract(self, file_path: Path) -> list[DocumentUnit]:
        units: list[DocumentUnit] = []
        with fitz.open(file_path) as document:
            for page_number, page in enumerate(document, start=1):
                content = clean_text(page.get_text())
                if content:
                    units.append(
                        DocumentUnit(
                            content=content,
                            metadata={
                                "file_name": file_path.name,
                                "file_type": "pdf",
                                "page": page_number,
                            },
                        )
                    )
        return units
