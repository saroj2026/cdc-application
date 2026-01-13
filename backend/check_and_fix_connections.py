"""Check and fix connections with correct database names."""

import requests

API_V1_URL = "http://localhost:8000/api/v1"

print("=" * 80)
print("Checking Connections")
print("=" * 80)

# Get all connections
response = requests.get(f"{API_V1_URL}/connections")
if response.status_code == 200:
    conns = response.json()
    print(f"\nFound {len(conns)} connection(s):\n")
    
    postgres_conn = None
    mssql_conn = None
    
    for conn in conns:
        db_type = conn.get('database_type', '')
        db_name = conn.get('database', '')
        conn_id = conn.get('id')
        conn_name = conn.get('name', '')
        
        print(f"  {conn_name}")
        print(f"    Type: {db_type}")
        print(f"    Database: {db_name}")
        print(f"    ID: {conn_id}")
        
        if db_type == 'postgresql' and db_name == 'cdctest':
            postgres_conn = conn
            print(f"    ✅ Correct PostgreSQL connection")
        elif db_type == 'sqlserver' and db_name == 'cdctest':
            mssql_conn = conn
            print(f"    ✅ Correct SQL Server connection")
        elif db_type == 'postgresql' and 'cdctest-db' in db_name:
            print(f"    ⚠️  Wrong database name: {db_name}")
        print()
    
    if not postgres_conn:
        print("❌ No correct PostgreSQL connection found (cdctest database)")
        print("   Creating new one...")
        # Create correct PostgreSQL connection
        conn_data = {
            "name": "PostgreSQL_cdctest_FinalTest",
            "connection_type": "source",
            "database_type": "postgresql",
            "host": "72.61.233.209",
            "port": 5432,
            "database": "cdctest",
            "username": "cdc_user",
            "password": "cdc_pass",
            "schema": "public"
        }
        create_response = requests.post(f"{API_V1_URL}/connections", json=conn_data)
        if create_response.status_code == 201:
            postgres_conn = create_response.json()
            print(f"   ✅ Created: {postgres_conn.get('id')}")
        else:
            print(f"   ❌ Failed: {create_response.status_code}")
    
    if not mssql_conn:
        print("❌ No correct SQL Server connection found (cdctest database)")
        print("   Creating new one...")
        # Create correct SQL Server connection
        conn_data = {
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
        create_response = requests.post(f"{API_V1_URL}/connections", json=conn_data)
        if create_response.status_code == 201:
            mssql_conn = create_response.json()
            print(f"   ✅ Created: {mssql_conn.get('id')}")
        else:
            print(f"   ❌ Failed: {create_response.status_code}")
    
    if postgres_conn and mssql_conn:
        print("\n" + "=" * 80)
        print("✅ Correct connections ready!")
        print("=" * 80)
        print(f"\nPostgreSQL: {postgres_conn.get('id')}")
        print(f"SQL Server: {mssql_conn.get('id')}")
        print(f"\nUse these connection IDs in the pipeline setup.")
    else:
        print("\n❌ Could not ensure correct connections exist")


import requests

API_V1_URL = "http://localhost:8000/api/v1"

print("=" * 80)
print("Checking Connections")
print("=" * 80)

# Get all connections
response = requests.get(f"{API_V1_URL}/connections")
if response.status_code == 200:
    conns = response.json()
    print(f"\nFound {len(conns)} connection(s):\n")
    
    postgres_conn = None
    mssql_conn = None
    
    for conn in conns:
        db_type = conn.get('database_type', '')
        db_name = conn.get('database', '')
        conn_id = conn.get('id')
        conn_name = conn.get('name', '')
        
        print(f"  {conn_name}")
        print(f"    Type: {db_type}")
        print(f"    Database: {db_name}")
        print(f"    ID: {conn_id}")
        
        if db_type == 'postgresql' and db_name == 'cdctest':
            postgres_conn = conn
            print(f"    ✅ Correct PostgreSQL connection")
        elif db_type == 'sqlserver' and db_name == 'cdctest':
            mssql_conn = conn
            print(f"    ✅ Correct SQL Server connection")
        elif db_type == 'postgresql' and 'cdctest-db' in db_name:
            print(f"    ⚠️  Wrong database name: {db_name}")
        print()
    
    if not postgres_conn:
        print("❌ No correct PostgreSQL connection found (cdctest database)")
        print("   Creating new one...")
        # Create correct PostgreSQL connection
        conn_data = {
            "name": "PostgreSQL_cdctest_FinalTest",
            "connection_type": "source",
            "database_type": "postgresql",
            "host": "72.61.233.209",
            "port": 5432,
            "database": "cdctest",
            "username": "cdc_user",
            "password": "cdc_pass",
            "schema": "public"
        }
        create_response = requests.post(f"{API_V1_URL}/connections", json=conn_data)
        if create_response.status_code == 201:
            postgres_conn = create_response.json()
            print(f"   ✅ Created: {postgres_conn.get('id')}")
        else:
            print(f"   ❌ Failed: {create_response.status_code}")
    
    if not mssql_conn:
        print("❌ No correct SQL Server connection found (cdctest database)")
        print("   Creating new one...")
        # Create correct SQL Server connection
        conn_data = {
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
        create_response = requests.post(f"{API_V1_URL}/connections", json=conn_data)
        if create_response.status_code == 201:
            mssql_conn = create_response.json()
            print(f"   ✅ Created: {mssql_conn.get('id')}")
        else:
            print(f"   ❌ Failed: {create_response.status_code}")
    
    if postgres_conn and mssql_conn:
        print("\n" + "=" * 80)
        print("✅ Correct connections ready!")
        print("=" * 80)
        print(f"\nPostgreSQL: {postgres_conn.get('id')}")
        print(f"SQL Server: {mssql_conn.get('id')}")
        print(f"\nUse these connection IDs in the pipeline setup.")
    else:
        print("\n❌ Could not ensure correct connections exist")

