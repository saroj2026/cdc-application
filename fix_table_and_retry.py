"""Drop and recreate table with correct schema, then retry transfer."""

import pyodbc
import psycopg2
from ingestion.connectors.postgresql import PostgreSQLConnector
from ingestion.connectors.sqlserver import SQLServerConnector
from ingestion.transfer import DataTransfer

print("=" * 80)
print("Fixing Table Schema and Retrying Transfer")
print("=" * 80)

# Step 1: Get correct schema from PostgreSQL
print("\n1. Getting schema from PostgreSQL...")
try:
    pg_conn = psycopg2.connect(
        host="72.61.233.209",
        port=5432,
        user="cdc_user",
        password="cdc_pass",
        database="cdctest"
    )
    pg_cur = pg_conn.cursor()
    
    pg_cur.execute("""
        SELECT column_name, data_type, character_maximum_length, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public' 
        AND table_name = 'projects_simple'
        ORDER BY ordinal_position;
    """)
    columns = pg_cur.fetchall()
    
    print(f"   [OK] Found {len(columns)} columns")
    for col in columns:
        print(f"      {col[0]}: {col[1]} (max_len={col[2]}, nullable={col[3]})")
    
    pg_cur.close()
    pg_conn.close()
    
except Exception as e:
    print(f"   [ERROR] Failed to get schema: {e}")
    exit(1)

# Step 2: Drop and recreate table in SQL Server
print("\n2. Dropping and recreating table in SQL Server...")
try:
    mssql_conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER=72.61.233.209,1433;"
        f"DATABASE=cdctest;"
        f"UID=sa;"
        f"PWD=Sql@12345;"
        f"TrustServerCertificate=yes;"
        f"Encrypt=no;"
    )
    mssql_cur = mssql_conn.cursor()
    
    # Drop table
    print("   Dropping existing table...")
    mssql_cur.execute("DROP TABLE IF EXISTS dbo.projects_simple;")
    mssql_conn.commit()
    print("   [OK] Table dropped")
    
    # Create table with correct schema
    print("   Creating table with correct schema...")
    create_sql = "CREATE TABLE dbo.projects_simple ("
    col_defs = []
    
    for col in columns:
        col_name = col[0]
        col_type = col[1]
        max_len = col[2]
        is_nullable = col[3] == 'YES'
        
        # Map PostgreSQL types to SQL Server types
        if col_type == 'integer':
            sql_type = 'INT'
        elif col_type == 'character varying' or col_type == 'varchar':
            if max_len:
                sql_type = f'VARCHAR({max_len})'
            else:
                sql_type = 'VARCHAR(MAX)'
        elif col_type == 'date':
            sql_type = 'DATE'
        elif col_type == 'text':
            sql_type = 'TEXT'
        else:
            sql_type = 'VARCHAR(MAX)'
        
        null_str = 'NULL' if is_nullable else 'NOT NULL'
        col_defs.append(f"[{col_name}] {sql_type} {null_str}")
    
    create_sql += ", ".join(col_defs) + ");"
    print(f"   SQL: {create_sql[:150]}...")
    
    mssql_cur.execute(create_sql)
    mssql_conn.commit()
    print("   [OK] Table created")
    
    mssql_cur.close()
    mssql_conn.close()
    
except Exception as e:
    print(f"   [ERROR] Failed to recreate table: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 3: Retry transfer
print("\n3. Retrying data transfer...")
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

transfer = DataTransfer(source_connector, target_connector)

try:
    result = transfer.transfer_table(
        table_name="projects_simple",
        source_database="cdctest",
        source_schema="public",
        target_database="cdctest",
        target_schema="dbo",
        transfer_schema=False,  # Don't recreate schema, we just did it
        transfer_data=True,
        batch_size=1000,
        create_if_not_exists=False
    )
    
    print(f"\n   Transfer Result:")
    print(f"   Data transferred: {result.get('data_transferred', False)}")
    print(f"   Rows transferred: {result.get('rows_transferred', 0)}")
    
    if result.get('errors'):
        print(f"   Errors:")
        for error in result.get('errors', []):
            print(f"      - {error[:200]}")
    else:
        print(f"   ✅ Transfer successful!")
        
except Exception as e:
    print(f"   [ERROR] Transfer failed: {e}")
    import traceback
    traceback.print_exc()

# Step 4: Verify
print("\n4. Verifying data...")
try:
    mssql_conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER=72.61.233.209,1433;"
        f"DATABASE=cdctest;"
        f"UID=sa;"
        f"PWD=Sql@12345;"
        f"TrustServerCertificate=yes;"
        f"Encrypt=no;"
    )
    mssql_cur = mssql_conn.cursor()
    mssql_cur.execute("SELECT COUNT(*) FROM dbo.projects_simple;")
    count = mssql_cur.fetchone()[0]
    print(f"   SQL Server rows: {count}")
    
    if count > 0:
        print(f"   ✅ Data verified!")
    else:
        print(f"   ⚠️  No data found")
    
    mssql_cur.close()
    mssql_conn.close()
except Exception as e:
    print(f"   [ERROR] Verification failed: {e}")

print("\n" + "=" * 80)
print("Fix and Retry Complete!")
print("=" * 80)


import pyodbc
import psycopg2
from ingestion.connectors.postgresql import PostgreSQLConnector
from ingestion.connectors.sqlserver import SQLServerConnector
from ingestion.transfer import DataTransfer

print("=" * 80)
print("Fixing Table Schema and Retrying Transfer")
print("=" * 80)

# Step 1: Get correct schema from PostgreSQL
print("\n1. Getting schema from PostgreSQL...")
try:
    pg_conn = psycopg2.connect(
        host="72.61.233.209",
        port=5432,
        user="cdc_user",
        password="cdc_pass",
        database="cdctest"
    )
    pg_cur = pg_conn.cursor()
    
    pg_cur.execute("""
        SELECT column_name, data_type, character_maximum_length, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public' 
        AND table_name = 'projects_simple'
        ORDER BY ordinal_position;
    """)
    columns = pg_cur.fetchall()
    
    print(f"   [OK] Found {len(columns)} columns")
    for col in columns:
        print(f"      {col[0]}: {col[1]} (max_len={col[2]}, nullable={col[3]})")
    
    pg_cur.close()
    pg_conn.close()
    
except Exception as e:
    print(f"   [ERROR] Failed to get schema: {e}")
    exit(1)

# Step 2: Drop and recreate table in SQL Server
print("\n2. Dropping and recreating table in SQL Server...")
try:
    mssql_conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER=72.61.233.209,1433;"
        f"DATABASE=cdctest;"
        f"UID=sa;"
        f"PWD=Sql@12345;"
        f"TrustServerCertificate=yes;"
        f"Encrypt=no;"
    )
    mssql_cur = mssql_conn.cursor()
    
    # Drop table
    print("   Dropping existing table...")
    mssql_cur.execute("DROP TABLE IF EXISTS dbo.projects_simple;")
    mssql_conn.commit()
    print("   [OK] Table dropped")
    
    # Create table with correct schema
    print("   Creating table with correct schema...")
    create_sql = "CREATE TABLE dbo.projects_simple ("
    col_defs = []
    
    for col in columns:
        col_name = col[0]
        col_type = col[1]
        max_len = col[2]
        is_nullable = col[3] == 'YES'
        
        # Map PostgreSQL types to SQL Server types
        if col_type == 'integer':
            sql_type = 'INT'
        elif col_type == 'character varying' or col_type == 'varchar':
            if max_len:
                sql_type = f'VARCHAR({max_len})'
            else:
                sql_type = 'VARCHAR(MAX)'
        elif col_type == 'date':
            sql_type = 'DATE'
        elif col_type == 'text':
            sql_type = 'TEXT'
        else:
            sql_type = 'VARCHAR(MAX)'
        
        null_str = 'NULL' if is_nullable else 'NOT NULL'
        col_defs.append(f"[{col_name}] {sql_type} {null_str}")
    
    create_sql += ", ".join(col_defs) + ");"
    print(f"   SQL: {create_sql[:150]}...")
    
    mssql_cur.execute(create_sql)
    mssql_conn.commit()
    print("   [OK] Table created")
    
    mssql_cur.close()
    mssql_conn.close()
    
except Exception as e:
    print(f"   [ERROR] Failed to recreate table: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 3: Retry transfer
print("\n3. Retrying data transfer...")
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

transfer = DataTransfer(source_connector, target_connector)

try:
    result = transfer.transfer_table(
        table_name="projects_simple",
        source_database="cdctest",
        source_schema="public",
        target_database="cdctest",
        target_schema="dbo",
        transfer_schema=False,  # Don't recreate schema, we just did it
        transfer_data=True,
        batch_size=1000,
        create_if_not_exists=False
    )
    
    print(f"\n   Transfer Result:")
    print(f"   Data transferred: {result.get('data_transferred', False)}")
    print(f"   Rows transferred: {result.get('rows_transferred', 0)}")
    
    if result.get('errors'):
        print(f"   Errors:")
        for error in result.get('errors', []):
            print(f"      - {error[:200]}")
    else:
        print(f"   ✅ Transfer successful!")
        
except Exception as e:
    print(f"   [ERROR] Transfer failed: {e}")
    import traceback
    traceback.print_exc()

# Step 4: Verify
print("\n4. Verifying data...")
try:
    mssql_conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER=72.61.233.209,1433;"
        f"DATABASE=cdctest;"
        f"UID=sa;"
        f"PWD=Sql@12345;"
        f"TrustServerCertificate=yes;"
        f"Encrypt=no;"
    )
    mssql_cur = mssql_conn.cursor()
    mssql_cur.execute("SELECT COUNT(*) FROM dbo.projects_simple;")
    count = mssql_cur.fetchone()[0]
    print(f"   SQL Server rows: {count}")
    
    if count > 0:
        print(f"   ✅ Data verified!")
    else:
        print(f"   ⚠️  No data found")
    
    mssql_cur.close()
    mssql_conn.close()
except Exception as e:
    print(f"   [ERROR] Verification failed: {e}")

print("\n" + "=" * 80)
print("Fix and Retry Complete!")
print("=" * 80)

