"""Create a pipeline with CDC enabled for department table."""

import requests
import json

API_URL = "http://localhost:8000/api"
API_V1_URL = "http://localhost:8000/api/v1"

print("=" * 60)
print("Create CDC Pipeline for Department Table")
print("=" * 60)

# Get connections
print("\n1. Getting connections...")
response = requests.get(f"{API_V1_URL}/connections")
if response.status_code != 200:
    print(f"❌ Error: {response.status_code}")
    exit(1)

connections = response.json()
postgres_conn = next((c for c in connections if c.get('database_type') == 'postgresql'), None)
s3_conn = next((c for c in connections if c.get('database_type') == 's3'), None)

if not postgres_conn or not s3_conn:
    print("❌ Could not find required connections")
    exit(1)

print(f"   ✅ Source: {postgres_conn.get('name')}")
print(f"   ✅ Target: {s3_conn.get('name')}")

# Create pipeline with CDC mode
print("\n2. Creating pipeline with CDC mode...")
print("   ⚠️  Note: S3 sink connector is not implemented yet")
print("   This will create Debezium connector to capture changes")
print("   But changes won't be written to S3 automatically\n")

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

response = requests.post(f"{API_URL}/pipelines", json=pipeline_data)
if response.status_code == 201:
    pipeline = response.json()
    print(f"   ✅ Pipeline created: {pipeline.get('id')}")
    print(f"   Name: {pipeline.get('name')}")
    print(f"   Mode: {pipeline.get('mode')}")
    
    # Start the pipeline
    print(f"\n3. Starting pipeline...")
    start_response = requests.post(f"{API_URL}/pipelines/{pipeline.get('id')}/start")
    
    if start_response.status_code == 200:
        result = start_response.json()
        print(f"   ✅ Pipeline started!")
        print(f"   Status: {result.get('status')}")
        print(f"   Full Load: {result.get('full_load', {}).get('success', False)}")
        print(f"   Debezium Connector: {result.get('debezium_connector', {}).get('name', 'Not created')}")
        print(f"   Sink Connector: {result.get('sink_connector', {}).get('name', 'Not created')}")
        
        if result.get('debezium_connector', {}).get('name'):
            print(f"\n   ✅ Debezium connector created!")
            print(f"   Changes from PostgreSQL will be captured")
        else:
            print(f"\n   ⚠️  Debezium connector not created")
            if result.get('message'):
                print(f"   Message: {result.get('message')}")
    else:
        print(f"   ❌ Failed to start: {start_response.status_code}")
        print(f"   Response: {start_response.text}")
else:
    print(f"   ❌ Failed to create: {response.status_code}")
    print(f"   Response: {response.text}")

print("\n" + "=" * 60)
