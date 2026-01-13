"""Create a fresh pipeline from scratch."""

import requests
import time

API_URL = "http://localhost:8000/api"

print("=" * 80)
print("Creating Fresh Pipeline")
print("=" * 80)

# Step 1: Get connections
print("\n1. Getting connections...")
try:
    response = requests.get(f"{API_URL}/v1/connections")
    if response.status_code == 200:
        connections = response.json()
        
        pg_conn = None
        mssql_conn = None
        
        for conn in connections:
            if conn.get('database_type') == 'postgresql' and conn.get('database') == 'cdctest':
                pg_conn = conn
            elif conn.get('database_type') in ['sqlserver', 'mssql'] and conn.get('database') == 'cdctest':
                mssql_conn = conn
        
        if not pg_conn:
            print("   [ERROR] PostgreSQL connection not found")
            exit(1)
        if not mssql_conn:
            print("   [ERROR] SQL Server connection not found")
            exit(1)
        
        print(f"   [OK] PostgreSQL: {pg_conn.get('name')} (ID: {pg_conn.get('id')})")
        print(f"   [OK] SQL Server: {mssql_conn.get('name')} (ID: {mssql_conn.get('id')})")
        
        pg_conn_id = pg_conn.get('id')
        mssql_conn_id = mssql_conn.get('id')
        
    else:
        print(f"   [ERROR] Failed to get connections: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"   [ERROR] Exception: {e}")
    exit(1)

# Step 2: Delete existing final_test pipeline if it exists
print("\n2. Checking for existing 'final_test' pipeline...")
try:
    response = requests.get(f"{API_URL}/pipelines")
    if response.status_code == 200:
        pipelines = response.json()
        existing_pipeline = next((p for p in pipelines if p.get('name') == 'final_test'), None)
        
        if existing_pipeline:
            pipeline_id = existing_pipeline.get('id')
            print(f"   [INFO] Found existing pipeline: {pipeline_id}")
            
            # Stop pipeline first
            try:
                stop_response = requests.post(f"{API_URL}/pipelines/{pipeline_id}/stop", timeout=30)
                print(f"   [OK] Pipeline stopped")
            except:
                pass
            
            # Delete pipeline
            delete_response = requests.delete(f"{API_URL}/pipelines/{pipeline_id}?hard_delete=true", timeout=30)
            if delete_response.status_code in [200, 204]:
                print(f"   [OK] Pipeline deleted")
            else:
                print(f"   [WARNING] Delete status: {delete_response.status_code}")
        else:
            print(f"   [OK] No existing pipeline found")
except Exception as e:
    print(f"   [WARNING] Exception checking pipelines: {e}")

print("\n3. Waiting 3 seconds...")
time.sleep(3)

# Step 3: Create new pipeline
print("\n4. Creating new 'final_test' pipeline...")
pipeline_data = {
    "name": "final_test",
    "source_connection_id": pg_conn_id,
    "target_connection_id": mssql_conn_id,
    "source_database": "cdctest",
    "source_schema": "public",
    "source_tables": ["projects_simple"],
    "target_database": "cdctest",
    "target_schema": "dbo",
    "target_tables": ["projects_simple"],
    "mode": "full_load_and_cdc",
    "enable_full_load": True,
    "auto_create_target": True
}

try:
    response = requests.post(f"{API_URL}/pipelines", json=pipeline_data, timeout=30)
    if response.status_code == 201:
        pipeline = response.json()
        new_pipeline_id = pipeline.get('id')
        print(f"   [OK] Pipeline created: {new_pipeline_id}")
        print(f"   Name: {pipeline.get('name')}")
        print(f"   Mode: {pipeline.get('mode')}")
        print(f"   Source: {pipeline.get('source_database')}.{pipeline.get('source_schema')}.{pipeline.get('source_tables')[0]}")
        print(f"   Target: {pipeline.get('target_database')}.{pipeline.get('target_schema')}.{pipeline.get('target_tables')[0]}")
    else:
        print(f"   [ERROR] Failed to create pipeline: {response.status_code}")
        print(f"   Response: {response.text[:300]}")
        exit(1)
except Exception as e:
    print(f"   [ERROR] Exception: {e}")
    exit(1)

# Step 4: Start pipeline
print("\n5. Starting pipeline (Full Load + CDC)...")
print("   This will:")
print("   1. Run full load (copy data from PostgreSQL to SQL Server)")
print("   2. Create Debezium connector (capture PostgreSQL changes)")
print("   3. Create SQL Server sink connector (write changes to SQL Server)")
print("   4. Start CDC streaming")
print("\n   This may take several minutes...")

try:
    response = requests.post(f"{API_URL}/pipelines/{new_pipeline_id}/start", timeout=180)
    if response.status_code == 200:
        result = response.json()
        print(f"\n   [OK] Pipeline started!")
        print(f"   Status: {result.get('status', 'N/A')}")
        
        full_load = result.get('full_load', {})
        if full_load.get('success'):
            print(f"\n   ✅ Full Load: SUCCESS")
            print(f"      Tables transferred: {full_load.get('tables_transferred', 'N/A')}")
            print(f"      Total rows: {full_load.get('total_rows', 'N/A')}")
        else:
            print(f"\n   ⚠️  Full Load: {full_load.get('error', 'Unknown error')}")
        
        debezium = result.get('debezium_connector', {})
        if debezium.get('name'):
            print(f"\n   ✅ Debezium Connector: {debezium.get('name')}")
            print(f"      Status: {debezium.get('status', 'N/A')}")
        
        sink = result.get('sink_connector', {})
        if sink.get('name'):
            print(f"\n   ✅ Sink Connector: {sink.get('name')}")
            print(f"      Status: {sink.get('status', 'N/A')}")
        
        topics = result.get('kafka_topics', [])
        if topics:
            print(f"\n   ✅ Kafka Topics: {', '.join(topics)}")
    else:
        print(f"   [ERROR] Failed to start pipeline: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
        exit(1)
except Exception as e:
    print(f"   [ERROR] Exception: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 5: Wait and check status
print("\n6. Waiting 20 seconds for pipeline to initialize...")
time.sleep(20)

print("\n7. Checking final pipeline status...")
try:
    response = requests.get(f"{API_URL}/pipelines/{new_pipeline_id}")
    if response.status_code == 200:
        pipeline = response.json()
        print(f"   Status: {pipeline.get('status')}")
        print(f"   Full Load Status: {pipeline.get('full_load_status')}")
        print(f"   CDC Status: {pipeline.get('cdc_status')}")
        print(f"   Debezium Connector: {pipeline.get('debezium_connector_name', 'None')}")
        print(f"   Sink Connector: {pipeline.get('sink_connector_name', 'None')}")
except Exception as e:
    print(f"   [WARNING] Failed to check status: {e}")

print("\n" + "=" * 80)
print("Fresh Pipeline Created and Started!")
print("=" * 80)
print(f"\nPipeline ID: {new_pipeline_id}")
print(f"Monitor: GET http://localhost:8000/api/pipelines/{new_pipeline_id}")
print("\nNext steps:")
print("1. Run 'python check_full_load_status.py' to verify data transfer")
print("2. Test CDC by inserting a row in PostgreSQL and checking SQL Server")


import requests
import time

API_URL = "http://localhost:8000/api"

print("=" * 80)
print("Creating Fresh Pipeline")
print("=" * 80)

# Step 1: Get connections
print("\n1. Getting connections...")
try:
    response = requests.get(f"{API_URL}/v1/connections")
    if response.status_code == 200:
        connections = response.json()
        
        pg_conn = None
        mssql_conn = None
        
        for conn in connections:
            if conn.get('database_type') == 'postgresql' and conn.get('database') == 'cdctest':
                pg_conn = conn
            elif conn.get('database_type') in ['sqlserver', 'mssql'] and conn.get('database') == 'cdctest':
                mssql_conn = conn
        
        if not pg_conn:
            print("   [ERROR] PostgreSQL connection not found")
            exit(1)
        if not mssql_conn:
            print("   [ERROR] SQL Server connection not found")
            exit(1)
        
        print(f"   [OK] PostgreSQL: {pg_conn.get('name')} (ID: {pg_conn.get('id')})")
        print(f"   [OK] SQL Server: {mssql_conn.get('name')} (ID: {mssql_conn.get('id')})")
        
        pg_conn_id = pg_conn.get('id')
        mssql_conn_id = mssql_conn.get('id')
        
    else:
        print(f"   [ERROR] Failed to get connections: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"   [ERROR] Exception: {e}")
    exit(1)

# Step 2: Delete existing final_test pipeline if it exists
print("\n2. Checking for existing 'final_test' pipeline...")
try:
    response = requests.get(f"{API_URL}/pipelines")
    if response.status_code == 200:
        pipelines = response.json()
        existing_pipeline = next((p for p in pipelines if p.get('name') == 'final_test'), None)
        
        if existing_pipeline:
            pipeline_id = existing_pipeline.get('id')
            print(f"   [INFO] Found existing pipeline: {pipeline_id}")
            
            # Stop pipeline first
            try:
                stop_response = requests.post(f"{API_URL}/pipelines/{pipeline_id}/stop", timeout=30)
                print(f"   [OK] Pipeline stopped")
            except:
                pass
            
            # Delete pipeline
            delete_response = requests.delete(f"{API_URL}/pipelines/{pipeline_id}?hard_delete=true", timeout=30)
            if delete_response.status_code in [200, 204]:
                print(f"   [OK] Pipeline deleted")
            else:
                print(f"   [WARNING] Delete status: {delete_response.status_code}")
        else:
            print(f"   [OK] No existing pipeline found")
except Exception as e:
    print(f"   [WARNING] Exception checking pipelines: {e}")

print("\n3. Waiting 3 seconds...")
time.sleep(3)

# Step 3: Create new pipeline
print("\n4. Creating new 'final_test' pipeline...")
pipeline_data = {
    "name": "final_test",
    "source_connection_id": pg_conn_id,
    "target_connection_id": mssql_conn_id,
    "source_database": "cdctest",
    "source_schema": "public",
    "source_tables": ["projects_simple"],
    "target_database": "cdctest",
    "target_schema": "dbo",
    "target_tables": ["projects_simple"],
    "mode": "full_load_and_cdc",
    "enable_full_load": True,
    "auto_create_target": True
}

try:
    response = requests.post(f"{API_URL}/pipelines", json=pipeline_data, timeout=30)
    if response.status_code == 201:
        pipeline = response.json()
        new_pipeline_id = pipeline.get('id')
        print(f"   [OK] Pipeline created: {new_pipeline_id}")
        print(f"   Name: {pipeline.get('name')}")
        print(f"   Mode: {pipeline.get('mode')}")
        print(f"   Source: {pipeline.get('source_database')}.{pipeline.get('source_schema')}.{pipeline.get('source_tables')[0]}")
        print(f"   Target: {pipeline.get('target_database')}.{pipeline.get('target_schema')}.{pipeline.get('target_tables')[0]}")
    else:
        print(f"   [ERROR] Failed to create pipeline: {response.status_code}")
        print(f"   Response: {response.text[:300]}")
        exit(1)
except Exception as e:
    print(f"   [ERROR] Exception: {e}")
    exit(1)

# Step 4: Start pipeline
print("\n5. Starting pipeline (Full Load + CDC)...")
print("   This will:")
print("   1. Run full load (copy data from PostgreSQL to SQL Server)")
print("   2. Create Debezium connector (capture PostgreSQL changes)")
print("   3. Create SQL Server sink connector (write changes to SQL Server)")
print("   4. Start CDC streaming")
print("\n   This may take several minutes...")

try:
    response = requests.post(f"{API_URL}/pipelines/{new_pipeline_id}/start", timeout=180)
    if response.status_code == 200:
        result = response.json()
        print(f"\n   [OK] Pipeline started!")
        print(f"   Status: {result.get('status', 'N/A')}")
        
        full_load = result.get('full_load', {})
        if full_load.get('success'):
            print(f"\n   ✅ Full Load: SUCCESS")
            print(f"      Tables transferred: {full_load.get('tables_transferred', 'N/A')}")
            print(f"      Total rows: {full_load.get('total_rows', 'N/A')}")
        else:
            print(f"\n   ⚠️  Full Load: {full_load.get('error', 'Unknown error')}")
        
        debezium = result.get('debezium_connector', {})
        if debezium.get('name'):
            print(f"\n   ✅ Debezium Connector: {debezium.get('name')}")
            print(f"      Status: {debezium.get('status', 'N/A')}")
        
        sink = result.get('sink_connector', {})
        if sink.get('name'):
            print(f"\n   ✅ Sink Connector: {sink.get('name')}")
            print(f"      Status: {sink.get('status', 'N/A')}")
        
        topics = result.get('kafka_topics', [])
        if topics:
            print(f"\n   ✅ Kafka Topics: {', '.join(topics)}")
    else:
        print(f"   [ERROR] Failed to start pipeline: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
        exit(1)
except Exception as e:
    print(f"   [ERROR] Exception: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 5: Wait and check status
print("\n6. Waiting 20 seconds for pipeline to initialize...")
time.sleep(20)

print("\n7. Checking final pipeline status...")
try:
    response = requests.get(f"{API_URL}/pipelines/{new_pipeline_id}")
    if response.status_code == 200:
        pipeline = response.json()
        print(f"   Status: {pipeline.get('status')}")
        print(f"   Full Load Status: {pipeline.get('full_load_status')}")
        print(f"   CDC Status: {pipeline.get('cdc_status')}")
        print(f"   Debezium Connector: {pipeline.get('debezium_connector_name', 'None')}")
        print(f"   Sink Connector: {pipeline.get('sink_connector_name', 'None')}")
except Exception as e:
    print(f"   [WARNING] Failed to check status: {e}")

print("\n" + "=" * 80)
print("Fresh Pipeline Created and Started!")
print("=" * 80)
print(f"\nPipeline ID: {new_pipeline_id}")
print(f"Monitor: GET http://localhost:8000/api/pipelines/{new_pipeline_id}")
print("\nNext steps:")
print("1. Run 'python check_full_load_status.py' to verify data transfer")
print("2. Test CDC by inserting a row in PostgreSQL and checking SQL Server")

