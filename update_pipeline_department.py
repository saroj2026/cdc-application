"""Update pipeline to include department table and load to S3."""

import requests
import json

API_URL = "http://localhost:8000/api/v1"
PIPELINE_ID = "94bedc4f-20ea-4647-b943-8e057ada49d9"

print("=" * 60)
print("Update Pipeline - Add Department Table")
print("=" * 60)

# Get connections first
print("\n1. Getting connections...")
conn_response = requests.get(f"{API_URL}/connections")
if conn_response.status_code != 200:
    print(f"❌ Error getting connections: {conn_response.status_code}")
    exit(1)

connections = conn_response.json()
postgres_conn = next((c for c in connections if c.get('database_type') == 'postgresql'), None)
s3_conn = next((c for c in connections if c.get('database_type') == 's3'), None)

if not postgres_conn or not s3_conn:
    print("❌ Could not find required connections")
    exit(1)

print(f"   ✅ Source (PostgreSQL): {postgres_conn.get('name')} ({postgres_conn.get('id')})")
print(f"   ✅ Target (S3): {s3_conn.get('name')} ({s3_conn.get('id')})")

source_conn_id = postgres_conn.get('id')
target_conn_id = s3_conn.get('id')

# Create new pipeline with department table
print("\n2. Creating new pipeline with department table...")

new_pipeline_data = {
    "name": "PostgreSQL_to_S3_department",
    "source_connection_id": source_conn_id,
    "target_connection_id": target_conn_id,
    "source_database": postgres_conn.get('database', 'cdctest'),
    "source_schema": postgres_conn.get('schema', 'public'),
    "source_tables": ["department"],  # Only department table
    "target_database": s3_conn.get('database', 'mycdcbucket26'),
    "target_schema": s3_conn.get('schema', ''),
    "target_tables": ["department"],
    "mode": "full_load_only",
    "enable_full_load": True,
    "auto_create_target": True
}

# Use /api/pipelines endpoint (not /api/v1/pipelines)
response = requests.post("http://localhost:8000/api/pipelines", json=new_pipeline_data)
if response.status_code == 201:
    new_pipeline = response.json()
    print(f"   ✅ New pipeline created: {new_pipeline.get('id')}")
    print(f"   Name: {new_pipeline.get('name')}")
    print(f"   Tables: {new_pipeline.get('source_tables', [])}")
    
    # Start the pipeline
    print(f"\n4. Starting pipeline...")
    start_response = requests.post(f"http://localhost:8000/api/pipelines/{new_pipeline.get('id')}/start")
    
    if start_response.status_code == 200:
        result = start_response.json()
        print(f"   ✅ Pipeline started!")
        print(f"   Status: {result.get('status')}")
        print(f"   Message: {result.get('message', 'Pipeline started')}")
        
        print(f"\n" + "=" * 60)
        print("Pipeline Started Successfully!")
        print("=" * 60)
        print(f"\nPipeline ID: {new_pipeline.get('id')}")
        print(f"Table: department")
        print(f"Target: S3 bucket mycdcbucket26")
        print(f"\nThe data will be uploaded to:")
        print(f"  s3://mycdcbucket26/department/full_load_<timestamp>.json")
    else:
        print(f"   ❌ Failed to start pipeline: {start_response.status_code}")
        print(f"   Response: {start_response.text}")
else:
    print(f"   ❌ Failed to create pipeline: {response.status_code}")
    print(f"   Response: {response.text}")

