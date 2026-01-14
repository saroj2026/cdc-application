"""Setup and test final_test pipeline: PostgreSQL -> SQL Server with full load + CDC."""

import requests
import json
import time

API_URL = "http://localhost:8000/api"
API_V1_URL = "http://localhost:8000/api/v1"

print("=" * 80)
print("Setting Up Final Test Pipeline: PostgreSQL -> SQL Server")
print("=" * 80)

# Step 1: Create PostgreSQL Connection
print("\n1. Creating PostgreSQL connection...")
postgres_conn_data = {
    "name": "PostgreSQL_cdctest_FinalTest",
    "connection_type": "source",
    "database_type": "postgresql",
    "host": "72.61.233.209",
    "port": 5432,
    "database": "cdctest",  # Changed from cdctest-db to cdctest
    "username": "cdc_user",
    "password": "cdc_pass",
    "schema": "public"
}

response = requests.post(f"{API_V1_URL}/connections", json=postgres_conn_data)
if response.status_code == 201:
    postgres_conn = response.json()
    postgres_conn_id = postgres_conn.get('id')
    print(f"   [OK] PostgreSQL connection created: {postgres_conn_id}")
elif response.status_code == 500 and "duplicate" in response.text.lower():
    print("   [INFO] Connection already exists, finding it...")
    conns_response = requests.get(f"{API_V1_URL}/connections")
    if conns_response.status_code == 200:
        conns = conns_response.json()
        # Find connection with exact database name 'cdctest' (not 'cdctest-db')
        postgres_conn = next((c for c in conns if c.get('database') == 'cdctest' and c.get('database_type') == 'postgresql'), None)
        if postgres_conn:
            postgres_conn_id = postgres_conn.get('id')
            print(f"   [OK] Found existing PostgreSQL connection: {postgres_conn_id}")
        else:
            print("   [ERROR] Could not find PostgreSQL connection")
            exit(1)
    else:
        print(f"   [ERROR] Failed to list connections: {conns_response.status_code}")
        exit(1)
else:
    print(f"   [ERROR] Failed to create PostgreSQL connection: {response.status_code}")
    print(f"   Response: {response.text[:300]}")
    exit(1)

# Step 2: Test PostgreSQL Connection
print("\n2. Testing PostgreSQL connection...")
test_response = requests.post(f"{API_V1_URL}/connections/{postgres_conn_id}/test", timeout=30)
if test_response.status_code == 200:
    test_result = test_response.json()
    if test_result.get('success'):
        print(f"   [OK] PostgreSQL connection test passed")
    else:
        print(f"   [WARNING] Connection test: {test_result.get('message', 'Unknown')}")
else:
    print(f"   [WARNING] Connection test failed: {test_response.status_code}")

# Step 3: Create SQL Server Connection
print("\n3. Creating SQL Server connection...")
mssql_conn_data = {
    "name": "SQLServer_cdctest_FinalTest",
    "connection_type": "target",
    "database_type": "sqlserver",
    "host": "72.61.233.209",
    "port": 1433,
    "database": "cdctest",
    "username": "sa",
    "password": "Sql@12345",
    "schema": "dbo"
}

response = requests.post(f"{API_V1_URL}/connections", json=mssql_conn_data)
if response.status_code == 201:
    mssql_conn = response.json()
    mssql_conn_id = mssql_conn.get('id')
    print(f"   [OK] SQL Server connection created: {mssql_conn_id}")
elif response.status_code == 500 and "duplicate" in response.text.lower():
    print("   [INFO] Connection already exists, finding it...")
    conns_response = requests.get(f"{API_V1_URL}/connections")
    if conns_response.status_code == 200:
        conns = conns_response.json()
        # Find SQL Server connection with exact database name 'cdctest'
        mssql_conn = next((c for c in conns if c.get('database') == 'cdctest' and c.get('database_type') == 'sqlserver'), None)
        if mssql_conn:
            mssql_conn_id = mssql_conn.get('id')
            print(f"   [OK] Found existing SQL Server connection: {mssql_conn_id}")
        else:
            print("   [ERROR] Could not find SQL Server connection")
            exit(1)
    else:
        print(f"   [ERROR] Failed to list connections: {conns_response.status_code}")
        exit(1)
else:
    print(f"   [ERROR] Failed to create SQL Server connection: {response.status_code}")
    print(f"   Response: {response.text[:300]}")
    exit(1)

# Step 4: Test SQL Server Connection
print("\n4. Testing SQL Server connection...")
test_response = requests.post(f"{API_V1_URL}/connections/{mssql_conn_id}/test", timeout=30)
if test_response.status_code == 200:
    test_result = test_response.json()
    if test_result.get('success'):
        print(f"   [OK] SQL Server connection test passed")
    else:
        print(f"   [WARNING] Connection test: {test_result.get('message', 'Unknown')}")
        print(f"   Note: You may need to update SQL Server password in the connection")
else:
    print(f"   [WARNING] Connection test failed: {test_response.status_code}")

# Step 5: Discover source table
print("\n5. Discovering source table: public.projects_simple...")
discover_response = requests.get(
    f"{API_V1_URL}/connections/{postgres_conn_id}/discover",
    params={"database": "cdctest", "schema": "public", "table": "projects_simple"},
    timeout=30
)
if discover_response.status_code == 200:
    discover_result = discover_response.json()
    tables = discover_result.get('tables', [])
    if tables:
        table_info = tables[0]
        print(f"   [OK] Table found: {table_info.get('name')}")
        print(f"   Columns: {len(table_info.get('columns', []))}")
    else:
        print(f"   [WARNING] Table 'projects_simple' not found in public schema")
        print(f"   Available tables will be checked when creating pipeline")
else:
    print(f"   [WARNING] Could not discover table: {discover_response.status_code}")

# Step 6: Create Pipeline
print("\n6. Creating pipeline 'final_test'...")
pipeline_data = {
    "name": "final_test",
    "source_connection_id": postgres_conn_id,
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

response = requests.post(f"{API_URL}/pipelines", json=pipeline_data)
if response.status_code == 201:
    pipeline = response.json()
    pipeline_id = pipeline.get('id')
    print(f"   [OK] Pipeline created: {pipeline_id}")
    print(f"   Name: {pipeline.get('name')}")
    print(f"   Mode: {pipeline.get('mode')}")
elif response.status_code == 500 and "duplicate" in response.text.lower():
    print("   [INFO] Pipeline already exists, finding it...")
    pipelines_response = requests.get(f"{API_URL}/pipelines")
    if pipelines_response.status_code == 200:
        pipelines = pipelines_response.json()
        existing = next((p for p in pipelines if p.get('name') == 'final_test'), None)
        if existing:
            pipeline_id = existing.get('id')
            print(f"   [OK] Found existing pipeline: {pipeline_id}")
        else:
            print("   [ERROR] Could not find existing pipeline")
            exit(1)
    else:
        print(f"   [ERROR] Failed to list pipelines: {pipelines_response.status_code}")
        exit(1)
else:
    print(f"   [ERROR] Failed to create pipeline: {response.status_code}")
    print(f"   Response: {response.text[:500]}")
    exit(1)

# Step 7: Start Pipeline (Full Load + CDC)
print(f"\n7. Starting pipeline (Full Load + CDC)...")
print("   This will:")
print("   1. Run full load (copy all data from PostgreSQL to SQL Server)")
print("   2. Create Debezium connector (capture PostgreSQL changes)")
print("   3. Create SQL Server sink connector (write changes to SQL Server)")
print("   4. Start CDC streaming")
print("\n   This may take several minutes...")

start_response = requests.post(
    f"{API_URL}/pipelines/{pipeline_id}/start",
    timeout=600  # 10 minute timeout
)

if start_response.status_code == 200:
    result = start_response.json()
    print(f"\n   [OK] Pipeline started!")
    print(f"\n   Results:")
    print(f"   Status: {result.get('status', 'Unknown')}")
    
    # Full Load Results
    full_load = result.get('full_load', {})
    if full_load.get('success'):
        print(f"\n   ✅ Full Load: SUCCESS")
        print(f"      Tables transferred: {full_load.get('tables_transferred', [])}")
        print(f"      Total rows: {full_load.get('total_rows', 0)}")
        print(f"      Duration: {full_load.get('duration_seconds', 0):.2f} seconds")
    else:
        print(f"\n   ❌ Full Load: FAILED")
        print(f"      Error: {full_load.get('error', 'Unknown error')}")
    
    # Debezium Connector
    debezium = result.get('debezium_connector', {})
    if debezium.get('name'):
        print(f"\n   ✅ Debezium Connector: {debezium.get('name')}")
        print(f"      Status: {debezium.get('status', 'Unknown')}")
    else:
        print(f"\n   ⚠️  Debezium Connector: Not created")
        if debezium.get('error'):
            print(f"      Error: {debezium.get('error')}")
    
    # Sink Connector
    sink = result.get('sink_connector', {})
    if sink.get('name'):
        print(f"\n   ✅ SQL Server Sink Connector: {sink.get('name')}")
        print(f"      Status: {sink.get('status', 'Unknown')}")
    else:
        print(f"\n   ⚠️  Sink Connector: Not created")
        if sink.get('error'):
            print(f"      Error: {sink.get('error')}")
    
    # Kafka Topics
    topics = result.get('kafka_topics', [])
    if topics:
        print(f"\n   ✅ Kafka Topics: {', '.join(topics)}")
    
    # Message
    message = result.get('message', '')
    if message:
        print(f"\n   Message: {message}")
    
    print(f"\n   ✅ Pipeline is now running!")
    
else:
    print(f"\n   ❌ Failed to start pipeline: {start_response.status_code}")
    print(f"   Response: {start_response.text[:500]}")
    exit(1)

# Step 8: Check Pipeline Status
print(f"\n8. Checking final pipeline status...")
time.sleep(5)
status_response = requests.get(f"{API_URL}/pipelines/{pipeline_id}")
if status_response.status_code == 200:
    status = status_response.json()
    print(f"   Status: {status.get('status')}")
    print(f"   Full Load Status: {status.get('full_load_status')}")
    print(f"   CDC Status: {status.get('cdc_status')}")
    print(f"   Debezium Connector: {status.get('debezium_connector_name', 'None')}")
    print(f"   Sink Connector: {status.get('sink_connector_name', 'None')}")

print("\n" + "=" * 80)
print("Setup Complete!")
print("=" * 80)
print(f"\nPipeline ID: {pipeline_id}")
print(f"Monitor: GET {API_URL}/pipelines/{pipeline_id}")
print(f"\nNext steps:")
print(f"1. Make changes to PostgreSQL 'public.projects_simple' table")
print(f"2. Changes will be captured by Debezium")
print(f"3. Changes will be written to SQL Server 'dbo.projects_simple' table")
print(f"4. Verify changes in SQL Server database")


import requests
import json
import time

API_URL = "http://localhost:8000/api"
API_V1_URL = "http://localhost:8000/api/v1"

print("=" * 80)
print("Setting Up Final Test Pipeline: PostgreSQL -> SQL Server")
print("=" * 80)

# Step 1: Create PostgreSQL Connection
print("\n1. Creating PostgreSQL connection...")
postgres_conn_data = {
    "name": "PostgreSQL_cdctest_FinalTest",
    "connection_type": "source",
    "database_type": "postgresql",
    "host": "72.61.233.209",
    "port": 5432,
    "database": "cdctest",  # Changed from cdctest-db to cdctest
    "username": "cdc_user",
    "password": "cdc_pass",
    "schema": "public"
}

response = requests.post(f"{API_V1_URL}/connections", json=postgres_conn_data)
if response.status_code == 201:
    postgres_conn = response.json()
    postgres_conn_id = postgres_conn.get('id')
    print(f"   [OK] PostgreSQL connection created: {postgres_conn_id}")
elif response.status_code == 500 and "duplicate" in response.text.lower():
    print("   [INFO] Connection already exists, finding it...")
    conns_response = requests.get(f"{API_V1_URL}/connections")
    if conns_response.status_code == 200:
        conns = conns_response.json()
        # Find connection with exact database name 'cdctest' (not 'cdctest-db')
        postgres_conn = next((c for c in conns if c.get('database') == 'cdctest' and c.get('database_type') == 'postgresql'), None)
        if postgres_conn:
            postgres_conn_id = postgres_conn.get('id')
            print(f"   [OK] Found existing PostgreSQL connection: {postgres_conn_id}")
        else:
            print("   [ERROR] Could not find PostgreSQL connection")
            exit(1)
    else:
        print(f"   [ERROR] Failed to list connections: {conns_response.status_code}")
        exit(1)
else:
    print(f"   [ERROR] Failed to create PostgreSQL connection: {response.status_code}")
    print(f"   Response: {response.text[:300]}")
    exit(1)

# Step 2: Test PostgreSQL Connection
print("\n2. Testing PostgreSQL connection...")
test_response = requests.post(f"{API_V1_URL}/connections/{postgres_conn_id}/test", timeout=30)
if test_response.status_code == 200:
    test_result = test_response.json()
    if test_result.get('success'):
        print(f"   [OK] PostgreSQL connection test passed")
    else:
        print(f"   [WARNING] Connection test: {test_result.get('message', 'Unknown')}")
else:
    print(f"   [WARNING] Connection test failed: {test_response.status_code}")

# Step 3: Create SQL Server Connection
print("\n3. Creating SQL Server connection...")
mssql_conn_data = {
    "name": "SQLServer_cdctest_FinalTest",
    "connection_type": "target",
    "database_type": "sqlserver",
    "host": "72.61.233.209",
    "port": 1433,
    "database": "cdctest",
    "username": "sa",
    "password": "Sql@12345",
    "schema": "dbo"
}

response = requests.post(f"{API_V1_URL}/connections", json=mssql_conn_data)
if response.status_code == 201:
    mssql_conn = response.json()
    mssql_conn_id = mssql_conn.get('id')
    print(f"   [OK] SQL Server connection created: {mssql_conn_id}")
elif response.status_code == 500 and "duplicate" in response.text.lower():
    print("   [INFO] Connection already exists, finding it...")
    conns_response = requests.get(f"{API_V1_URL}/connections")
    if conns_response.status_code == 200:
        conns = conns_response.json()
        # Find SQL Server connection with exact database name 'cdctest'
        mssql_conn = next((c for c in conns if c.get('database') == 'cdctest' and c.get('database_type') == 'sqlserver'), None)
        if mssql_conn:
            mssql_conn_id = mssql_conn.get('id')
            print(f"   [OK] Found existing SQL Server connection: {mssql_conn_id}")
        else:
            print("   [ERROR] Could not find SQL Server connection")
            exit(1)
    else:
        print(f"   [ERROR] Failed to list connections: {conns_response.status_code}")
        exit(1)
else:
    print(f"   [ERROR] Failed to create SQL Server connection: {response.status_code}")
    print(f"   Response: {response.text[:300]}")
    exit(1)

# Step 4: Test SQL Server Connection
print("\n4. Testing SQL Server connection...")
test_response = requests.post(f"{API_V1_URL}/connections/{mssql_conn_id}/test", timeout=30)
if test_response.status_code == 200:
    test_result = test_response.json()
    if test_result.get('success'):
        print(f"   [OK] SQL Server connection test passed")
    else:
        print(f"   [WARNING] Connection test: {test_result.get('message', 'Unknown')}")
        print(f"   Note: You may need to update SQL Server password in the connection")
else:
    print(f"   [WARNING] Connection test failed: {test_response.status_code}")

# Step 5: Discover source table
print("\n5. Discovering source table: public.projects_simple...")
discover_response = requests.get(
    f"{API_V1_URL}/connections/{postgres_conn_id}/discover",
    params={"database": "cdctest", "schema": "public", "table": "projects_simple"},
    timeout=30
)
if discover_response.status_code == 200:
    discover_result = discover_response.json()
    tables = discover_result.get('tables', [])
    if tables:
        table_info = tables[0]
        print(f"   [OK] Table found: {table_info.get('name')}")
        print(f"   Columns: {len(table_info.get('columns', []))}")
    else:
        print(f"   [WARNING] Table 'projects_simple' not found in public schema")
        print(f"   Available tables will be checked when creating pipeline")
else:
    print(f"   [WARNING] Could not discover table: {discover_response.status_code}")

# Step 6: Create Pipeline
print("\n6. Creating pipeline 'final_test'...")
pipeline_data = {
    "name": "final_test",
    "source_connection_id": postgres_conn_id,
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

response = requests.post(f"{API_URL}/pipelines", json=pipeline_data)
if response.status_code == 201:
    pipeline = response.json()
    pipeline_id = pipeline.get('id')
    print(f"   [OK] Pipeline created: {pipeline_id}")
    print(f"   Name: {pipeline.get('name')}")
    print(f"   Mode: {pipeline.get('mode')}")
elif response.status_code == 500 and "duplicate" in response.text.lower():
    print("   [INFO] Pipeline already exists, finding it...")
    pipelines_response = requests.get(f"{API_URL}/pipelines")
    if pipelines_response.status_code == 200:
        pipelines = pipelines_response.json()
        existing = next((p for p in pipelines if p.get('name') == 'final_test'), None)
        if existing:
            pipeline_id = existing.get('id')
            print(f"   [OK] Found existing pipeline: {pipeline_id}")
        else:
            print("   [ERROR] Could not find existing pipeline")
            exit(1)
    else:
        print(f"   [ERROR] Failed to list pipelines: {pipelines_response.status_code}")
        exit(1)
else:
    print(f"   [ERROR] Failed to create pipeline: {response.status_code}")
    print(f"   Response: {response.text[:500]}")
    exit(1)

# Step 7: Start Pipeline (Full Load + CDC)
print(f"\n7. Starting pipeline (Full Load + CDC)...")
print("   This will:")
print("   1. Run full load (copy all data from PostgreSQL to SQL Server)")
print("   2. Create Debezium connector (capture PostgreSQL changes)")
print("   3. Create SQL Server sink connector (write changes to SQL Server)")
print("   4. Start CDC streaming")
print("\n   This may take several minutes...")

start_response = requests.post(
    f"{API_URL}/pipelines/{pipeline_id}/start",
    timeout=600  # 10 minute timeout
)

if start_response.status_code == 200:
    result = start_response.json()
    print(f"\n   [OK] Pipeline started!")
    print(f"\n   Results:")
    print(f"   Status: {result.get('status', 'Unknown')}")
    
    # Full Load Results
    full_load = result.get('full_load', {})
    if full_load.get('success'):
        print(f"\n   ✅ Full Load: SUCCESS")
        print(f"      Tables transferred: {full_load.get('tables_transferred', [])}")
        print(f"      Total rows: {full_load.get('total_rows', 0)}")
        print(f"      Duration: {full_load.get('duration_seconds', 0):.2f} seconds")
    else:
        print(f"\n   ❌ Full Load: FAILED")
        print(f"      Error: {full_load.get('error', 'Unknown error')}")
    
    # Debezium Connector
    debezium = result.get('debezium_connector', {})
    if debezium.get('name'):
        print(f"\n   ✅ Debezium Connector: {debezium.get('name')}")
        print(f"      Status: {debezium.get('status', 'Unknown')}")
    else:
        print(f"\n   ⚠️  Debezium Connector: Not created")
        if debezium.get('error'):
            print(f"      Error: {debezium.get('error')}")
    
    # Sink Connector
    sink = result.get('sink_connector', {})
    if sink.get('name'):
        print(f"\n   ✅ SQL Server Sink Connector: {sink.get('name')}")
        print(f"      Status: {sink.get('status', 'Unknown')}")
    else:
        print(f"\n   ⚠️  Sink Connector: Not created")
        if sink.get('error'):
            print(f"      Error: {sink.get('error')}")
    
    # Kafka Topics
    topics = result.get('kafka_topics', [])
    if topics:
        print(f"\n   ✅ Kafka Topics: {', '.join(topics)}")
    
    # Message
    message = result.get('message', '')
    if message:
        print(f"\n   Message: {message}")
    
    print(f"\n   ✅ Pipeline is now running!")
    
else:
    print(f"\n   ❌ Failed to start pipeline: {start_response.status_code}")
    print(f"   Response: {start_response.text[:500]}")
    exit(1)

# Step 8: Check Pipeline Status
print(f"\n8. Checking final pipeline status...")
time.sleep(5)
status_response = requests.get(f"{API_URL}/pipelines/{pipeline_id}")
if status_response.status_code == 200:
    status = status_response.json()
    print(f"   Status: {status.get('status')}")
    print(f"   Full Load Status: {status.get('full_load_status')}")
    print(f"   CDC Status: {status.get('cdc_status')}")
    print(f"   Debezium Connector: {status.get('debezium_connector_name', 'None')}")
    print(f"   Sink Connector: {status.get('sink_connector_name', 'None')}")

print("\n" + "=" * 80)
print("Setup Complete!")
print("=" * 80)
print(f"\nPipeline ID: {pipeline_id}")
print(f"Monitor: GET {API_URL}/pipelines/{pipeline_id}")
print(f"\nNext steps:")
print(f"1. Make changes to PostgreSQL 'public.projects_simple' table")
print(f"2. Changes will be captured by Debezium")
print(f"3. Changes will be written to SQL Server 'dbo.projects_simple' table")
print(f"4. Verify changes in SQL Server database")

