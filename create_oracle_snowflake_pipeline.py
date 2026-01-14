"""Create Oracle to Snowflake pipeline."""

import requests
import json
import sys

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Oracle Connection Details
ORACLE_CONFIG = {
    "host": "72.61.233.209",
    "port": 1521,
    "database": "XE",
    "user": "c##cdc_user",
    "password": "cdc_pass"
}

print("=" * 70)
print("Creating Oracle to Snowflake Pipeline")
print("=" * 70)

# Step 1: Get or create Oracle connection
print("\n1. Checking Oracle connection...")
try:
    # Get all connections
    response = requests.get(f"{API_BASE_URL}/connections", timeout=10)
    connections = response.json() if response.status_code == 200 else []
    
    # Find Oracle connection
    oracle_conn = None
    for conn in connections:
        if conn.get("database_type", "").lower() == "oracle" and conn.get("host") == ORACLE_CONFIG["host"]:
            oracle_conn = conn
            break
    
    if not oracle_conn:
        print("   Creating Oracle connection...")
        oracle_conn_data = {
            "name": "oracle-xe",
            "connection_type": "source",
            "database_type": "oracle",
            "host": ORACLE_CONFIG["host"],
            "port": ORACLE_CONFIG["port"],
            "database": ORACLE_CONFIG["database"],
            "username": ORACLE_CONFIG["user"],
            "password": ORACLE_CONFIG["password"],
            "schema": "c##cdc_user",
            "is_active": True
        }
        response = requests.post(f"{API_BASE_URL}/connections", json=oracle_conn_data, timeout=10)
        if response.status_code in [200, 201]:
            oracle_conn = response.json()
            print(f"   ✅ Oracle connection created: {oracle_conn.get('id')}")
        else:
            print(f"   ❌ Failed to create Oracle connection: {response.status_code} - {response.text}")
            sys.exit(1)
    else:
        print(f"   ✅ Oracle connection found: {oracle_conn.get('id')} - {oracle_conn.get('name')}")
    
    oracle_conn_id = oracle_conn["id"]
    
except Exception as e:
    print(f"   ❌ Error with Oracle connection: {e}")
    sys.exit(1)

# Step 2: Get Snowflake connection
print("\n2. Finding Snowflake connection...")
try:
    response = requests.get(f"{API_BASE_URL}/connections", timeout=10)
    connections = response.json() if response.status_code == 200 else []
    
    snowflake_conn = None
    for conn in connections:
        if conn.get("database_type", "").lower() == "snowflake" and "snowflake-s" in conn.get("name", "").lower():
            snowflake_conn = conn
            break
    
    if not snowflake_conn:
        print("   ❌ Snowflake connection 'snowflake-s' not found")
        print("   Available connections:")
        for conn in connections:
            if conn.get("database_type", "").lower() == "snowflake":
                print(f"      - {conn.get('name')} (id: {conn.get('id')})")
        sys.exit(1)
    
    print(f"   ✅ Snowflake connection found: {snowflake_conn.get('id')} - {snowflake_conn.get('name')}")
    snowflake_conn_id = snowflake_conn["id"]
    
except Exception as e:
    print(f"   ❌ Error finding Snowflake connection: {e}")
    sys.exit(1)

# Step 3: Check if pipeline already exists
print("\n3. Checking for existing pipeline...")
try:
    response = requests.get(f"{API_BASE_URL}/pipelines", timeout=10)
    pipelines = response.json() if response.status_code == 200 else []
    
    existing_pipeline = None
    for pipeline in pipelines:
        if pipeline.get("name") == "oracle_sf_p":
            existing_pipeline = pipeline
            break
    
    if existing_pipeline:
        print(f"   ⚠️  Pipeline 'oracle_sf_p' already exists (id: {existing_pipeline.get('id')})")
        print("   Deleting existing pipeline...")
        delete_response = requests.delete(f"{API_BASE_URL}/pipelines/{existing_pipeline.get('id')}", timeout=10)
        if delete_response.status_code in [200, 204]:
            print("   ✅ Existing pipeline deleted")
        else:
            print(f"   ⚠️  Could not delete existing pipeline: {delete_response.status_code}")
    
except Exception as e:
    print(f"   ⚠️  Error checking pipelines: {e}")

# Step 4: Create pipeline
print("\n4. Creating pipeline 'oracle_sf_p'...")
pipeline_data = {
    "name": "oracle_sf_p",
    "description": "Oracle to Snowflake pipeline with test table",
    "source_connection_id": str(oracle_conn_id),
    "target_connection_id": str(snowflake_conn_id),
    "source_database": "XE",
    "source_schema": "c##cdc_user",
    "source_tables": ["test"],
    "target_database": snowflake_conn.get("database", "TEST_DB"),
    "target_schema": snowflake_conn.get("schema", "PUBLIC"),
    "target_tables": ["test"],
    "mode": "full_load_and_cdc",
    "auto_create_target": True
}

try:
    response = requests.post(f"{API_BASE_URL}/pipelines", json=pipeline_data, timeout=30)
    
    if response.status_code in [200, 201]:
        pipeline = response.json()
        pipeline_id = pipeline.get("id")
        print(f"   ✅ Pipeline created successfully!")
        print(f"   Pipeline ID: {pipeline_id}")
        print(f"   Name: {pipeline.get('name')}")
        print(f"   Status: {pipeline.get('status', 'unknown')}")
    else:
        print(f"   ❌ Failed to create pipeline: {response.status_code}")
        print(f"   Response: {response.text}")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ Error creating pipeline: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Start pipeline
print("\n5. Starting pipeline with full_load_and_cdc mode...")
try:
    start_data = {
        "runType": "full_load"
    }
    response = requests.post(
        f"{API_BASE_URL}/pipelines/{pipeline_id}/trigger",
        json=start_data,
        timeout=30
    )
    
    if response.status_code in [200, 201, 202]:
        result = response.json()
        print(f"   ✅ Pipeline started successfully!")
        print(f"   Status: {result.get('status', 'unknown')}")
    else:
        print(f"   ⚠️  Pipeline start response: {response.status_code}")
        print(f"   Response: {response.text}")
        # Don't exit - pipeline might still be created
        
except Exception as e:
    print(f"   ⚠️  Error starting pipeline: {e}")
    print("   Pipeline created but may need to be started manually")

print("\n" + "=" * 70)
print("✅ Pipeline Setup Complete!")
print("=" * 70)
print(f"\nPipeline: oracle_sf_p (ID: {pipeline_id})")
print(f"Source: Oracle XE - c##cdc_user.test")
print(f"Target: Snowflake - {snowflake_conn.get('database')}.{snowflake_conn.get('schema', 'PUBLIC')}.test")
print(f"Mode: full_load_and_cdc")
print("\nNext steps:")
print("1. Check pipeline status via API or UI")
print("2. Monitor replication events")
print("3. Verify data in Snowflake")

