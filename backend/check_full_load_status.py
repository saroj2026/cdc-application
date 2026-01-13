"""Check full load status for final_test pipeline."""

import requests
import psycopg2
import pyodbc

API_URL = "http://localhost:8000/api"

print("=" * 80)
print("Checking Full Load Status")
print("=" * 80)

# Get the latest final_test pipeline
print("\n1. Finding final_test pipeline...")
try:
    response = requests.get(f"{API_URL}/pipelines")
    if response.status_code == 200:
        pipelines = response.json()
        pipeline = next((p for p in pipelines if p.get('name') == 'final_test'), None)
        
        if pipeline:
            pipeline_id = pipeline.get('id')
            print(f"   [OK] Pipeline found: {pipeline_id}")
            print(f"   Status: {pipeline.get('status')}")
            print(f"   Full Load Status: {pipeline.get('full_load_status')}")
            print(f"   CDC Status: {pipeline.get('cdc_status')}")
            print(f"   Mode: {pipeline.get('mode')}")
            
            full_load_status = pipeline.get('full_load_status')
            if full_load_status == 'COMPLETED':
                print(f"\n   ✅ Full Load Status: COMPLETED")
            elif full_load_status == 'IN_PROGRESS':
                print(f"\n   ⏳ Full Load Status: IN_PROGRESS")
            elif full_load_status == 'NOT_STARTED':
                print(f"\n   ⚠️  Full Load Status: NOT_STARTED")
            elif full_load_status == 'FAILED':
                print(f"\n   ❌ Full Load Status: FAILED")
        else:
            print("   [ERROR] Pipeline not found")
            exit(1)
    else:
        print(f"   [ERROR] Failed to get pipelines: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"   [ERROR] Exception: {e}")
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
    
    cur.execute("SELECT project_id, project_name FROM public.projects_simple ORDER BY project_id;")
    pg_rows = cur.fetchall()
    
    cur.close()
    conn.close()
    
    print(f"   [OK] PostgreSQL rows: {pg_count}")
    print(f"   Data:")
    for row in pg_rows[:5]:  # Show first 5 rows
        print(f"      ID={row[0]}, Name={row[1]}")
    if pg_count > 5:
        print(f"      ... and {pg_count - 5} more rows")
        
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
        f"PWD=Sql@12345;"
        f"TrustServerCertificate=yes;"
        f"Encrypt=no;"
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
        
        cur.execute("SELECT project_id, project_name FROM dbo.projects_simple ORDER BY project_id;")
        mssql_rows = cur.fetchall()
        
        print(f"   [OK] SQL Server table exists")
        print(f"   [OK] SQL Server rows: {mssql_count}")
        
        if mssql_count > 0:
            print(f"   Data:")
            for row in mssql_rows[:5]:  # Show first 5 rows
                print(f"      ID={row[0]}, Name={row[1]}")
            if mssql_count > 5:
                print(f"      ... and {mssql_count - 5} more rows")
        
        # Compare counts
        print(f"\n4. Comparing data...")
        if pg_count == mssql_count:
            print(f"   ✅ Row counts match! ({pg_count} rows in both)")
            print(f"   ✅ Full load is complete!")
        else:
            print(f"   ⚠️  Row count mismatch:")
            print(f"      PostgreSQL: {pg_count} rows")
            print(f"      SQL Server: {mssql_count} rows")
            print(f"      Missing: {pg_count - mssql_count} rows")
            print(f"   ⚠️  Full load may not be complete")
    else:
        print(f"   [WARNING] Table dbo.projects_simple does not exist")
        print(f"   ⚠️  Full load has not created the table")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"   [ERROR] Failed to check SQL Server: {e}")

print("\n" + "=" * 80)
print("Full Load Status Check Complete!")
print("=" * 80)

import requests
import psycopg2
import pyodbc

API_URL = "http://localhost:8000/api"

print("=" * 80)
print("Checking Full Load Status")
print("=" * 80)

# Get the latest final_test pipeline
print("\n1. Finding final_test pipeline...")
try:
    response = requests.get(f"{API_URL}/pipelines")
    if response.status_code == 200:
        pipelines = response.json()
        pipeline = next((p for p in pipelines if p.get('name') == 'final_test'), None)
        
        if pipeline:
            pipeline_id = pipeline.get('id')
            print(f"   [OK] Pipeline found: {pipeline_id}")
            print(f"   Status: {pipeline.get('status')}")
            print(f"   Full Load Status: {pipeline.get('full_load_status')}")
            print(f"   CDC Status: {pipeline.get('cdc_status')}")
            print(f"   Mode: {pipeline.get('mode')}")
            
            full_load_status = pipeline.get('full_load_status')
            if full_load_status == 'COMPLETED':
                print(f"\n   ✅ Full Load Status: COMPLETED")
            elif full_load_status == 'IN_PROGRESS':
                print(f"\n   ⏳ Full Load Status: IN_PROGRESS")
            elif full_load_status == 'NOT_STARTED':
                print(f"\n   ⚠️  Full Load Status: NOT_STARTED")
            elif full_load_status == 'FAILED':
                print(f"\n   ❌ Full Load Status: FAILED")
        else:
            print("   [ERROR] Pipeline not found")
            exit(1)
    else:
        print(f"   [ERROR] Failed to get pipelines: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"   [ERROR] Exception: {e}")
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
    
    cur.execute("SELECT project_id, project_name FROM public.projects_simple ORDER BY project_id;")
    pg_rows = cur.fetchall()
    
    cur.close()
    conn.close()
    
    print(f"   [OK] PostgreSQL rows: {pg_count}")
    print(f"   Data:")
    for row in pg_rows[:5]:  # Show first 5 rows
        print(f"      ID={row[0]}, Name={row[1]}")
    if pg_count > 5:
        print(f"      ... and {pg_count - 5} more rows")
        
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
        f"PWD=Sql@12345;"
        f"TrustServerCertificate=yes;"
        f"Encrypt=no;"
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
        
        cur.execute("SELECT project_id, project_name FROM dbo.projects_simple ORDER BY project_id;")
        mssql_rows = cur.fetchall()
        
        print(f"   [OK] SQL Server table exists")
        print(f"   [OK] SQL Server rows: {mssql_count}")
        
        if mssql_count > 0:
            print(f"   Data:")
            for row in mssql_rows[:5]:  # Show first 5 rows
                print(f"      ID={row[0]}, Name={row[1]}")
            if mssql_count > 5:
                print(f"      ... and {mssql_count - 5} more rows")
        
        # Compare counts
        print(f"\n4. Comparing data...")
        if pg_count == mssql_count:
            print(f"   ✅ Row counts match! ({pg_count} rows in both)")
            print(f"   ✅ Full load is complete!")
        else:
            print(f"   ⚠️  Row count mismatch:")
            print(f"      PostgreSQL: {pg_count} rows")
            print(f"      SQL Server: {mssql_count} rows")
            print(f"      Missing: {pg_count - mssql_count} rows")
            print(f"   ⚠️  Full load may not be complete")
    else:
        print(f"   [WARNING] Table dbo.projects_simple does not exist")
        print(f"   ⚠️  Full load has not created the table")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"   [ERROR] Failed to check SQL Server: {e}")

print("\n" + "=" * 80)
print("Full Load Status Check Complete!")
print("=" * 80)
