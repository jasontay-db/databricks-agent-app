#!/usr/bin/env python3
"""
Example script demonstrating how to use the File Upload API.

Usage:
    python examples/upload_example.py
"""

import requests
import json
from pathlib import Path


# API base URL - update this to match your deployment
API_BASE_URL = "http://localhost:8000"


def check_health():
    """Check if the API is healthy"""
    print("🔍 Checking API health...")
    response = requests.get(f"{API_BASE_URL}/health")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API is healthy!")
        print(f"   Volume path: {data['volume_path']}")
        return True
    else:
        print(f"❌ API health check failed: {response.status_code}")
        return False


def get_config():
    """Get API configuration"""
    print("\n📋 Getting API configuration...")
    response = requests.get(f"{API_BASE_URL}/config")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Configuration retrieved:")
        print(f"   Catalog: {data['volume']['catalog']}")
        print(f"   Schema: {data['volume']['schema']}")
        print(f"   Volume: {data['volume']['volume_name']}")
        print(f"   Max file size: {data['max_file_size_mb']} MB")
        return data
    else:
        print(f"❌ Failed to get configuration: {response.status_code}")
        return None


def create_test_file():
    """Create a test file for upload"""
    test_file = Path("test_upload.txt")
    with open(test_file, "w") as f:
        f.write("Hello from Databricks File Upload API!\n")
        f.write("This is a test file created by the example script.\n")
        f.write("Timestamp: " + str(Path.cwd()))
    return test_file


def upload_file(file_path):
    """Upload a file to the API"""
    print(f"\n📤 Uploading file: {file_path}")
    
    with open(file_path, "rb") as f:
        files = {"file": (file_path.name, f, "text/plain")}
        response = requests.post(f"{API_BASE_URL}/upload", files=files)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ File uploaded successfully!")
        print(f"   Filename: {data['filename']}")
        print(f"   Size: {data['size_mb']} MB ({data['size_bytes']} bytes)")
        print(f"   Target path: {data['target_path']}")
        return data
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None


def list_files():
    """List all files in the volume"""
    print("\n📁 Listing files in volume...")
    response = requests.get(f"{API_BASE_URL}/files")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['count']} file(s):")
        for file_info in data['files']:
            print(f"   - {file_info['filename']}: {file_info['size_mb']} MB")
        return data
    else:
        print(f"❌ Failed to list files: {response.status_code}")
        return None


def delete_file(filename):
    """Delete a file from the volume"""
    print(f"\n🗑️  Deleting file: {filename}")
    response = requests.delete(f"{API_BASE_URL}/files/{filename}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ File deleted successfully!")
        print(f"   Filename: {data['filename']}")
        return data
    elif response.status_code == 404:
        print(f"⚠️  File not found: {filename}")
        return None
    else:
        print(f"❌ Delete failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None


def main():
    """Main example workflow"""
    print("=" * 60)
    print("Databricks File Upload API - Example Script")
    print("=" * 60)
    
    # 1. Check API health
    if not check_health():
        print("\n❌ API is not available. Make sure the server is running.")
        print("   Start the server with: python app.py")
        return
    
    # 2. Get configuration
    config = get_config()
    if not config:
        return
    
    # 3. Create a test file
    print("\n📝 Creating test file...")
    test_file = create_test_file()
    print(f"✅ Created: {test_file}")
    
    # 4. Upload the file
    upload_result = upload_file(test_file)
    if not upload_result:
        return
    
    # 5. List all files
    list_files()
    
    # 6. Ask user if they want to delete the test file
    print("\n" + "=" * 60)
    user_input = input("Do you want to delete the test file? (y/n): ").lower()
    
    if user_input == 'y':
        delete_file(test_file.name)
        list_files()
    else:
        print("✅ Test file kept in volume.")
    
    # 7. Clean up local test file
    if test_file.exists():
        test_file.unlink()
        print(f"🧹 Cleaned up local test file: {test_file}")
    
    print("\n" + "=" * 60)
    print("✅ Example completed!")
    print("=" * 60)
    print("\n📚 API Documentation available at:")
    print(f"   Swagger UI: {API_BASE_URL}/docs")
    print(f"   ReDoc: {API_BASE_URL}/redoc")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrupted by user.")
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to API. Make sure the server is running at:")
        print(f"   {API_BASE_URL}")
        print("\n   Start the server with: python app.py")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

