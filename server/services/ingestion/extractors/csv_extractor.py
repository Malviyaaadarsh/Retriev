"""CSV extraction using pandas."""

from pathlib import Path

import pandas as pd

from ..base.extractor import BaseExtractor
from ..base.models import DocumentUnit
from ..cleaner import clean_text


class CSVExtractor(BaseExtractor):
    """Convert each CSV row into a separately retrievable human-readable record."""

    def extract(self, file_path: Path) -> list[DocumentUnit]:
        frame = pd.read_csv(file_path, dtype=str, keep_default_na=False)
        units: list[DocumentUnit] = []
        for row_number, (_, row) in enumerate(frame.iterrows(), start=1):
            content = "\n".join(f"{column}: {row[column]}" for column in frame.columns)
            units.append(
                DocumentUnit(
                    content=clean_text(content),
                    metadata={
                        "file_name": file_path.name,
                        "file_type": "csv",
                        "row": row_number,
                    },
                )
            )
        return units
