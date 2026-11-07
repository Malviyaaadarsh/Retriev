"""Progress state for a chat request."""

from dataclasses import dataclass, field


@dataclass
class ChatProgress:
    """Current chat stage, suitable for API or UI status reporting."""

    current_stage: str = "Receiving Query"
    percentage: float = 0.0
    errors: list[str] = field(default_factory=list)

    def update(self, stage: str, percentage: float) -> None:
        self.current_stage = stage
        self.percentage = percentage
