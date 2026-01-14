"""Check if source PostgreSQL tables have data."""

import psycopg2
from psycopg2.extras import RealDictCursor

# PostgreSQL connection details
PG_CONFIG = {
    "host": "72.61.233.209",
    "port": 5432,
    "database": "cdctest",
    "user": "cdc_user",
    "password": "cdc_pass"
}

TABLES = [
    "alembic_version",
    "alert_history",
    "alert_rules",
    "audit_logs",
    "connection_tests"
]

print("=" * 60)
print("Source PostgreSQL Data Check")
print("=" * 60)

try:
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print(f"\nConnected to PostgreSQL: {PG_CONFIG['database']}\n")
    
    for table in TABLES:
        try:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            result = cursor.fetchone()
            count = result['count'] if result else 0
            
            if count > 0:
                print(f"✅ {table}: {count} rows")
                # Show sample data
                cursor.execute(f"SELECT * FROM {table} LIMIT 1")
                sample = cursor.fetchone()
                if sample:
                    print(f"   Sample keys: {list(sample.keys())[:5]}")
            else:
                print(f"⚠️  {table}: 0 rows (empty table)")
        except Exception as e:
            print(f"❌ {table}: Error - {e}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ Connection error: {e}")

