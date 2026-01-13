"""Check if table exists and recreate if needed."""

import pyodbc
import psycopg2

print("=" * 80)
print("Checking and Fixing Table")
print("=" * 80)

# Check SQL Server
print("\n1. Checking SQL Server table...")
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
        count = cur.fetchone()[0]
        print(f"   [OK] Table exists with {count} rows")
    else:
        print(f"   [WARNING] Table does not exist, creating it...")
        
        # Get schema from PostgreSQL
        pg_conn = psycopg2.connect(
            host="72.61.233.209",
            port=5432,
            user="cdc_user",
            password="cdc_pass",
            database="cdctest"
        )
        pg_cur = pg_conn.cursor()
        
        pg_cur.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = 'public' 
            AND table_name = 'projects_simple'
            ORDER BY ordinal_position;
        """)
        columns = pg_cur.fetchall()
        
        # Create table in SQL Server
        create_sql = "CREATE TABLE dbo.projects_simple ("
        col_defs = []
        for col in columns:
            col_name = col[0]
            col_type = col[1]
            max_len = col[2]
            
            # Map PostgreSQL types to SQL Server types
            if col_type == 'integer':
                sql_type = 'INT'
            elif col_type == 'character varying' or col_type == 'varchar':
                sql_type = f'VARCHAR({max_len if max_len else 255})'
            elif col_type == 'date':
                sql_type = 'DATE'
            elif col_type == 'text':
                sql_type = 'TEXT'
            else:
                sql_type = 'VARCHAR(255)'
            
            col_defs.append(f"{col_name} {sql_type}")
        
        create_sql += ", ".join(col_defs) + ");"
        print(f"   Creating table with SQL: {create_sql[:200]}...")
        
        cur.execute(create_sql)
        conn.commit()
        print(f"   [OK] Table created")
        
        pg_cur.close()
        pg_conn.close()
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"   [ERROR] Exception: {e}")

print("\n" + "=" * 80)


import pyodbc
import psycopg2

print("=" * 80)
print("Checking and Fixing Table")
print("=" * 80)

# Check SQL Server
print("\n1. Checking SQL Server table...")
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
        count = cur.fetchone()[0]
        print(f"   [OK] Table exists with {count} rows")
    else:
        print(f"   [WARNING] Table does not exist, creating it...")
        
        # Get schema from PostgreSQL
        pg_conn = psycopg2.connect(
            host="72.61.233.209",
            port=5432,
            user="cdc_user",
            password="cdc_pass",
            database="cdctest"
        )
        pg_cur = pg_conn.cursor()
        
        pg_cur.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = 'public' 
            AND table_name = 'projects_simple'
            ORDER BY ordinal_position;
        """)
        columns = pg_cur.fetchall()
        
        # Create table in SQL Server
        create_sql = "CREATE TABLE dbo.projects_simple ("
        col_defs = []
        for col in columns:
            col_name = col[0]
            col_type = col[1]
            max_len = col[2]
            
            # Map PostgreSQL types to SQL Server types
            if col_type == 'integer':
                sql_type = 'INT'
            elif col_type == 'character varying' or col_type == 'varchar':
                sql_type = f'VARCHAR({max_len if max_len else 255})'
            elif col_type == 'date':
                sql_type = 'DATE'
            elif col_type == 'text':
                sql_type = 'TEXT'
            else:
                sql_type = 'VARCHAR(255)'
            
            col_defs.append(f"{col_name} {sql_type}")
        
        create_sql += ", ".join(col_defs) + ");"
        print(f"   Creating table with SQL: {create_sql[:200]}...")
        
        cur.execute(create_sql)
        conn.commit()
        print(f"   [OK] Table created")
        
        pg_cur.close()
        pg_conn.close()
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"   [ERROR] Exception: {e}")

print("\n" + "=" * 80)

