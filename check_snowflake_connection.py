"""Check snowflake-s connection details in the database."""
import psycopg2
import json

try:
    conn = psycopg2.connect(
        host='72.61.233.209',
        port=5432,
        database='cdctest',
        user='cdc_user',
        password='cdc_pass'
    )
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, name, database_type, host, port, database, username, schema, additional_config, last_test_status
        FROM public.connections 
        WHERE name='snowflake-s' AND deleted_at IS NULL
    """)
    
    row = cur.fetchone()
    
    if not row:
        print("❌ Connection 'snowflake-s' NOT FOUND")
    else:
        print("✅ Found 'snowflake-s' connection:")
        print(f"  ID: {row[0]}")
        print(f"  Name: {row[1]}")
        print(f"  Database Type: {row[2]}")
        print(f"  Host: {row[3]}")
        print(f"  Port: {row[4]}")
        print(f"  Database: {row[5]}")
        print(f"  Username: {row[6]}")
        print(f"  Schema: {row[7]}")
        print(f"  Additional Config: {json.dumps(row[8], indent=2)}")
        print(f"  Last Test Status: {row[9]}")
        
        print("\n📋 Analysis:")
        print(f"  - Account (from host): {row[3]}")
        
        if row[8]:
            if 'account' in row[8]:
                print(f"  - Account (from additional_config): {row[8]['account']}")
            if 'warehouse' in row[8]:
                print(f"  - Warehouse: {row[8]['warehouse']}")
            else:
                print(f"  ⚠️  Warehouse: NOT SET (optional but recommended)")
            if 'role' in row[8]:
                print(f"  - Role: {row[8]['role']}")
            else:
                print(f"  ⚠️  Role: NOT SET (will use default)")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")


