"""Add Oracle to database_type enum in PostgreSQL database."""

import psycopg2
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Database connection - using the same as backend
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "72.61.233.209"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "cdctest"),
    "user": os.getenv("DB_USER", "cdc_user"),
    "password": os.getenv("DB_PASSWORD", "cdc_pass")
}

print("=" * 70)
print("Adding Oracle to database_type enum")
print("=" * 70)

try:
    print(f"\nConnecting to database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Check if 'oracle' already exists in enum
    print("\n1. Checking if 'oracle' exists in enum...")
    cursor.execute("""
        SELECT enumlabel 
        FROM pg_enum 
        WHERE enumtypid = (
            SELECT oid FROM pg_type WHERE typname = 'databasetype'
        ) AND enumlabel = 'oracle'
    """)
    
    if cursor.fetchone():
        print("   ✅ 'oracle' already exists in enum")
    else:
        print("   ⚠️  'oracle' not found, adding it...")
        
        # Add 'oracle' to enum
        try:
            cursor.execute("ALTER TYPE databasetype ADD VALUE IF NOT EXISTS 'oracle'")
            print("   ✅ 'oracle' added to enum successfully")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("   ✅ 'oracle' already exists in enum")
            else:
                print(f"   ⚠️  Error: {e}")
                # Try alternative method
                try:
                    cursor.execute("ALTER TYPE databasetype ADD VALUE 'oracle'")
                    print("   ✅ 'oracle' added using alternative method")
                except Exception as e2:
                    print(f"   ❌ Failed to add 'oracle': {e2}")
                    raise
    
    # Verify
    print("\n2. Verifying enum values...")
    cursor.execute("""
        SELECT enumlabel 
        FROM pg_enum 
        WHERE enumtypid = (
            SELECT oid FROM pg_type WHERE typname = 'databasetype'
        )
        ORDER BY enumsortorder
    """)
    enum_values = [row[0] for row in cursor.fetchall()]
    print(f"   Current enum values: {', '.join(enum_values)}")
    
    if 'oracle' in enum_values:
        print("   ✅ Oracle is in the enum!")
    else:
        print("   ❌ Oracle is NOT in the enum")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 70)
    print("✅ Complete!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

