"""Document-level cleaning service."""

import logging
from time import perf_counter

from server.services.ingestion.base.models import DocumentUnit, ExtractedDocument

from .cleaner import TextCleaner
from .models import CleanedDocument

logger = logging.getLogger(__name__)


class CleaningService:
    """Clean every extracted unit while preserving its metadata."""

    def __init__(self, cleaner: TextCleaner | None = None) -> None:
        self._cleaner = cleaner or TextCleaner()

    def clean_document(self, extracted_document: ExtractedDocument) -> CleanedDocument:
        started = perf_counter()
        cleaned_units: list[DocumentUnit] = []
        before = 0
        after = 0

        for unit in extracted_document.units:
            content = unit.content if isinstance(unit.content, str) else ""
            cleaned_content, result = self._cleaner.clean_with_result(content)
            before += result.original_length
            after += result.cleaned_length
            cleaned_units.append(
                DocumentUnit(content=cleaned_content, metadata=dict(unit.metadata))
            )

        logger.info(
            "File cleaned: %s | Before: %d chars | After: %d chars | Removed: %d chars | Time: %.4fs",
            extracted_document.file_name,
            before,
            after,
            before - after,
            perf_counter() - started,
        )
        return CleanedDocument(
            file_name=extracted_document.file_name,
            file_path=extracted_document.file_path,
            file_type=extracted_document.file_type,
            units=cleaned_units,
        )
