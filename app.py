#!/usr/bin/env python3
"""
Databricks App entry point for FastAPI application.
This file is used to run the FastAPI app in Databricks Apps environment.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from databricks_agent_app.main import app

# This is used by Databricks Apps to serve the FastAPI application
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Starting Databricks FastAPI app on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )

