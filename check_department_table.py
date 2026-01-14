"""Check department table in PostgreSQL."""

import psycopg2
from psycopg2.extras import RealDictCursor

PG_CONFIG = {
    "host": "72.61.233.209",
    "port": 5432,
    "database": "cdctest",
    "user": "cdc_user",
    "password": "cdc_pass"
}

print("=" * 60)
print("Department Table Check")
print("=" * 60)

try:
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print(f"\nConnected to PostgreSQL: {PG_CONFIG['database']}\n")
    
    # Check if table exists and get row count
    cursor.execute("SELECT COUNT(*) as count FROM department")
    result = cursor.fetchone()
    count = result['count'] if result else 0
    
    print(f"✅ Department table: {count} rows")
    
    if count > 0:
        # Show sample data
        cursor.execute("SELECT * FROM department LIMIT 5")
        samples = cursor.fetchall()
        print(f"\nSample data (first {len(samples)} rows):")
        for i, row in enumerate(samples, 1):
            print(f"  Row {i}: {dict(row)}")
        
        # Get column info
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name = 'department'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        print(f"\nColumns ({len(columns)}):")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']}")
    else:
        print("  ⚠️  Table is empty")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")

