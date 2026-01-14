"""Run CDC for department table to sync new data to S3."""

import requests
import json
import time

API_URL = "http://localhost:8000/api"

print("=" * 60)
print("Run CDC for Department Table")
print("=" * 60)

# Find the department pipeline
print("\n1. Finding department pipeline...")
response = requests.get(f"{API_URL}/pipelines")
if response.status_code != 200:
    print(f"❌ Error getting pipelines: {response.status_code}")
    exit(1)

pipelines = response.json()
department_pipeline = next((p for p in pipelines if 'department' in p.get('name', '').lower()), None)

if not department_pipeline:
    print("   ⚠️  Department pipeline not found")
    print("   Creating new pipeline with CDC mode...")
    
    # Get connections
    conn_response = requests.get("http://localhost:8000/api/v1/connections")
    if conn_response.status_code != 200:
        print(f"❌ Error getting connections: {conn_response.status_code}")
        exit(1)
    
    connections = conn_response.json()
    postgres_conn = next((c for c in connections if c.get('database_type') == 'postgresql'), None)
    s3_conn = next((c for c in connections if c.get('database_type') == 's3'), None)
    
    if not postgres_conn or not s3_conn:
        print("❌ Could not find required connections")
        exit(1)
    
    # Create pipeline with CDC mode
    pipeline_data = {
        "name": "PostgreSQL_to_S3_department_CDC",
        "source_connection_id": postgres_conn.get('id'),
        "target_connection_id": s3_conn.get('id'),
        "source_database": postgres_conn.get('database', 'cdctest'),
        "source_schema": postgres_conn.get('schema', 'public'),
        "source_tables": ["department"],
        "target_database": s3_conn.get('database', 'mycdcbucket26'),
        "target_schema": s3_conn.get('schema', ''),
        "target_tables": ["department"],
        "mode": "full_load_and_cdc",  # Enable CDC
        "enable_full_load": True,
        "auto_create_target": True
    }
    
    create_response = requests.post(f"{API_URL}/pipelines", json=pipeline_data)
    if create_response.status_code != 201:
        print(f"❌ Failed to create pipeline: {create_response.status_code}")
        print(create_response.text)
        exit(1)
    
    department_pipeline = create_response.json()
    print(f"   ✅ Pipeline created: {department_pipeline.get('id')}")
else:
    print(f"   ✅ Found pipeline: {department_pipeline.get('name')}")
    print(f"   Pipeline ID: {department_pipeline.get('id')}")
    print(f"   Mode: {department_pipeline.get('mode')}")

pipeline_id = department_pipeline.get('id')

# Check pipeline mode
pipeline_mode = department_pipeline.get('mode', 'full_load_only')
print(f"\n2. Pipeline mode: {pipeline_mode}")

if pipeline_mode == 'full_load_only':
    print("\n   ⚠️  Pipeline is in 'full_load_only' mode")
    print("   For CDC, we need to run another full load to capture the new record")
    print("   Starting full load...")
    
    # Start pipeline (will do full load)
    start_response = requests.post(f"{API_URL}/pipelines/{pipeline_id}/start")
    if start_response.status_code == 200:
        result = start_response.json()
        print(f"   ✅ Full load started!")
        print(f"   Status: {result.get('status')}")
        print(f"   Message: {result.get('message', 'Pipeline started')}")
        
        # Wait a bit and check status
        print("\n3. Waiting for full load to complete...")
        time.sleep(5)
        
        status_response = requests.get(f"{API_URL}/pipelines/{pipeline_id}")
        if status_response.status_code == 200:
            status = status_response.json()
            print(f"   Full Load Status: {status.get('full_load_status')}")
            print(f"   Pipeline Status: {status.get('status')}")
    else:
        print(f"   ❌ Failed to start pipeline: {start_response.status_code}")
        print(start_response.text)
elif pipeline_mode in ['full_load_and_cdc', 'cdc_only']:
    print("\n   ✅ Pipeline supports CDC")
    print("   Starting pipeline to capture changes...")
    
    start_response = requests.post(f"{API_URL}/pipelines/{pipeline_id}/start")
    if start_response.status_code == 200:
        result = start_response.json()
        print(f"   ✅ Pipeline started!")
        print(f"   Status: {result.get('status')}")
    else:
        print(f"   ❌ Failed to start pipeline: {start_response.status_code}")
        print(start_response.text)
else:
    print(f"\n   ⚠️  Unknown pipeline mode: {pipeline_mode}")

print("\n" + "=" * 60)
print("CDC Process Initiated")
print("=" * 60)
print(f"\nPipeline ID: {pipeline_id}")
print(f"Table: department")
print(f"Target: S3 bucket mycdcbucket26")
print(f"\nMonitor pipeline status:")
print(f"  GET {API_URL}/pipelines/{pipeline_id}")

