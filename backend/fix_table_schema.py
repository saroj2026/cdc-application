"""Fix SQL Server table schema to match PostgreSQL."""

import pyodbc
import psycopg2

print("=" * 80)
print("Fixing SQL Server Table Schema")
print("=" * 80)

# Get schema from PostgreSQL
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
        print(f"      {col[0]}: {col[1]} ({col[2] if col[2] else 'N/A'})")
    
    pg_cur.close()
    pg_conn.close()
    
except Exception as e:
    print(f"   [ERROR] Failed to get PostgreSQL schema: {e}")
    exit(1)

# Drop and recreate table in SQL Server
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
    
    # Drop table if exists
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
                sql_type = 'VARCHAR(MAX)'  # Use MAX for unlimited length
        elif col_type == 'date':
            sql_type = 'DATE'
        elif col_type == 'text':
            sql_type = 'TEXT'
        elif col_type == 'timestamp without time zone':
            sql_type = 'DATETIME2'
        else:
            sql_type = 'VARCHAR(MAX)'
        
        null_str = 'NULL' if is_nullable else 'NOT NULL'
        col_defs.append(f"{col_name} {sql_type} {null_str}")
    
    create_sql += ", ".join(col_defs) + ");"
    print(f"   SQL: {create_sql[:200]}...")
    
    mssql_cur.execute(create_sql)
    mssql_conn.commit()
    print("   [OK] Table created with correct schema")
    
    mssql_cur.close()
    mssql_conn.close()
    
except Exception as e:
    print(f"   [ERROR] Failed to recreate table: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("Table Schema Fixed!")
print("=" * 80)
print("\nNow run the full load again: python manual_full_load.py")


import pyodbc
import psycopg2

print("=" * 80)
print("Fixing SQL Server Table Schema")
print("=" * 80)

# Get schema from PostgreSQL
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
        print(f"      {col[0]}: {col[1]} ({col[2] if col[2] else 'N/A'})")
    
    pg_cur.close()
    pg_conn.close()
    
except Exception as e:
    print(f"   [ERROR] Failed to get PostgreSQL schema: {e}")
    exit(1)

# Drop and recreate table in SQL Server
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
    
    # Drop table if exists
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
                sql_type = 'VARCHAR(MAX)'  # Use MAX for unlimited length
        elif col_type == 'date':
            sql_type = 'DATE'
        elif col_type == 'text':
            sql_type = 'TEXT'
        elif col_type == 'timestamp without time zone':
            sql_type = 'DATETIME2'
        else:
            sql_type = 'VARCHAR(MAX)'
        
        null_str = 'NULL' if is_nullable else 'NOT NULL'
        col_defs.append(f"{col_name} {sql_type} {null_str}")
    
    create_sql += ", ".join(col_defs) + ");"
    print(f"   SQL: {create_sql[:200]}...")
    
    mssql_cur.execute(create_sql)
    mssql_conn.commit()
    print("   [OK] Table created with correct schema")
    
    mssql_cur.close()
    mssql_conn.close()
    
except Exception as e:
    print(f"   [ERROR] Failed to recreate table: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("Table Schema Fixed!")
print("=" * 80)
print("\nNow run the full load again: python manual_full_load.py")

