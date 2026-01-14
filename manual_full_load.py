"""Manually run full load for projects_simple table."""

import psycopg2
import pyodbc
from ingestion.connectors.postgresql import PostgreSQLConnector
from ingestion.connectors.sqlserver import SQLServerConnector
from ingestion.transfer import DataTransfer

print("=" * 80)
print("Manual Full Load for projects_simple")
print("=" * 80)

# Initialize connectors
print("\n1. Initializing connectors...")
source_config = {
    "host": "72.61.233.209",
    "port": 5432,
    "database": "cdctest",
    "user": "cdc_user",
    "password": "cdc_pass"
}
source_connector = PostgreSQLConnector(source_config)

target_config = {
    "server": "72.61.233.209",
    "port": 1433,
    "database": "cdctest",
    "user": "sa",
    "password": "Sql@12345",
    "trust_server_certificate": True,
    "encrypt": False
}
target_connector = SQLServerConnector(target_config)

print("   [OK] Connectors initialized")

# Initialize data transfer
print("\n2. Initializing data transfer...")
transfer = DataTransfer(source_connector, target_connector)
print("   [OK] Data transfer initialized")

# Transfer table
print("\n3. Transferring table 'projects_simple'...")
print("   Source: cdctest.public.projects_simple")
print("   Target: cdctest.dbo.projects_simple")
try:
    result = transfer.transfer_table(
        table_name="projects_simple",
        source_database="cdctest",
        source_schema="public",
        target_database="cdctest",
        target_schema="dbo",
        transfer_schema=True,
        transfer_data=True,
        batch_size=1000,
        create_if_not_exists=True
    )
    
    print(f"\n   Transfer Result:")
    print(f"   Schema transferred: {result.get('schema_transferred', False)}")
    print(f"   Data transferred: {result.get('data_transferred', False)}")
    print(f"   Rows transferred: {result.get('rows_transferred', 0)}")
    
    if result.get('errors'):
        print(f"   Errors: {result.get('errors')}")
    else:
        print(f"   ✅ Transfer successful!")
        
except Exception as e:
    print(f"   [ERROR] Transfer failed: {e}")
    import traceback
    traceback.print_exc()

# Verify
print("\n4. Verifying data...")
try:
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER=72.61.233.209,1433;"
        f"DATABASE=cdctest;"
        f"UID=sa;"
        f"PWD=Sql@12345"
    )
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM dbo.projects_simple;")
    count = cur.fetchone()[0]
    print(f"   SQL Server rows: {count}")
    
    if count > 0:
        print(f"   ✅ Data verified!")
    else:
        print(f"   ⚠️  No data found")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"   [ERROR] Verification failed: {e}")

print("\n" + "=" * 80)
print("Manual Full Load Complete!")
print("=" * 80)


import psycopg2
import pyodbc
from ingestion.connectors.postgresql import PostgreSQLConnector
from ingestion.connectors.sqlserver import SQLServerConnector
from ingestion.transfer import DataTransfer

print("=" * 80)
print("Manual Full Load for projects_simple")
print("=" * 80)

# Initialize connectors
print("\n1. Initializing connectors...")
source_config = {
    "host": "72.61.233.209",
    "port": 5432,
    "database": "cdctest",
    "user": "cdc_user",
    "password": "cdc_pass"
}
source_connector = PostgreSQLConnector(source_config)

target_config = {
    "server": "72.61.233.209",
    "port": 1433,
    "database": "cdctest",
    "user": "sa",
    "password": "Sql@12345",
    "trust_server_certificate": True,
    "encrypt": False
}
target_connector = SQLServerConnector(target_config)

print("   [OK] Connectors initialized")

# Initialize data transfer
print("\n2. Initializing data transfer...")
transfer = DataTransfer(source_connector, target_connector)
print("   [OK] Data transfer initialized")

# Transfer table
print("\n3. Transferring table 'projects_simple'...")
print("   Source: cdctest.public.projects_simple")
print("   Target: cdctest.dbo.projects_simple")
try:
    result = transfer.transfer_table(
        table_name="projects_simple",
        source_database="cdctest",
        source_schema="public",
        target_database="cdctest",
        target_schema="dbo",
        transfer_schema=True,
        transfer_data=True,
        batch_size=1000,
        create_if_not_exists=True
    )
    
    print(f"\n   Transfer Result:")
    print(f"   Schema transferred: {result.get('schema_transferred', False)}")
    print(f"   Data transferred: {result.get('data_transferred', False)}")
    print(f"   Rows transferred: {result.get('rows_transferred', 0)}")
    
    if result.get('errors'):
        print(f"   Errors: {result.get('errors')}")
    else:
        print(f"   ✅ Transfer successful!")
        
except Exception as e:
    print(f"   [ERROR] Transfer failed: {e}")
    import traceback
    traceback.print_exc()

# Verify
print("\n4. Verifying data...")
try:
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER=72.61.233.209,1433;"
        f"DATABASE=cdctest;"
        f"UID=sa;"
        f"PWD=Sql@12345"
    )
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM dbo.projects_simple;")
    count = cur.fetchone()[0]
    print(f"   SQL Server rows: {count}")
    
    if count > 0:
        print(f"   ✅ Data verified!")
    else:
        print(f"   ⚠️  No data found")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"   [ERROR] Verification failed: {e}")

print("\n" + "=" * 80)
print("Manual Full Load Complete!")
print("=" * 80)

