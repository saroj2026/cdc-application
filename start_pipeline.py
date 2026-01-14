"""Start the PostgreSQL to S3 pipeline."""

import requests
import json
import time

API_URL = "http://localhost:8000/api"
PIPELINE_ID = "94bedc4f-20ea-4647-b943-8e057ada49d9"

print("=" * 60)
print("Starting Pipeline")
print("=" * 60)

try:
    print(f"\nPipeline ID: {PIPELINE_ID}")
    print("Starting full load from PostgreSQL to S3...\n")
    
    response = requests.post(
        f"{API_URL}/pipelines/{PIPELINE_ID}/start",
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Pipeline started successfully!")
        print(f"\nStatus: {result.get('status', 'Unknown')}")
        print(f"Message: {result.get('message', 'Pipeline started')}")
        
        if result.get('full_load_status'):
            print(f"Full Load Status: {result.get('full_load_status')}")
        
        print("\n" + "=" * 60)
        print("Pipeline is now running")
        print("=" * 60)
        print("\nThe full load process will:")
        print("  1. Extract schema from PostgreSQL tables")
        print("  2. Read all data from source tables")
        print("  3. Upload data to S3 bucket: mycdcbucket26")
        print("\nThis may take some time depending on data volume.")
        print("\nMonitor progress with:")
        print(f"  GET {API_URL}/pipelines/{PIPELINE_ID}")
        
    elif response.status_code == 400:
        error = response.json()
        print(f"❌ Failed to start pipeline: {error.get('detail', 'Bad Request')}")
    else:
        print(f"❌ Failed to start pipeline: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.Timeout:
    print("❌ Request timed out - pipeline may still be starting")
except requests.exceptions.ConnectionError:
    print("❌ Could not connect to API server")
    print("   Make sure the backend server is running on http://localhost:8000")
except Exception as e:
    print(f"❌ Error: {e}")

