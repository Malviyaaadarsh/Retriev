"""Progress state emitted while ingesting a workspace."""

from dataclasses import dataclass, field


@dataclass
class PipelineProgress:
    """Mutable progress snapshot suitable for API or UI integration."""

    current_file: str | None = None
    total_files: int = 0
    current_stage: str | None = None
    percentage: float = 0.0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def update(
        self,
        *,
        current_file: str | None = None,
        current_stage: str | None = None,
        file_index: int | None = None,
    ) -> None:
        if current_file is not None:
            self.current_file = current_file
        if current_stage is not None:
            self.current_stage = current_stage
        if file_index is not None and self.total_files:
            self.percentage = round((file_index / self.total_files) * 100, 2)
