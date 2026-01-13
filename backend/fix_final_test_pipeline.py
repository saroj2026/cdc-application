"""Fix final_test pipeline by deleting and recreating with correct database."""

import requests

API_URL = "http://localhost:8000/api"
API_V1_URL = "http://localhost:8000/api/v1"

print("=" * 80)
print("Fixing Final Test Pipeline")
print("=" * 80)

# Step 1: Delete existing pipeline
print("\n1. Deleting existing 'final_test' pipeline...")
pipelines_response = requests.get(f"{API_URL}/pipelines")
if pipelines_response.status_code == 200:
    pipelines = pipelines_response.json()
    existing = next((p for p in pipelines if p.get('name') == 'final_test'), None)
    if existing:
        pipeline_id = existing.get('id')
        delete_response = requests.delete(f"{API_URL}/pipelines/{pipeline_id}?hard_delete=true")
        if delete_response.status_code in [200, 204]:
            print(f"   [OK] Deleted existing pipeline: {pipeline_id}")
        else:
            print(f"   [WARNING] Could not delete: {delete_response.status_code}")
    else:
        print("   [INFO] No existing pipeline found")

# Step 2: Get connections
print("\n2. Getting connections...")
conns_response = requests.get(f"{API_V1_URL}/connections")
if conns_response.status_code == 200:
    conns = conns_response.json()
    # Find connections with exact database name 'cdctest' (not 'cdctest-db')
    postgres_conn = next((c for c in conns if c.get('database') == 'cdctest' and c.get('database_type') == 'postgresql'), None)
    mssql_conn = next((c for c in conns if c.get('database') == 'cdctest' and c.get('database_type') == 'sqlserver'), None)
    
    # If not found, try to find by name
    if not postgres_conn:
        postgres_conn = next((c for c in conns if c.get('name') == 'POSTGRE' and c.get('database_type') == 'postgresql'), None)
    if not mssql_conn:
        mssql_conn = next((c for c in conns if c.get('name') == 'MS-SQL' and c.get('database_type') == 'sqlserver'), None)
    
    if not postgres_conn:
        print("   [ERROR] PostgreSQL connection not found")
        exit(1)
    if not mssql_conn:
        print("   [ERROR] SQL Server connection not found")
        exit(1)
    
    postgres_conn_id = postgres_conn.get('id')
    mssql_conn_id = mssql_conn.get('id')
    print(f"   [OK] PostgreSQL connection: {postgres_conn_id}")
    print(f"   [OK] SQL Server connection: {mssql_conn_id}")
else:
    print(f"   [ERROR] Failed to get connections: {conns_response.status_code}")
    exit(1)

# Step 3: Create new pipeline with correct database
print("\n3. Creating new 'final_test' pipeline with correct database...")
pipeline_data = {
    "name": "final_test",
    "source_connection_id": postgres_conn_id,
    "target_connection_id": mssql_conn_id,
    "source_database": "cdctest",  # Correct database name
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
    print(f"   Source DB: {pipeline.get('source_database')}")
    print(f"   Target DB: {pipeline.get('target_database')}")
else:
    print(f"   [ERROR] Failed to create pipeline: {response.status_code}")
    print(f"   Response: {response.text[:500]}")
    exit(1)

print("\n" + "=" * 80)
print("Pipeline fixed! Now run setup_final_test_pipeline.py to start it.")
print("=" * 80)


import requests

API_URL = "http://localhost:8000/api"
API_V1_URL = "http://localhost:8000/api/v1"

print("=" * 80)
print("Fixing Final Test Pipeline")
print("=" * 80)

# Step 1: Delete existing pipeline
print("\n1. Deleting existing 'final_test' pipeline...")
pipelines_response = requests.get(f"{API_URL}/pipelines")
if pipelines_response.status_code == 200:
    pipelines = pipelines_response.json()
    existing = next((p for p in pipelines if p.get('name') == 'final_test'), None)
    if existing:
        pipeline_id = existing.get('id')
        delete_response = requests.delete(f"{API_URL}/pipelines/{pipeline_id}?hard_delete=true")
        if delete_response.status_code in [200, 204]:
            print(f"   [OK] Deleted existing pipeline: {pipeline_id}")
        else:
            print(f"   [WARNING] Could not delete: {delete_response.status_code}")
    else:
        print("   [INFO] No existing pipeline found")

# Step 2: Get connections
print("\n2. Getting connections...")
conns_response = requests.get(f"{API_V1_URL}/connections")
if conns_response.status_code == 200:
    conns = conns_response.json()
    # Find connections with exact database name 'cdctest' (not 'cdctest-db')
    postgres_conn = next((c for c in conns if c.get('database') == 'cdctest' and c.get('database_type') == 'postgresql'), None)
    mssql_conn = next((c for c in conns if c.get('database') == 'cdctest' and c.get('database_type') == 'sqlserver'), None)
    
    # If not found, try to find by name
    if not postgres_conn:
        postgres_conn = next((c for c in conns if c.get('name') == 'POSTGRE' and c.get('database_type') == 'postgresql'), None)
    if not mssql_conn:
        mssql_conn = next((c for c in conns if c.get('name') == 'MS-SQL' and c.get('database_type') == 'sqlserver'), None)
    
    if not postgres_conn:
        print("   [ERROR] PostgreSQL connection not found")
        exit(1)
    if not mssql_conn:
        print("   [ERROR] SQL Server connection not found")
        exit(1)
    
    postgres_conn_id = postgres_conn.get('id')
    mssql_conn_id = mssql_conn.get('id')
    print(f"   [OK] PostgreSQL connection: {postgres_conn_id}")
    print(f"   [OK] SQL Server connection: {mssql_conn_id}")
else:
    print(f"   [ERROR] Failed to get connections: {conns_response.status_code}")
    exit(1)

# Step 3: Create new pipeline with correct database
print("\n3. Creating new 'final_test' pipeline with correct database...")
pipeline_data = {
    "name": "final_test",
    "source_connection_id": postgres_conn_id,
    "target_connection_id": mssql_conn_id,
    "source_database": "cdctest",  # Correct database name
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
    print(f"   Source DB: {pipeline.get('source_database')}")
    print(f"   Target DB: {pipeline.get('target_database')}")
else:
    print(f"   [ERROR] Failed to create pipeline: {response.status_code}")
    print(f"   Response: {response.text[:500]}")
    exit(1)

print("\n" + "=" * 80)
print("Pipeline fixed! Now run setup_final_test_pipeline.py to start it.")
print("=" * 80)

