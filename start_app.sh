#!/bin/bash
#
# Quick start script for the Databricks FastAPI File Upload App
# This script will set up the environment and start the application
#

set -e

echo "=================================================="
echo "Databricks FastAPI File Upload App - Quick Start"
echo "=================================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Found Python $PYTHON_VERSION"

# Check if UV is available (recommended)
if command -v uv &> /dev/null; then
    echo "✅ UV package manager found"
    PACKAGE_MANAGER="uv pip"
else
    echo "ℹ️  UV not found, using pip"
    PACKAGE_MANAGER="pip"
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
if [ "$PACKAGE_MANAGER" = "uv pip" ]; then
    uv pip install -e ".[dev]"
else
    python3 -m pip install -e ".[dev]"
fi

echo ""
echo "✅ Dependencies installed successfully!"

# Check if project_properties.json exists
if [ ! -f "project_properties.json" ]; then
    echo ""
    echo "⚠️  Warning: project_properties.json not found!"
    echo "   Using default configuration..."
fi

# Set environment variables (optional)
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8000}"

echo ""
echo "=================================================="
echo "🚀 Starting FastAPI Application"
echo "=================================================="
echo ""
echo "   Host: $HOST"
echo "   Port: $PORT"
echo ""
echo "   API Documentation:"
echo "   - Swagger UI: http://localhost:$PORT/docs"
echo "   - ReDoc: http://localhost:$PORT/redoc"
echo ""
echo "   Press Ctrl+C to stop the server"
echo ""
echo "=================================================="
echo ""

# Start the application
python3 app.py

