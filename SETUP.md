# Setup Guide: Databricks FastAPI File Upload App

This guide will walk you through setting up and deploying the FastAPI file upload application to Databricks.

## Prerequisites

1. **Databricks Workspace**: Access to a Databricks workspace with Unity Catalog enabled
2. **Databricks CLI**: Installed and configured
3. **Python 3.11+**: For local development
4. **UV Package Manager**: Recommended for dependency management

## Step 1: Create Databricks Volume

First, create a volume in your Databricks workspace to store uploaded files.

### Option A: Using SQL in Databricks Workspace

1. Open your Databricks workspace
2. Navigate to **SQL Editor** or open a notebook
3. Run the following SQL commands:

```sql
-- Create catalog (if it doesn't exist)
CREATE CATALOG IF NOT EXISTS main;

-- Create schema (if it doesn't exist)
CREATE SCHEMA IF NOT EXISTS main.default;

-- Create volume for file uploads
CREATE VOLUME IF NOT EXISTS main.default.uploaded_files;

-- Verify the volume was created
SHOW VOLUMES IN main.default;

-- Check permissions
DESCRIBE VOLUME EXTENDED main.default.uploaded_files;
```

### Option B: Using Databricks CLI

```bash
# Create the volume using CLI
databricks volumes create main.default.uploaded_files

# List volumes to verify
databricks volumes list --catalog main --schema default
```

## Step 2: Configure Application

Edit `project_properties.json` to match your Databricks workspace and volume settings:

```json
{
  "volume": {
    "catalog": "main",
    "schema": "default",
    "volume_name": "uploaded_files",
    "path": "/Volumes/main/default/uploaded_files"
  },
  "app": {
    "name": "databricks-file-upload-app",
    "description": "FastAPI app for uploading files to Databricks Volumes",
    "max_file_size_mb": 100
  }
}
```

**Important**: Update these values if you're using a different catalog, schema, or volume name.

## Step 3: Install Dependencies

### Using UV (Recommended)

```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv pip install -e ".[dev]"
```

### Using pip

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

## Step 4: Test Locally

Before deploying to Databricks, test the application locally:

```bash
# Start the FastAPI server
python app.py
```

The server will start at `http://localhost:8000`

### Test with the Example Script

In a new terminal:

```bash
# Run the example upload script
python examples/upload_example.py
```

### Test with curl

```bash
# Create a test file
echo "Hello Databricks!" > test.txt

# Upload the file
curl -X POST "http://localhost:8000/upload" \
  -F "file=@test.txt"

# List files
curl http://localhost:8000/files

# Delete the file
curl -X DELETE "http://localhost:8000/files/test.txt"
```

### Access API Documentation

Open your browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Step 5: Deploy to Databricks

### Configure Databricks CLI

```bash
# Configure authentication
databricks configure

# Or use environment variables
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="your-token"
```

### Deploy the Application

```bash
# Build the wheel package
uv build --wheel

# Deploy to development
databricks bundle deploy --target dev

# Or deploy to production
databricks bundle deploy --target prod
```

## Step 6: Run on Databricks

### Option A: Run as a Job

```bash
# Run the deployed job
databricks bundle run
```

### Option B: Deploy as Databricks App

If using Databricks Apps (serverless):

1. The app will be deployed according to `resources/databricks_agent_app.app.yml`
2. Access the app URL provided after deployment
3. The app will run continuously and auto-scale

## Configuration Options

### Volume Configuration

Modify `project_properties.json` to change volume settings:

- **catalog**: Unity Catalog name
- **schema**: Schema within the catalog
- **volume_name**: Name of the volume
- **path**: Full volume path (must match catalog/schema/volume_name)

### App Configuration

- **max_file_size_mb**: Maximum upload size in megabytes (default: 100)
- **name**: Application name
- **description**: Application description

### Environment Variables

Set these environment variables to customize runtime behavior:

```bash
# Server host
export HOST="0.0.0.0"

# Server port
export PORT="8000"
```

## Volume Permissions

Ensure appropriate permissions on the volume:

```sql
-- Grant permissions to a user
GRANT ALL PRIVILEGES ON VOLUME main.default.uploaded_files 
TO `user@example.com`;

-- Grant permissions to a group
GRANT ALL PRIVILEGES ON VOLUME main.default.uploaded_files 
TO `data-engineers`;

-- Check current permissions
SHOW GRANTS ON VOLUME main.default.uploaded_files;
```

## Troubleshooting

### Issue: "Volume not found" or "Permission denied"

**Solution:**
1. Verify the volume exists: `SHOW VOLUMES IN main.default;`
2. Check your permissions: `SHOW GRANTS ON VOLUME main.default.uploaded_files;`
3. Ensure the path in `project_properties.json` is correct

### Issue: "Failed to write to volume"

**Solution:**
1. Verify you have WRITE permissions on the volume
2. Check if the volume path is accessible from your environment
3. For local testing, the path might need to be a local directory

### Issue: Import errors when running

**Solution:**
```bash
# Reinstall dependencies
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

### Issue: File upload fails with 413 error

**Solution:**
- Increase `max_file_size_mb` in `project_properties.json`
- Check if there are any workspace-level file size limits

## Production Considerations

### Security

1. **Add Authentication**: Implement authentication middleware
```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    token: str = Security(security)
):
    # Validate token
    # ... upload logic
```

2. **File Type Validation**: Add validation for allowed file types
3. **Rate Limiting**: Implement rate limiting for uploads
4. **CORS**: Configure CORS if accessed from web browsers

### Monitoring

1. Add logging:
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    logger.info(f"Upload started: {file.filename}")
    # ... upload logic
    logger.info(f"Upload completed: {file.filename}")
```

2. Add metrics and health checks
3. Set up alerts for failures

### Scaling

1. For Databricks Apps, scaling is automatic
2. For job-based deployment, consider cluster size and concurrency
3. Monitor volume storage usage

## Next Steps

1. **Customize the API**: Add custom endpoints for your use case
2. **Add File Processing**: Process uploaded files with Spark
3. **Integration**: Integrate with Delta Lake or other Databricks features
4. **CI/CD**: Set up automated deployment pipelines

## Resources

- [Databricks Volumes Documentation](https://docs.databricks.com/en/connect/unity-catalog/volumes.html)
- [Databricks Apps Documentation](https://docs.databricks.com/en/dev-tools/databricks-apps/index.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Databricks CLI Documentation](https://docs.databricks.com/dev-tools/cli/index.html)

## Support

For issues or questions:
- Check the API documentation at `/docs` endpoint
- Review Databricks workspace logs
- Consult the Databricks documentation

---

**Project maintained by**: jason.taylor@databricks.com

