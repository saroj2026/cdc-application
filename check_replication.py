"""Check if data was replicated from PostgreSQL to SQL Server."""

import psycopg2
import pyodbc
from datetime import datetime

print("=" * 60)
print("Checking Data Replication")
print("=" * 60)

# Connection details
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
    
    # Get row count
    pg_cursor.execute("SELECT COUNT(*) FROM public.cdc_test")
    pg_count = pg_cursor.fetchone()[0]
    
    # Get column names first
    pg_cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'cdc_test'
        ORDER BY ordinal_position
    """)
    pg_columns = [row[0] for row in pg_cursor.fetchall()]
    
    # Get all rows (limit to 10 for display)
    pg_cursor.execute("SELECT * FROM public.cdc_test LIMIT 10")
    pg_rows = pg_cursor.fetchall()
    
    print(f"   ✓ PostgreSQL: {pg_count} rows")
    print(f"   Columns: {', '.join(pg_columns)}")
    
    pg_cursor.close()
    pg_conn.close()
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

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
    
    # Check if table exists
    sql_cursor.execute("""
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = 'dbo' 
        AND TABLE_NAME = 'cdc_test'
    """)
    table_exists = sql_cursor.fetchone()[0] > 0
    
    if table_exists:
        # Get row count
        sql_cursor.execute("SELECT COUNT(*) FROM dbo.cdc_test")
        sql_count = sql_cursor.fetchone()[0]
        
        # Get column names first
        sql_cursor.execute("""
            SELECT column_name 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'dbo' 
            AND TABLE_NAME = 'cdc_test'
            ORDER BY ordinal_position
        """)
        sql_columns = [row[0] for row in sql_cursor.fetchall()]
        
        # Get all rows
        sql_cursor.execute("SELECT * FROM dbo.cdc_test")
        sql_rows = sql_cursor.fetchall()
        
        print(f"   ✓ SQL Server: Table exists")
        print(f"   ✓ Row count: {sql_count}")
        print(f"   Columns: {', '.join(sql_columns)}")
        
        print("\n3. Comparing data...")
        if sql_count == pg_count:
            print(f"   ✓ Row counts match! ({pg_count} rows in both)")
            print("\n   Sample data from SQL Server:")
            for i, row in enumerate(sql_rows[:5], 1):
                print(f"   Row {i}: {dict(zip(sql_columns, row))}")
        elif sql_count < pg_count:
            print(f"   ⚠ SQL Server has fewer rows ({sql_count} vs {pg_count})")
            print("   CDC may still be processing...")
        else:
            print(f"   ⚠ SQL Server has more rows ({sql_count} vs {pg_count})")
    else:
        print("   ✗ Table 'cdc_test' does not exist in SQL Server")
        print("   The sink connector should auto-create it when first message arrives")
        print("   Check Kafka Connect logs if messages are not being processed")
    
    sql_cursor.close()
    sql_conn.close()
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 60)
if table_exists and sql_count >= pg_count:
    print("✓ REPLICATION SUCCESSFUL!")
    print("=" * 60)
else:
    print("⚠ Replication status: Check details above")
    print("=" * 60)

