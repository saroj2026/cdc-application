"""Trigger a pipeline by name."""

import requests
import json
import sys

API_BASE = "http://localhost:8000/api/v1"
PIPELINE_NAME = "PostgreSQL_to_S3_cdctest"

print("=" * 70)
print(f"Triggering Pipeline: {PIPELINE_NAME}")
print("=" * 70)

try:
    # Get all pipelines
    print(f"\n1. Fetching pipelines...")
    response = requests.get(f"{API_BASE}/pipelines", timeout=10)
    
    if response.status_code != 200:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   Response: {response.text}")
        sys.exit(1)
    
    pipelines = response.json()
    print(f"   ✅ Found {len(pipelines)} pipeline(s)")
    
    # Find the pipeline by name
    pipeline = None
    for p in pipelines:
        if p.get('name') == PIPELINE_NAME:
            pipeline = p
            break
    
    if not pipeline:
        print(f"\n   ❌ Pipeline '{PIPELINE_NAME}' not found!")
        print(f"\n   Available pipelines:")
        for p in pipelines:
            print(f"      - {p.get('name')} (ID: {p.get('id')})")
        sys.exit(1)
    
    pipeline_id = pipeline.get('id')
    pipeline_status = pipeline.get('status', 'unknown')
    
    print(f"\n2. Found pipeline:")
    print(f"   Name: {pipeline.get('name')}")
    print(f"   ID: {pipeline_id}")
    print(f"   Status: {pipeline_status}")
    print(f"   Source: {pipeline.get('source_database')}.{pipeline.get('source_schema')}")
    print(f"   Target: {pipeline.get('target_database')}.{pipeline.get('target_schema')}")
    
    # Trigger the pipeline
    print(f"\n3. Triggering pipeline...")
    trigger_response = requests.post(
        f"{API_BASE}/pipelines/{pipeline_id}/start",
        timeout=30
    )
    
    if trigger_response.status_code == 200:
        result = trigger_response.json()
        print(f"   ✅ Pipeline triggered successfully!")
        print(f"\n   Result:")
        print(json.dumps(result, indent=2))
        
        # Check status
        print(f"\n4. Checking pipeline status...")
        status_response = requests.get(f"{API_BASE}/pipelines/{pipeline_id}/status", timeout=10)
        if status_response.status_code == 200:
            status = status_response.json()
            print(f"   Status: {status.get('status', 'unknown')}")
            print(f"   Full Load: {status.get('full_load_status', 'unknown')}")
            print(f"   CDC: {status.get('cdc_status', 'unknown')}")
    else:
        print(f"   ❌ Error: {trigger_response.status_code}")
        print(f"   Response: {trigger_response.text}")
        try:
            error_detail = trigger_response.json()
            print(f"\n   Error Details:")
            print(json.dumps(error_detail, indent=2))
        except:
            pass
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("Pipeline Trigger Complete")
    print("=" * 70)
    
except requests.exceptions.ConnectionError:
    print("\n❌ Could not connect to backend API at http://localhost:8000")
    print("   Make sure the backend is running: ./start_backend.sh")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

