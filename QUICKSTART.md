# 🚀 Quick Start Guide

Get the Databricks FastAPI File Upload App running in 5 minutes!

## Prerequisites Check

- ✅ Python 3.11 or higher
- ✅ Databricks workspace access (for deployment)
- ✅ UV or pip package manager

## Step 1: Install Dependencies (1 minute)

```bash
# Option A: Using UV (recommended)
uv pip install -e ".[dev]"

# Option B: Using pip
pip install -e ".[dev]"
```

## Step 2: Start the App (30 seconds)

```bash
# Quick start with the script
./start_app.sh

# Or manually
python app.py
```

✅ **App is now running at**: http://localhost:8000

## Step 3: Test the API (2 minutes)

### Option A: Use the Example Script

```bash
# In a new terminal
python examples/upload_example.py
```

This will:
- Check API health ✓
- Create and upload a test file ✓
- List files in the volume ✓
- Optionally delete the test file ✓

### Option B: Use the Browser

Open these URLs in your browser:

1. **API Documentation**: http://localhost:8000/docs
2. **Try the upload**: Click "POST /upload" → "Try it out" → Upload a file
3. **List files**: Click "GET /files" → "Try it out" → Execute

### Option C: Use curl

```bash
# Create a test file
echo "Hello Databricks!" > test.txt

# Upload it
curl -X POST http://localhost:8000/upload -F "file=@test.txt"

# List files
curl http://localhost:8000/files

# Check health
curl http://localhost:8000/health
```

## 🎉 That's It!

You now have a working FastAPI file upload application!

## Next Steps

### 1. Configure for Databricks Volume

Edit `project_properties.json` to point to your Databricks Volume:

```json
{
  "volume": {
    "catalog": "main",
    "schema": "default", 
    "volume_name": "uploaded_files",
    "path": "/Volumes/main/default/uploaded_files"
  }
}
```

### 2. Create the Volume in Databricks

Run this SQL in your Databricks workspace:

```sql
CREATE VOLUME IF NOT EXISTS main.default.uploaded_files;
```

### 3. Deploy to Databricks

```bash
# Deploy to development
databricks bundle deploy --target dev

# Or deploy to production
databricks bundle deploy --target prod
```

## API Endpoints Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/config` | GET | Current configuration |
| `/upload` | POST | Upload a file |
| `/files` | GET | List all files |
| `/files/{filename}` | DELETE | Delete a file |

## Common Commands

```bash
# Start the app
python app.py

# Run tests
pytest tests/test_api.py

# Run example
python examples/upload_example.py

# Install/update dependencies
uv pip install -e ".[dev]"

# Deploy to Databricks
databricks bundle deploy
```

## Need More Help?

- 📖 **Detailed API docs**: See `API_README.md`
- 🔧 **Setup guide**: See `SETUP.md`
- 📊 **Full summary**: See `IMPLEMENTATION_SUMMARY.md`
- 💡 **Issues?**: Check the troubleshooting section in `SETUP.md`

## Project Structure at a Glance

```
databricks_agent_app/
├── app.py                          ← Start here
├── start_app.sh                    ← Quick start script
├── project_properties.json         ← Configure volume here
├── src/databricks_agent_app/
│   └── main.py                     ← FastAPI application
├── examples/
│   └── upload_example.py           ← Try this!
└── tests/
    └── test_api.py                 ← Run tests
```

## Troubleshooting

### "Module not found" error
```bash
uv pip install -e ".[dev]"
```

### "Cannot connect to API"
```bash
# Make sure the app is running
python app.py
```

### "Permission denied" on volume
- Update `project_properties.json` path to a local directory for testing
- Or create the Databricks volume (see step 2 above)

---

**Ready to go? Start with**: `./start_app.sh` 🚀

