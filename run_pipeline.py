#!/usr/bin/env python3
"""Run a pipeline by name."""

import requests
import sys

API_URL = "http://localhost:8000/api/v1"

def find_and_start_pipeline(pipeline_name: str):
    """Find and start a pipeline by name."""
    print(f"Looking for pipeline: {pipeline_name}")
    print("=" * 60)
    
    # Get all pipelines
    print("\n1. Fetching pipelines...")
    try:
        response = requests.get(f"{API_URL}/pipelines", timeout=10)
        if response.status_code != 200:
            print(f"❌ Error fetching pipelines: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend API. Is the backend running?")
        print("   Try: cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application && ./start_backend.sh")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    pipelines = response.json()
    print(f"   ✅ Found {len(pipelines)} pipeline(s)")
    
    # Find the pipeline by name
    pipeline = None
    for p in pipelines:
        if p.get('name') == pipeline_name:
            pipeline = p
            break
    
    if not pipeline:
        print(f"\n❌ Pipeline '{pipeline_name}' not found!")
        print("\nAvailable pipelines:")
        for p in pipelines:
            print(f"   - {p.get('name')} (ID: {p.get('id')}, Status: {p.get('status')})")
        return False
    
    pipeline_id = pipeline.get('id')
    print(f"\n2. Found pipeline:")
    print(f"   Name: {pipeline.get('name')}")
    print(f"   ID: {pipeline_id}")
    print(f"   Status: {pipeline.get('status')}")
    print(f"   Full Load Status: {pipeline.get('full_load_status')}")
    print(f"   CDC Status: {pipeline.get('cdc_status')}")
    print(f"   Mode: {pipeline.get('mode')}")
    
    # Check if already running
    if pipeline.get('status') in ['RUNNING', 'STARTING']:
        print(f"\n⚠️  Pipeline is already {pipeline.get('status')}")
        print("   Use the frontend or API to stop it first if you want to restart.")
        return True
    
    # Start the pipeline
    print(f"\n3. Starting pipeline...")
    try:
        start_response = requests.post(
            f"{API_URL}/pipelines/{pipeline_id}/start",
            timeout=30
        )
        
        if start_response.status_code == 200:
            result = start_response.json()
            print("   ✅ Pipeline started successfully!")
            print(f"   Message: {result.get('message', 'OK')}")
            
            if result.get('full_load'):
                fl = result['full_load']
                print(f"\n   Full Load Results:")
                print(f"   - Success: {fl.get('success')}")
                print(f"   - Tables Transferred: {fl.get('tables_transferred', 0)}")
                print(f"   - Total Rows: {fl.get('total_rows', 0)}")
            
            if result.get('cdc'):
                cdc = result['cdc']
                print(f"\n   CDC Results:")
                print(f"   - Status: {cdc.get('status')}")
                print(f"   - Connector: {cdc.get('connector_name', 'N/A')}")
            
            return True
        else:
            print(f"   ❌ Failed to start pipeline: {start_response.status_code}")
            print(f"   Response: {start_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error starting pipeline: {e}")
        return False

if __name__ == "__main__":
    pipeline_name = sys.argv[1] if len(sys.argv) > 1 else "pg_to_mssql_projects_simple"
    
    success = find_and_start_pipeline(pipeline_name)
    sys.exit(0 if success else 1)


