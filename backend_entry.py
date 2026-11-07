"""Standalone entry point for the packaged Retriev backend."""
import os

import uvicorn
from server.app import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=int(os.getenv("RETRIEV_PORT", "8000")),
        reload=False,
        log_level="info",
    )
