"""Extractor interface."""

from abc import ABC, abstractmethod
from pathlib import Path

from .models import DocumentUnit


class BaseExtractor(ABC):
    """Interface implemented by each supported file-type extractor."""

    @abstractmethod
    def extract(self, file_path: Path) -> list[DocumentUnit]:
        """Extract document units from ``file_path``."""
