"""Verify final_test pipeline data transfer."""

import requests
import psycopg2
import pyodbc

API_URL = "http://localhost:8000/api"

print("=" * 80)
print("Verifying Final Test Pipeline")
print("=" * 80)

# Step 1: Check pipeline status
print("\n1. Checking pipeline status...")
response = requests.get(f"{API_URL}/pipelines")
if response.status_code == 200:
    pipelines = response.json()
    pipeline = next((p for p in pipelines if p.get('name') == 'final_test'), None)
    if pipeline:
        print(f"   [OK] Pipeline: {pipeline.get('name')}")
        print(f"   Status: {pipeline.get('status')}")
        print(f"   Full Load Status: {pipeline.get('full_load_status')}")
        print(f"   CDC Status: {pipeline.get('cdc_status')}")
        print(f"   Debezium Connector: {pipeline.get('debezium_connector_name', 'None')}")
        print(f"   Sink Connector: {pipeline.get('sink_connector_name', 'None')}")
    else:
        print("   [ERROR] Pipeline not found")
        exit(1)
else:
    print(f"   [ERROR] Failed to get pipelines: {response.status_code}")
    exit(1)

# Step 2: Check source data (PostgreSQL)
print("\n2. Checking source data in PostgreSQL...")
try:
    conn = psycopg2.connect(
        host="72.61.233.209",
        port=5432,
        user="cdc_user",
        password="cdc_pass",
        database="cdctest"
    )
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM public.projects_simple;")
    pg_count = cur.fetchone()[0]
    cur.execute("SELECT * FROM public.projects_simple ORDER BY project_id;")
    pg_rows = cur.fetchall()
    cur.close()
    conn.close()
    
    print(f"   [OK] PostgreSQL rows: {pg_count}")
    print(f"   Data:")
    for row in pg_rows:
        print(f"      {row}")
except Exception as e:
    print(f"   [ERROR] Failed to check PostgreSQL: {e}")

# Step 3: Check target data (SQL Server)
print("\n3. Checking target data in SQL Server...")
try:
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER=72.61.233.209,1433;"
        f"DATABASE=cdctest;"
        f"UID=sa;"
        f"PWD=Sql@12345"
    )
    cur = conn.cursor()
    
    # Check if table exists
    cur.execute("""
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = 'dbo' 
        AND TABLE_NAME = 'projects_simple';
    """)
    table_exists = cur.fetchone()[0] > 0
    
    if table_exists:
        cur.execute("SELECT COUNT(*) FROM dbo.projects_simple;")
        mssql_count = cur.fetchone()[0]
        cur.execute("SELECT * FROM dbo.projects_simple ORDER BY project_id;")
        mssql_rows = cur.fetchall()
        
        print(f"   [OK] SQL Server table exists")
        print(f"   [OK] SQL Server rows: {mssql_count}")
        print(f"   Data:")
        for row in mssql_rows:
            print(f"      {row}")
        
        # Compare counts
        if pg_count == mssql_count:
            print(f"\n   ✅ Data matches! ({pg_count} rows in both)")
        else:
            print(f"\n   ⚠️  Row count mismatch: PostgreSQL={pg_count}, SQL Server={mssql_count}")
    else:
        print(f"   [WARNING] Table dbo.projects_simple does not exist yet")
        print(f"   This might mean full load hasn't completed or table creation failed")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"   [ERROR] Failed to check SQL Server: {e}")
    print(f"   Error details: {str(e)}")

print("\n" + "=" * 80)
print("Verification Complete!")
print("=" * 80)


import requests
import psycopg2
import pyodbc

API_URL = "http://localhost:8000/api"

print("=" * 80)
print("Verifying Final Test Pipeline")
print("=" * 80)

# Step 1: Check pipeline status
print("\n1. Checking pipeline status...")
response = requests.get(f"{API_URL}/pipelines")
if response.status_code == 200:
    pipelines = response.json()
    pipeline = next((p for p in pipelines if p.get('name') == 'final_test'), None)
    if pipeline:
        print(f"   [OK] Pipeline: {pipeline.get('name')}")
        print(f"   Status: {pipeline.get('status')}")
        print(f"   Full Load Status: {pipeline.get('full_load_status')}")
        print(f"   CDC Status: {pipeline.get('cdc_status')}")
        print(f"   Debezium Connector: {pipeline.get('debezium_connector_name', 'None')}")
        print(f"   Sink Connector: {pipeline.get('sink_connector_name', 'None')}")
    else:
        print("   [ERROR] Pipeline not found")
        exit(1)
else:
    print(f"   [ERROR] Failed to get pipelines: {response.status_code}")
    exit(1)

# Step 2: Check source data (PostgreSQL)
print("\n2. Checking source data in PostgreSQL...")
try:
    conn = psycopg2.connect(
        host="72.61.233.209",
        port=5432,
        user="cdc_user",
        password="cdc_pass",
        database="cdctest"
    )
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM public.projects_simple;")
    pg_count = cur.fetchone()[0]
    cur.execute("SELECT * FROM public.projects_simple ORDER BY project_id;")
    pg_rows = cur.fetchall()
    cur.close()
    conn.close()
    
    print(f"   [OK] PostgreSQL rows: {pg_count}")
    print(f"   Data:")
    for row in pg_rows:
        print(f"      {row}")
except Exception as e:
    print(f"   [ERROR] Failed to check PostgreSQL: {e}")

# Step 3: Check target data (SQL Server)
print("\n3. Checking target data in SQL Server...")
try:
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER=72.61.233.209,1433;"
        f"DATABASE=cdctest;"
        f"UID=sa;"
        f"PWD=Sql@12345"
    )
    cur = conn.cursor()
    
    # Check if table exists
    cur.execute("""
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = 'dbo' 
        AND TABLE_NAME = 'projects_simple';
    """)
    table_exists = cur.fetchone()[0] > 0
    
    if table_exists:
        cur.execute("SELECT COUNT(*) FROM dbo.projects_simple;")
        mssql_count = cur.fetchone()[0]
        cur.execute("SELECT * FROM dbo.projects_simple ORDER BY project_id;")
        mssql_rows = cur.fetchall()
        
        print(f"   [OK] SQL Server table exists")
        print(f"   [OK] SQL Server rows: {mssql_count}")
        print(f"   Data:")
        for row in mssql_rows:
            print(f"      {row}")
        
        # Compare counts
        if pg_count == mssql_count:
            print(f"\n   ✅ Data matches! ({pg_count} rows in both)")
        else:
            print(f"\n   ⚠️  Row count mismatch: PostgreSQL={pg_count}, SQL Server={mssql_count}")
    else:
        print(f"   [WARNING] Table dbo.projects_simple does not exist yet")
        print(f"   This might mean full load hasn't completed or table creation failed")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"   [ERROR] Failed to check SQL Server: {e}")
    print(f"   Error details: {str(e)}")

print("\n" + "=" * 80)
print("Verification Complete!")
print("=" * 80)

