"""Configuration for document ingestion orchestration."""

from dataclasses import dataclass, field


@dataclass
class IngestionPipelineConfig:
    """Runtime options for the version-one ingestion pipeline."""

    continue_on_error: bool = True
    verbose_logging: bool = True
    supported_extensions: list[str] = field(
        default_factory=lambda: ["pdf", "txt", "md", "docx", "csv"]
    )

    def __post_init__(self) -> None:
        self.supported_extensions = [
            extension.lower().lstrip(".") for extension in self.supported_extensions
        ]
