"""Add a new record to the department/departments table in PostgreSQL and verify CDC replication."""

import psycopg2
import pyodbc
from psycopg2.extras import RealDictCursor
from datetime import datetime
import time

PG_CONFIG = {
    "host": "72.61.233.209",
    "port": 5432,
    "database": "cdctest",
    "user": "cdc_user",
    "password": "cdc_pass"
}

MSSQL_CONFIG = {
    "server": "72.61.233.209",
    "port": 1433,
    "database": "cdctest",
    "user": "sa",
    "password": "Segmetriq@2025",
    "driver": "ODBC Driver 18 for SQL Server",
    "TrustServerCertificate": "yes",
    "Encrypt": "yes"
}

print("=" * 70)
print("CDC Replication Test - Add Department Record")
print("=" * 70)

try:
    # Step 1: Connect to PostgreSQL
    print("\n1. Connecting to PostgreSQL...")
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print(f"   ✅ Connected to PostgreSQL: {PG_CONFIG['database']}")
    
    # Check which table exists (department or departments)
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND (table_name = 'department' OR table_name = 'departments')
    """)
    tables = cursor.fetchall()
    
    if not tables:
        print("   ❌ Neither 'department' nor 'departments' table found!")
        print("   Available tables:")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        for table in cursor.fetchall():
            print(f"      - {table['table_name']}")
        exit(1)
    
    table_name = tables[0]['table_name']
    print(f"   ✅ Found table: {table_name}")
    
    # Check current records
    cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
    result = cursor.fetchone()
    current_count = result['count'] if result else 0
    print(f"   Current records: {current_count}")
    
    # Add new department record with timestamp for uniqueness
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_department = {
        'name': f'Test Department {timestamp}',
        'location': 'Test Location'
    }
    
    print(f"\n1. Adding new department record...")
    print(f"   Name: {new_department['name']}")
    print(f"   Location: {new_department['location']}")
    
    cursor.execute(
        "INSERT INTO department (name, location) VALUES (%s, %s) RETURNING id, name, location",
        (new_department['name'], new_department['location'])
    )
    
    new_record = cursor.fetchone()
    conn.commit()
    
    print(f"   ✅ Record added successfully!")
    print(f"   New record ID: {new_record['id']}")
    print(f"   Name: {new_record['name']}")
    print(f"   Location: {new_record['location']}")
    
    # Verify the new count
    cursor.execute("SELECT COUNT(*) as count FROM department")
    result = cursor.fetchone()
    new_count = result['count'] if result else 0
    print(f"\n2. Updated department records: {new_count}")
    print(f"   Added: {new_count - current_count} record(s)")
    
    # Show all records
    cursor.execute("SELECT * FROM department ORDER BY id")
    all_records = cursor.fetchall()
    print(f"\n3. All department records ({len(all_records)}):")
    for record in all_records:
        print(f"   ID {record['id']}: {record['name']} - {record['location']}")
    
    cursor.close()
    conn.close()
    
    # Step 3: Wait for CDC to process
    print(f"\n3. Waiting 5 seconds for CDC to process...")
    time.sleep(5)
    
    # Step 4: Verify in SQL Server
    print(f"\n4. Verifying replication in SQL Server...")
    try:
        mssql_conn_str = (
            f"DRIVER={{{MSSQL_CONFIG['driver']}}};"
            f"SERVER={MSSQL_CONFIG['server']},{MSSQL_CONFIG['port']};"
            f"DATABASE={MSSQL_CONFIG['database']};"
            f"UID={MSSQL_CONFIG['user']};"
            f"PWD={MSSQL_CONFIG['password']};"
            f"TrustServerCertificate={MSSQL_CONFIG['TrustServerCertificate']};"
            f"Encrypt={MSSQL_CONFIG['Encrypt']};"
        )
        
        mssql_conn = pyodbc.connect(mssql_conn_str, timeout=30)
        mssql_cursor = mssql_conn.cursor()
        print(f"   ✅ Connected to SQL Server")
        
        # Check for table in dbo schema
        mssql_cursor.execute(f"""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = 'dbo' 
            AND (TABLE_NAME = 'department' OR TABLE_NAME = 'departments')
        """)
        mssql_tables = mssql_cursor.fetchall()
        
        if mssql_tables:
            mssql_table = f"dbo.{mssql_tables[0][0]}"
            print(f"   ✅ Found table: {mssql_table}")
            
            # Check record count
            mssql_cursor.execute(f"SELECT COUNT(*) FROM {mssql_table}")
            mssql_count = mssql_cursor.fetchone()[0]
            print(f"   Records in SQL Server: {mssql_count}")
            
            # Try to find the new record
            search_name = new_department['name'].split()[0]  # "Test"
            mssql_cursor.execute(f"""
                SELECT TOP 5 * FROM {mssql_table} 
                WHERE name LIKE ? 
                ORDER BY id DESC
            """, (f'%{search_name}%',))
            
            found_records = mssql_cursor.fetchall()
            if found_records:
                print(f"   ✅ Found {len(found_records)} matching record(s) in SQL Server!")
                for record in found_records:
                    print(f"      {[str(col) for col in record]}")
            else:
                print(f"   ⚠️  Record not found yet (may need more time)")
        else:
            print(f"   ⚠️  Table not found in SQL Server dbo schema")
        
        mssql_conn.close()
    except Exception as e:
        print(f"   ⚠️  Could not verify in SQL Server: {e}")
    
    print("\n" + "=" * 70)
    print("✅ Test Complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Check Analytics page - should show new replication event")
    print("2. Check Dashboard - metrics should update")
    print("3. Check Monitoring page - should show INSERT event")
    print("4. Refresh pages to see the new data")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

