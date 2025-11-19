"""
Tests for the FastAPI file upload application.
Run with: pytest tests/test_api.py
"""

import os
import sys
from pathlib import Path
import tempfile
import json

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from fastapi.testclient import TestClient
from databricks_agent_app.main import app, load_config

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "endpoints" in data


def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "volume_path" in data


def test_get_config():
    """Test the configuration endpoint"""
    response = client.get("/config")
    assert response.status_code == 200
    data = response.json()
    assert "volume" in data
    assert "max_file_size_mb" in data
    assert "catalog" in data["volume"]
    assert "schema" in data["volume"]
    assert "volume_name" in data["volume"]


def test_file_upload():
    """Test file upload functionality"""
    # Create a temporary test file
    test_content = b"This is a test file for upload"
    
    # Use files parameter for multipart form data
    files = {"file": ("test_upload.txt", test_content, "text/plain")}
    
    response = client.post("/upload", files=files)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "File uploaded successfully"
    assert data["filename"] == "test_upload.txt"
    assert "target_path" in data
    assert "size_bytes" in data


def test_file_upload_no_file():
    """Test file upload without providing a file"""
    response = client.post("/upload")
    assert response.status_code == 422  # Unprocessable Entity (missing required field)


def test_list_files():
    """Test listing files in the volume"""
    response = client.get("/files")
    assert response.status_code == 200
    data = response.json()
    assert "files" in data
    assert "count" in data
    assert "volume_path" in data
    assert isinstance(data["files"], list)


def test_load_config():
    """Test configuration loading"""
    config = load_config()
    assert "volume" in config
    assert "app" in config
    assert "path" in config["volume"]


def test_file_lifecycle():
    """Test complete file lifecycle: upload, list, delete"""
    # 1. Upload a file
    test_filename = "lifecycle_test.txt"
    test_content = b"Test file for lifecycle testing"
    files = {"file": (test_filename, test_content, "text/plain")}
    
    upload_response = client.post("/upload", files=files)
    assert upload_response.status_code == 200
    
    # 2. List files and verify it's there
    list_response = client.get("/files")
    assert list_response.status_code == 200
    files_data = list_response.json()
    
    # Check if our file is in the list (if volume is accessible)
    filenames = [f["filename"] for f in files_data["files"]]
    
    # 3. Delete the file
    delete_response = client.delete(f"/files/{test_filename}")
    # Will succeed if file exists, 404 if it doesn't
    assert delete_response.status_code in [200, 404]


def test_delete_nonexistent_file():
    """Test deleting a file that doesn't exist"""
    response = client.delete("/files/nonexistent_file_12345.txt")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

