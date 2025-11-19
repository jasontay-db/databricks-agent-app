import json
import os
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import aiofiles


# Load configuration from project_properties.json
def load_config() -> Dict[str, Any]:
    """Load configuration from project_properties.json"""
    config_path = Path(__file__).parent.parent.parent / "project_properties.json"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, "r") as f:
        return json.load(f)


# Initialize configuration
config = load_config()
volume_config = config["volume"]
app_config = config["app"]

# Maximum file size in bytes
MAX_FILE_SIZE = app_config.get("max_file_size_mb", 100) * 1024 * 1024

# Initialize FastAPI app
app = FastAPI(
    title=app_config.get("name", "Databricks File Upload App"),
    description=app_config.get("description", "FastAPI app for uploading files to Databricks Volumes"),
    version="1.0.0"
)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Databricks File Upload API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "upload": "/upload",
            "config": "/config"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "volume_path": volume_config["path"]
    }


@app.get("/config")
async def get_config():
    """Get current configuration (volume settings)"""
    return {
        "volume": {
            "catalog": volume_config["catalog"],
            "schema": volume_config["schema"],
            "volume_name": volume_config["volume_name"],
            "path": volume_config["path"]
        },
        "max_file_size_mb": app_config.get("max_file_size_mb", 100)
    }


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file to the configured Databricks Volume.
    
    Args:
        file: The file to upload
        
    Returns:
        JSON response with upload status and file information
    """
    try:
        # Validate file is provided
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate file size
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File size ({file_size / 1024 / 1024:.2f} MB) exceeds maximum allowed size ({app_config.get('max_file_size_mb', 100)} MB)"
            )
        
        # Construct target path
        volume_path = volume_config["path"]
        target_path = os.path.join(volume_path, file.filename)
        
        # Ensure volume directory exists
        os.makedirs(volume_path, exist_ok=True)
        
        # Write file to volume
        async with aiofiles.open(target_path, "wb") as f:
            await f.write(content)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "File uploaded successfully",
                "filename": file.filename,
                "size_bytes": file_size,
                "size_mb": round(file_size / 1024 / 1024, 2),
                "target_path": target_path,
                "volume": {
                    "catalog": volume_config["catalog"],
                    "schema": volume_config["schema"],
                    "volume_name": volume_config["volume_name"]
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file: {str(e)}"
        )


@app.delete("/files/{filename}")
async def delete_file(filename: str):
    """
    Delete a file from the configured Databricks Volume.
    
    Args:
        filename: Name of the file to delete
        
    Returns:
        JSON response with deletion status
    """
    try:
        volume_path = volume_config["path"]
        target_path = os.path.join(volume_path, filename)
        
        if not os.path.exists(target_path):
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")
        
        os.remove(target_path)
        
        return {
            "message": "File deleted successfully",
            "filename": filename,
            "path": target_path
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        )


@app.get("/files")
async def list_files():
    """
    List all files in the configured Databricks Volume.
    
    Returns:
        JSON response with list of files
    """
    try:
        volume_path = volume_config["path"]
        
        if not os.path.exists(volume_path):
            return {
                "files": [],
                "count": 0,
                "volume_path": volume_path,
                "message": "Volume directory does not exist yet"
            }
        
        files = []
        for filename in os.listdir(volume_path):
            file_path = os.path.join(volume_path, filename)
            if os.path.isfile(file_path):
                file_stat = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "size_bytes": file_stat.st_size,
                    "size_mb": round(file_stat.st_size / 1024 / 1024, 2),
                    "modified": file_stat.st_mtime
                })
        
        return {
            "files": files,
            "count": len(files),
            "volume_path": volume_path
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list files: {str(e)}"
        )


def main():
    """Run the FastAPI app using uvicorn"""
    import uvicorn
    
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Starting FastAPI app on {host}:{port}")
    print(f"Volume path: {volume_config['path']}")
    
    uvicorn.run(
        "databricks_agent_app.main:app",
        host=host,
        port=port,
        reload=False
    )


if __name__ == "__main__":
    main()
