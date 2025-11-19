# Databricks FastAPI File Upload Application

A FastAPI-based application for uploading files to Databricks Volumes with configurable settings.

## Features

- **File Upload**: Upload files to a configured Databricks Volume
- **File Management**: List and delete files from the volume
- **Configuration**: Volume settings defined in `project_properties.json`
- **Health Check**: Monitor application status
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

## Configuration

The application reads its configuration from `project_properties.json`:

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

### Configuration Parameters

- `volume.catalog`: Databricks Unity Catalog name
- `volume.schema`: Schema within the catalog
- `volume.volume_name`: Name of the volume
- `volume.path`: Full path to the volume (format: `/Volumes/{catalog}/{schema}/{volume_name}`)
- `app.max_file_size_mb`: Maximum allowed file size in MB (default: 100)

## Installation

### Prerequisites

1. Python 3.11 or higher
2. UV package manager (recommended) or pip
3. Databricks workspace with Unity Catalog enabled
4. A Databricks Volume created for file storage

### Install Dependencies

Using UV:
```bash
uv pip install -e .
```

Or using pip:
```bash
pip install -r requirements.txt
```

## Running the Application

### Local Development

Run the FastAPI application locally:

```bash
python src/databricks_agent_app/main.py
```

Or using the app.py entry point:

```bash
python app.py
```

The application will start on `http://0.0.0.0:8000` by default.

### Custom Host and Port

Set environment variables to customize:

```bash
export HOST="127.0.0.1"
export PORT="8080"
python app.py
```

### Databricks Deployment

Deploy using Databricks bundles:

```bash
# Deploy to development
databricks bundle deploy --target dev

# Deploy to production
databricks bundle deploy --target prod
```

## API Endpoints

### Root Endpoint
- **GET** `/`
- Returns API information and available endpoints

### Health Check
- **GET** `/health`
- Returns application health status and volume path

### Configuration
- **GET** `/config`
- Returns current volume and app configuration

### Upload File
- **POST** `/upload`
- Upload a file to the configured Databricks Volume
- **Request**: `multipart/form-data` with file field
- **Response**: File information and upload status

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@/path/to/your/file.txt"
```

**Example using Python:**
```python
import requests

url = "http://localhost:8000/upload"
files = {"file": open("example.txt", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

### List Files
- **GET** `/files`
- List all files in the configured volume
- **Response**: Array of file information (name, size, modified date)

### Delete File
- **DELETE** `/files/{filename}`
- Delete a specific file from the volume
- **Path Parameter**: `filename` - name of the file to delete

## API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Testing

### Using curl

Upload a file:
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@test.txt" \
  -H "accept: application/json"
```

List files:
```bash
curl -X GET "http://localhost:8000/files" \
  -H "accept: application/json"
```

Delete a file:
```bash
curl -X DELETE "http://localhost:8000/files/test.txt" \
  -H "accept: application/json"
```

### Using the Test Script

A test script is provided in `tests/test_api.py`:

```bash
pytest tests/test_api.py
```

## Volume Setup in Databricks

Before using the application, ensure you have a volume created in your Databricks workspace:

```sql
-- Create catalog (if not exists)
CREATE CATALOG IF NOT EXISTS main;

-- Create schema (if not exists)
CREATE SCHEMA IF NOT EXISTS main.default;

-- Create volume for file uploads
CREATE VOLUME IF NOT EXISTS main.default.uploaded_files;
```

Then update `project_properties.json` with the correct volume path.

## Error Handling

The application handles various error scenarios:

- **400 Bad Request**: No file provided
- **404 Not Found**: File not found for deletion
- **413 Payload Too Large**: File exceeds maximum size limit
- **500 Internal Server Error**: Server-side errors (with detailed messages)

## Security Considerations

1. **File Size Limits**: Configure appropriate limits in `project_properties.json`
2. **Authentication**: Add authentication middleware for production use
3. **File Validation**: Consider adding file type validation
4. **Volume Permissions**: Ensure proper access controls on the Databricks Volume

## Development

### Project Structure

```
databricks_agent_app/
├── project_properties.json          # Configuration file
├── app.py                          # Databricks App entry point
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Project metadata
├── src/
│   └── databricks_agent_app/
│       ├── __init__.py
│       └── main.py                 # FastAPI application
├── tests/
│   └── test_api.py                 # API tests
└── resources/
    └── databricks_agent_app.app.yml # Databricks App config
```

## Support

For issues or questions:
- Check the API documentation at `/docs`
- Review Databricks Volumes documentation
- Verify volume permissions and paths

## License

Copyright © Databricks

