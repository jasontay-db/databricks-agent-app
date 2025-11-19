import json
import os
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
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


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint serving the upload UI"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Databricks File Upload</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                padding: 40px;
                max-width: 600px;
                width: 100%;
            }
            
            h1 {
                color: #333;
                margin-bottom: 10px;
                font-size: 28px;
            }
            
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 14px;
            }
            
            .upload-area {
                border: 3px dashed #667eea;
                border-radius: 15px;
                padding: 40px;
                text-align: center;
                background: #f8f9ff;
                transition: all 0.3s ease;
                cursor: pointer;
                margin-bottom: 20px;
            }
            
            .upload-area:hover {
                border-color: #764ba2;
                background: #f0f1ff;
            }
            
            .upload-area.dragover {
                border-color: #764ba2;
                background: #e8e9ff;
                transform: scale(1.02);
            }
            
            .upload-icon {
                font-size: 48px;
                margin-bottom: 15px;
            }
            
            .upload-text {
                color: #667eea;
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 8px;
            }
            
            .upload-hint {
                color: #999;
                font-size: 14px;
            }
            
            .file-input {
                display: none;
            }
            
            .btn-upload {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px 40px;
                border-radius: 30px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                width: 100%;
            }
            
            .btn-upload:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
            }
            
            .btn-upload:disabled {
                background: #ccc;
                cursor: not-allowed;
                transform: none;
            }
            
            .selected-file {
                background: #e8f5e9;
                border: 1px solid #4caf50;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
                display: none;
            }
            
            .selected-file.show {
                display: block;
            }
            
            .file-name {
                color: #2e7d32;
                font-weight: 600;
                margin-bottom: 5px;
            }
            
            .file-size {
                color: #666;
                font-size: 14px;
            }
            
            .message {
                padding: 15px;
                border-radius: 10px;
                margin-top: 20px;
                display: none;
            }
            
            .message.show {
                display: block;
            }
            
            .message.success {
                background: #e8f5e9;
                border: 1px solid #4caf50;
                color: #2e7d32;
            }
            
            .message.error {
                background: #ffebee;
                border: 1px solid #f44336;
                color: #c62828;
            }
            
            .progress-bar {
                width: 100%;
                height: 8px;
                background: #e0e0e0;
                border-radius: 4px;
                overflow: hidden;
                margin-top: 15px;
                display: none;
            }
            
            .progress-bar.show {
                display: block;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                width: 0%;
                transition: width 0.3s ease;
            }
            
            .file-list {
                margin-top: 30px;
            }
            
            .file-list h2 {
                font-size: 20px;
                color: #333;
                margin-bottom: 15px;
            }
            
            .file-item {
                background: #f8f9fa;
                padding: 12px 15px;
                border-radius: 8px;
                margin-bottom: 8px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .file-item-name {
                font-weight: 500;
                color: #333;
            }
            
            .file-item-size {
                color: #666;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📁 Databricks File Upload</h1>
            <p class="subtitle">Upload files to UC Volume: /Volumes/users/jason_taylor/agent_app_uploads</p>
            
            <div class="upload-area" id="uploadArea">
                <div class="upload-icon">☁️</div>
                <div class="upload-text">Drop files here or click to browse</div>
                <div class="upload-hint">Maximum file size: 100 MB</div>
            </div>
            
            <input type="file" id="fileInput" class="file-input" multiple>
            
            <div class="selected-file" id="selectedFile">
                <div class="file-name" id="fileName"></div>
                <div class="file-size" id="fileSize"></div>
            </div>
            
            <button class="btn-upload" id="uploadBtn" disabled>Upload File</button>
            
            <div class="progress-bar" id="progressBar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            
            <div class="message" id="message"></div>
            
            <div class="file-list" id="fileList"></div>
        </div>
        
        <script>
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            const uploadBtn = document.getElementById('uploadBtn');
            const selectedFile = document.getElementById('selectedFile');
            const fileName = document.getElementById('fileName');
            const fileSize = document.getElementById('fileSize');
            const message = document.getElementById('message');
            const progressBar = document.getElementById('progressBar');
            const progressFill = document.getElementById('progressFill');
            const fileList = document.getElementById('fileList');
            
            let currentFile = null;
            
            // Click to browse
            uploadArea.addEventListener('click', () => {
                fileInput.click();
            });
            
            // Drag and drop
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                
                if (e.dataTransfer.files.length > 0) {
                    handleFileSelect(e.dataTransfer.files[0]);
                }
            });
            
            // File input change
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    handleFileSelect(e.target.files[0]);
                }
            });
            
            function handleFileSelect(file) {
                currentFile = file;
                
                // Display file info
                fileName.textContent = `📄 ${file.name}`;
                fileSize.textContent = `Size: ${formatFileSize(file.size)}`;
                selectedFile.classList.add('show');
                
                // Enable upload button
                uploadBtn.disabled = false;
                
                // Hide previous messages
                message.classList.remove('show');
            }
            
            function formatFileSize(bytes) {
                if (bytes === 0) return '0 Bytes';
                const k = 1024;
                const sizes = ['Bytes', 'KB', 'MB', 'GB'];
                const i = Math.floor(Math.log(bytes) / Math.log(k));
                return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
            }
            
            // Upload file
            uploadBtn.addEventListener('click', async () => {
                if (!currentFile) return;
                
                const formData = new FormData();
                formData.append('file', currentFile);
                
                try {
                    uploadBtn.disabled = true;
                    uploadBtn.textContent = 'Uploading...';
                    progressBar.classList.add('show');
                    progressFill.style.width = '50%';
                    
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    progressFill.style.width = '100%';
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        showMessage(`✅ File uploaded successfully: ${result.filename}`, 'success');
                        
                        // Reset form
                        currentFile = null;
                        fileInput.value = '';
                        selectedFile.classList.remove('show');
                        uploadBtn.textContent = 'Upload File';
                        
                        // Refresh file list
                        await loadFileList();
                    } else {
                        showMessage(`❌ Error: ${result.detail}`, 'error');
                        uploadBtn.disabled = false;
                        uploadBtn.textContent = 'Upload File';
                    }
                } catch (error) {
                    showMessage(`❌ Upload failed: ${error.message}`, 'error');
                    uploadBtn.disabled = false;
                    uploadBtn.textContent = 'Upload File';
                } finally {
                    setTimeout(() => {
                        progressBar.classList.remove('show');
                        progressFill.style.width = '0%';
                    }, 1000);
                }
            });
            
            function showMessage(text, type) {
                message.textContent = text;
                message.className = `message ${type} show`;
            }
            
            // Load and display file list
            async function loadFileList() {
                try {
                    const response = await fetch('/files');
                    const result = await response.json();
                    
                    if (result.files && result.files.length > 0) {
                        let html = '<h2>📂 Uploaded Files</h2>';
                        result.files.forEach(file => {
                            html += `
                                <div class="file-item">
                                    <span class="file-item-name">${file.filename}</span>
                                    <span class="file-item-size">${formatFileSize(file.size_bytes)}</span>
                                </div>
                            `;
                        });
                        fileList.innerHTML = html;
                    }
                } catch (error) {
                    console.error('Failed to load file list:', error);
                }
            }
            
            // Load file list on page load
            loadFileList();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "message": "Databricks File Upload API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "upload": "/upload",
            "files": "/files",
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
