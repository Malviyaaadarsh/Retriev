"""Storage-specific exceptions."""


class StorageError(RuntimeError):
    """Base storage error."""


class WorkspaceNotFound(StorageError):
    """Raised when a workspace does not exist."""


class ChatNotFound(StorageError):
    """Raised when a chat does not exist."""


class VectorStoreError(StorageError):
    """Raised when vector storage fails."""


class DatabaseError(StorageError):
    """Raised when relational persistence fails."""
