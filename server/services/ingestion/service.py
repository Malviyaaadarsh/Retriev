"""Public extraction service."""

from pathlib import Path

from .base.models import ExtractedDocument
from .factory import ExtractorFactory


class ExtractionService:
    """Validate a path, extract it with the registered extractor, and return the model."""

    @staticmethod
    def extract(path: str | Path) -> ExtractedDocument:
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")
        if not file_path.is_file():
            raise IsADirectoryError(f"Expected a file, got: {file_path}")

        file_type = file_path.suffix.lower().lstrip(".")
        units = ExtractorFactory.get(file_path).extract(file_path)
        return ExtractedDocument(
            file_name=file_path.name,
            file_path=str(file_path.resolve()),
            file_type=file_type,
            units=units,
        )
