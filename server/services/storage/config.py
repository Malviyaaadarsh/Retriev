"""Storage configuration."""

from dataclasses import dataclass


@dataclass
class StorageConfig:
    vector_db_path: str
    sqlite_db_path: str
