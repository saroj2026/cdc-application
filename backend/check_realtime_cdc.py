"""Check if real-time CDC is working by comparing row counts."""

import psycopg2
import pyodbc
import time

VM_PG_HOST = "72.61.241.193"
VM_PG_PORT = 5432
VM_PG_DATABASE = "openmetadata_db"
VM_PG_USER = "cdc_user"
VM_PG_PASSWORD = "cdc_password"

SQL_SERVER_HOST = "72.61.233.209"
SQL_SERVER_PORT = 1433
SQL_SERVER_DATABASE = "cdctest"
SQL_SERVER_USER = "SA"
SQL_SERVER_PASSWORD = "Sql@12345"

print("=" * 60)
print("Checking Real-Time CDC Status")
print("=" * 60)

# Get PostgreSQL count
print("\n1. Checking PostgreSQL (source)...")
try:
    pg_conn = psycopg2.connect(
        host=VM_PG_HOST,
        port=VM_PG_PORT,
        database=VM_PG_DATABASE,
        user=VM_PG_USER,
        password=VM_PG_PASSWORD,
        connect_timeout=10
    )
    pg_cursor = pg_conn.cursor()
    pg_cursor.execute("SELECT COUNT(*) FROM public.cdc_test")
    pg_count = pg_cursor.fetchone()[0]
    
    # Get latest rows
    pg_cursor.execute("SELECT name FROM public.cdc_test ORDER BY (SELECT NULL) LIMIT 5")
    pg_rows = [row[0] for row in pg_cursor.fetchall()]
    
    print(f"   Rows: {pg_count}")
    print(f"   Sample data: {pg_rows}")
    
    pg_cursor.close()
    pg_conn.close()
except Exception as e:
    print(f"   Error: {e}")
    exit(1)

# Get SQL Server count
print("\n2. Checking SQL Server (target)...")
try:
    sql_conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SQL_SERVER_HOST},{SQL_SERVER_PORT};"
        f"DATABASE={SQL_SERVER_DATABASE};"
        f"UID={SQL_SERVER_USER};"
        f"PWD={SQL_SERVER_PASSWORD};"
        f"TrustServerCertificate=yes;"
        f"Encrypt=no;"
    )
    sql_conn = pyodbc.connect(sql_conn_str, timeout=10)
    sql_cursor = sql_conn.cursor()
    
    sql_cursor.execute("SELECT COUNT(*) FROM dbo.cdc_test")
    sql_count = sql_cursor.fetchone()[0]
    
    # Get latest rows
    sql_cursor.execute("SELECT TOP 5 name FROM dbo.cdc_test ORDER BY (SELECT NULL)")
    sql_rows = [row[0] for row in sql_cursor.fetchall()]
    
    print(f"   Rows: {sql_count}")
    print(f"   Sample data: {sql_rows}")
    
    sql_cursor.close()
    sql_conn.close()
except Exception as e:
    print(f"   Error: {e}")
    exit(1)

# Compare
print("\n3. Comparison:")
print(f"   PostgreSQL: {pg_count} rows")
print(f"   SQL Server: {sql_count} rows")
print(f"   Difference: {pg_count - sql_count} rows")

if sql_count == pg_count:
    print("\n   SUCCESS: Row counts match!")
    print("   Real-time CDC is working correctly!")
elif sql_count < pg_count:
    print(f"\n   WARNING: SQL Server has {pg_count - sql_count} fewer rows")
    print("   CDC may still be processing, or there's a replication issue")
    print("\n   To test real-time CDC:")
    print("   1. Insert a new row in PostgreSQL")
    print("   2. Wait 10-15 seconds")
    print("   3. Run this script again to verify replication")
else:
    print(f"\n   ERROR: SQL Server has more rows than PostgreSQL (unexpected)")

print("\n" + "=" * 60)


