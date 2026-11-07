
"""Local MiniLM embedding provider."""

import sys
from pathlib import Path
from typing import Any

from ..config import EmbeddingConfig
from ..exceptions import ModelLoadError
from .base_provider import EmbeddingProvider


def _bundled_model_path() -> Path:
    """Return the model path shipped alongside the packaged executable."""
    if getattr(sys, "frozen", False):
        pyinstaller_root = getattr(sys, "_MEIPASS", None)
        if pyinstaller_root:
            internal_model = (
                Path(pyinstaller_root) / "models" / "all-MiniLM-L6-v2"
            )
            if (internal_model / "model.safetensors").is_file():
                return internal_model
        return (
            Path(sys.executable).resolve().parent
            / "models"
            / "all-MiniLM-L6-v2"
        )

    project_root = Path(__file__).resolve().parents[4]
    return project_root / "models" / "all-MiniLM-L6-v2"


class MiniLMProvider(EmbeddingProvider):
    """Generate embeddings with sentence-transformers MiniLM."""

    def __init__(self, config: EmbeddingConfig | None = None) -> None:
        self.config = config or EmbeddingConfig()
        self._model: Any = None

    def _load_model(self) -> Any:
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                local_model = _bundled_model_path()
                if not (local_model / "model.safetensors").is_file():
                    raise FileNotFoundError(
                        f"Bundled embedding model not found: {local_model}"
                    )

                self._model = SentenceTransformer(
                    str(local_model),
                    local_files_only=True,
                )
            except Exception as error:
                raise ModelLoadError(
                    f"Unable to load local embedding model "
                    f"'{self.config.model_name}'"
                ) from error

        return self._model

    def embed(self, text: str) -> list[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        embeddings = self._load_model().encode(
            texts,
            batch_size=self.config.batch_size,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return [[float(value) for value in vector] for vector in embeddings]
