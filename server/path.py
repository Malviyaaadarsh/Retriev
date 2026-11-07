
"""Centralized filesystem paths for Retriev."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path


def get_default_data_root() -> Path:
    """Return the platform-specific default root for Retriev user data."""
    if sys.platform == "win32":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / "Retriev"
        return Path.home() / "AppData" / "Local" / "Retriev"

    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Retriev"

    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home).expanduser() / "Retriev"

    return Path.home() / ".local" / "share" / "Retriev"


def get_data_root() -> Path:
    """Resolve the user-data root, honoring the standard override."""
    configured_root = os.environ.get("RETRIEV_DATA_ROOT")
    if configured_root and configured_root.strip():
        return Path(configured_root).expanduser().resolve()

    return get_default_data_root().resolve()


@dataclass(frozen=True)
class AppPaths:
    """All persistent and temporary filesystem locations used by Retriev."""

    root: Path

    @property
    def data_dir(self) -> Path:
        # Retained temporarily to avoid mixing path refactoring with migration.
        return self.root / "data"

    @property
    def sqlite_db(self) -> Path:
        return self.data_dir / "metadata.sqlite"

    @property
    def vector_db(self) -> Path:
        return self.data_dir / "vectors"

    @property
    def workspace_dir(self) -> Path:
        return self.root / "workspaces"

    @property
    def settings_dir(self) -> Path:
        return self.root / "settings"

    @property
    def logs_dir(self) -> Path:
        return self.root / "logs"

    @property
    def temp_dir(self) -> Path:
        return self.root / "temp"

    def ensure_runtime_dirs(self) -> None:
        """Create required directories explicitly when the app starts."""
        for directory in (
            self.data_dir,
            self.vector_db,
            self.workspace_dir,
            self.settings_dir,
            self.logs_dir,
            self.temp_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)


# Constructing paths is safe: this does not create any directories.
APP_PATHS = AppPaths(root=get_data_root())

# Temporary compatibility aliases for existing imports.
RETRIEV_ROOT_STORAGE = APP_PATHS.root
DATA_ROOT = APP_PATHS.data_dir
WORKSPACE_ROOT = APP_PATHS.workspace_dir
VECTORS_ROOT = APP_PATHS.vector_db
