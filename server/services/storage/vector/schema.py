"""LanceDB schema for embedded chunks."""

import pyarrow as pa


CHUNK_SCHEMA = pa.schema(
    [
        ("chunk_id", pa.string()),
        ("workspace_id", pa.string()),
        ("file_name", pa.string()),
        ("file_type", pa.string()),
        ("content", pa.string()),
        ("embedding", pa.list_(pa.float32())),
        ("metadata", pa.string()),
    ]
)
