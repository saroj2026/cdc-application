"""Create and start a CDC pipeline with S3 target."""

import requests
import json
import time

API_URL = "http://localhost:8000/api"
API_V1_URL = "http://localhost:8000/api/v1"

print("=" * 70)
print("Create and Start CDC Pipeline with S3 Target")
print("=" * 70)

# Step 1: Get connections
print("\n1. Getting connections...")
response = requests.get(f"{API_V1_URL}/connections")
if response.status_code != 200:
    print(f"   ❌ Error getting connections: {response.status_code}")
    exit(1)

connections = response.json()
postgres_conn = next((c for c in connections if c.get('database_type') == 'postgresql'), None)
s3_conn = next((c for c in connections if c.get('database_type') == 's3'), None)

if not postgres_conn:
    print("   ❌ PostgreSQL connection not found")
    exit(1)

if not s3_conn:
    print("   ❌ S3 connection not found")
    exit(1)

print(f"   [OK] Source: {postgres_conn.get('name')} (ID: {postgres_conn.get('id')})")
print(f"   [OK] Target: {s3_conn.get('name')} (ID: {s3_conn.get('id')})")

# Step 2: Create pipeline
print("\n2. Creating CDC pipeline...")
pipeline_data = {
    "name": "PostgreSQL_to_S3_Department_CDC",
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

print(f"   Pipeline data:")
print(f"      Name: {pipeline_data['name']}")
print(f"      Mode: {pipeline_data['mode']}")
print(f"      Tables: {pipeline_data['source_tables']}")

response = requests.post(f"{API_URL}/pipelines", json=pipeline_data)
if response.status_code == 201:
    pipeline = response.json()
    pipeline_id = pipeline.get('id')
    print(f"   [OK] Pipeline created successfully!")
    print(f"      ID: {pipeline_id}")
    print(f"      Name: {pipeline.get('name')}")
    print(f"      Status: {pipeline.get('status')}")
elif response.status_code == 500 and "duplicate" in response.text.lower():
    print("   ⚠️  Pipeline with this name already exists")
    print("   Finding existing pipeline...")
    
    # Get all pipelines
    list_response = requests.get(f"{API_URL}/pipelines")
    if list_response.status_code == 200:
        pipelines = list_response.json()
        existing = next(
            (p for p in pipelines if p.get('name') == pipeline_data['name']),
            None
        )
        if existing:
            pipeline_id = existing.get('id')
            print(f"   [OK] Found existing pipeline: {pipeline_id}")
        else:
            print("   ❌ Could not find existing pipeline")
            exit(1)
    else:
        print(f"   ❌ Error listing pipelines: {list_response.status_code}")
        exit(1)
else:
    print(f"   ❌ Failed to create pipeline: {response.status_code}")
    print(f"   Response: {response.text}")
    exit(1)

# Step 3: Start pipeline
print(f"\n3. Starting pipeline: {pipeline_id}...")
print("   This may take a few minutes...")

start_response = requests.post(
    f"{API_URL}/pipelines/{pipeline_id}/start",
    timeout=300  # 5 minute timeout
)

if start_response.status_code == 200:
    result = start_response.json()
    print(f"   [OK] Pipeline started successfully!")
    print(f"\n   Results:")
    print(f"      Status: {result.get('status', 'Unknown')}")
    
    # Full load results
    full_load = result.get('full_load', {})
    if full_load:
        if full_load.get('success'):
            print(f"      [OK] Full Load: SUCCESS")
            print(f"         Tables: {full_load.get('tables_transferred', [])}")
            print(f"         Total Rows: {full_load.get('total_rows', 0)}")
        else:
            print(f"      ⚠️  Full Load: {full_load.get('error', 'Unknown error')}")
    
    # Debezium connector
    debezium = result.get('debezium_connector', {})
    if debezium.get('name'):
        print(f"      [OK] Debezium Connector: {debezium.get('name')}")
        print(f"         Status: {debezium.get('status', 'Unknown')}")
    else:
        print(f"      ⚠️  Debezium Connector: Not created")
    
    # S3 sink connector
    sink = result.get('sink_connector', {})
    if sink.get('name'):
        print(f"      [OK] S3 Sink Connector: {sink.get('name')}")
        print(f"         Status: {sink.get('status', 'Unknown')}")
    elif sink.get('status') == 'SKIPPED':
        print(f"      ⚠️  S3 Sink: {sink.get('message', 'Skipped')}")
    else:
        print(f"      ⚠️  S3 Sink Connector: Not created")
        if sink.get('error'):
            print(f"         Error: {sink.get('error')}")
    
    # Kafka topics
    topics = result.get('kafka_topics', [])
    if topics:
        print(f"      [OK] Kafka Topics: {', '.join(topics)}")
    
    # Message
    message = result.get('message', '')
    if message:
        print(f"\n   Message: {message}")
    
    print(f"\n   [OK] CDC Pipeline is now running!")
    print(f"\n   Next steps:")
    print(f"      1. Make changes to PostgreSQL 'department' table")
    print(f"      2. Changes will be captured by Debezium")
    print(f"      3. Changes will be written to S3 bucket")
    print(f"      4. Check S3 bucket for new files")
    
else:
    print(f"   ❌ Failed to start pipeline: {start_response.status_code}")
    print(f"   Response: {start_response.text}")
    
    # Try to get more details
    if start_response.status_code == 404:
        print(f"\n   Pipeline might not be in database. Checking...")
        check_response = requests.get(f"{API_URL}/pipelines/{pipeline_id}")
        if check_response.status_code == 200:
            print(f"   Pipeline exists in database")
        else:
            print(f"   Pipeline not found in database")
    
    exit(1)

# Step 4: Check pipeline status
print(f"\n4. Checking final pipeline status...")
time.sleep(3)
status_response = requests.get(f"{API_URL}/pipelines/{pipeline_id}")
if status_response.status_code == 200:
    status = status_response.json()
    print(f"   Status: {status.get('status')}")
    print(f"   Full Load Status: {status.get('full_load_status')}")
    print(f"   CDC Status: {status.get('cdc_status')}")
    print(f"   Debezium Connector: {status.get('debezium_connector_name', 'None')}")
    print(f"   Sink Connector: {status.get('sink_connector_name', 'None')}")

print("\n" + "=" * 70)
print("✅ Complete!")
print("=" * 70)
print(f"\nPipeline ID: {pipeline_id}")
print(f"Monitor: GET {API_URL}/pipelines/{pipeline_id}")


import requests
import json
import time

API_URL = "http://localhost:8000/api"
API_V1_URL = "http://localhost:8000/api/v1"

print("=" * 70)
print("Create and Start CDC Pipeline with S3 Target")
print("=" * 70)

# Step 1: Get connections
print("\n1. Getting connections...")
response = requests.get(f"{API_V1_URL}/connections")
if response.status_code != 200:
    print(f"   ❌ Error getting connections: {response.status_code}")
    exit(1)

connections = response.json()
postgres_conn = next((c for c in connections if c.get('database_type') == 'postgresql'), None)
s3_conn = next((c for c in connections if c.get('database_type') == 's3'), None)

if not postgres_conn:
    print("   ❌ PostgreSQL connection not found")
    exit(1)

if not s3_conn:
    print("   ❌ S3 connection not found")
    exit(1)

print(f"   [OK] Source: {postgres_conn.get('name')} (ID: {postgres_conn.get('id')})")
print(f"   [OK] Target: {s3_conn.get('name')} (ID: {s3_conn.get('id')})")

# Step 2: Create pipeline
print("\n2. Creating CDC pipeline...")
pipeline_data = {
    "name": "PostgreSQL_to_S3_Department_CDC",
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

print(f"   Pipeline data:")
print(f"      Name: {pipeline_data['name']}")
print(f"      Mode: {pipeline_data['mode']}")
print(f"      Tables: {pipeline_data['source_tables']}")

response = requests.post(f"{API_URL}/pipelines", json=pipeline_data)
if response.status_code == 201:
    pipeline = response.json()
    pipeline_id = pipeline.get('id')
    print(f"   [OK] Pipeline created successfully!")
    print(f"      ID: {pipeline_id}")
    print(f"      Name: {pipeline.get('name')}")
    print(f"      Status: {pipeline.get('status')}")
elif response.status_code == 500 and "duplicate" in response.text.lower():
    print("   ⚠️  Pipeline with this name already exists")
    print("   Finding existing pipeline...")
    
    # Get all pipelines
    list_response = requests.get(f"{API_URL}/pipelines")
    if list_response.status_code == 200:
        pipelines = list_response.json()
        existing = next(
            (p for p in pipelines if p.get('name') == pipeline_data['name']),
            None
        )
        if existing:
            pipeline_id = existing.get('id')
            print(f"   [OK] Found existing pipeline: {pipeline_id}")
        else:
            print("   ❌ Could not find existing pipeline")
            exit(1)
    else:
        print(f"   ❌ Error listing pipelines: {list_response.status_code}")
        exit(1)
else:
    print(f"   ❌ Failed to create pipeline: {response.status_code}")
    print(f"   Response: {response.text}")
    exit(1)

# Step 3: Start pipeline
print(f"\n3. Starting pipeline: {pipeline_id}...")
print("   This may take a few minutes...")

start_response = requests.post(
    f"{API_URL}/pipelines/{pipeline_id}/start",
    timeout=300  # 5 minute timeout
)

if start_response.status_code == 200:
    result = start_response.json()
    print(f"   [OK] Pipeline started successfully!")
    print(f"\n   Results:")
    print(f"      Status: {result.get('status', 'Unknown')}")
    
    # Full load results
    full_load = result.get('full_load', {})
    if full_load:
        if full_load.get('success'):
            print(f"      [OK] Full Load: SUCCESS")
            print(f"         Tables: {full_load.get('tables_transferred', [])}")
            print(f"         Total Rows: {full_load.get('total_rows', 0)}")
        else:
            print(f"      ⚠️  Full Load: {full_load.get('error', 'Unknown error')}")
    
    # Debezium connector
    debezium = result.get('debezium_connector', {})
    if debezium.get('name'):
        print(f"      [OK] Debezium Connector: {debezium.get('name')}")
        print(f"         Status: {debezium.get('status', 'Unknown')}")
    else:
        print(f"      ⚠️  Debezium Connector: Not created")
    
    # S3 sink connector
    sink = result.get('sink_connector', {})
    if sink.get('name'):
        print(f"      [OK] S3 Sink Connector: {sink.get('name')}")
        print(f"         Status: {sink.get('status', 'Unknown')}")
    elif sink.get('status') == 'SKIPPED':
        print(f"      ⚠️  S3 Sink: {sink.get('message', 'Skipped')}")
    else:
        print(f"      ⚠️  S3 Sink Connector: Not created")
        if sink.get('error'):
            print(f"         Error: {sink.get('error')}")
    
    # Kafka topics
    topics = result.get('kafka_topics', [])
    if topics:
        print(f"      [OK] Kafka Topics: {', '.join(topics)}")
    
    # Message
    message = result.get('message', '')
    if message:
        print(f"\n   Message: {message}")
    
    print(f"\n   [OK] CDC Pipeline is now running!")
    print(f"\n   Next steps:")
    print(f"      1. Make changes to PostgreSQL 'department' table")
    print(f"      2. Changes will be captured by Debezium")
    print(f"      3. Changes will be written to S3 bucket")
    print(f"      4. Check S3 bucket for new files")
    
else:
    print(f"   ❌ Failed to start pipeline: {start_response.status_code}")
    print(f"   Response: {start_response.text}")
    
    # Try to get more details
    if start_response.status_code == 404:
        print(f"\n   Pipeline might not be in database. Checking...")
        check_response = requests.get(f"{API_URL}/pipelines/{pipeline_id}")
        if check_response.status_code == 200:
            print(f"   Pipeline exists in database")
        else:
            print(f"   Pipeline not found in database")
    
    exit(1)

# Step 4: Check pipeline status
print(f"\n4. Checking final pipeline status...")
time.sleep(3)
status_response = requests.get(f"{API_URL}/pipelines/{pipeline_id}")
if status_response.status_code == 200:
    status = status_response.json()
    print(f"   Status: {status.get('status')}")
    print(f"   Full Load Status: {status.get('full_load_status')}")
    print(f"   CDC Status: {status.get('cdc_status')}")
    print(f"   Debezium Connector: {status.get('debezium_connector_name', 'None')}")
    print(f"   Sink Connector: {status.get('sink_connector_name', 'None')}")

print("\n" + "=" * 70)
print("✅ Complete!")
print("=" * 70)
print(f"\nPipeline ID: {pipeline_id}")
print(f"Monitor: GET {API_URL}/pipelines/{pipeline_id}")

