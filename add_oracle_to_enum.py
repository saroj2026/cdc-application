"""Add Oracle to database_type enum directly in database (if migration has issues)."""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5434)),
    "database": os.getenv("DB_NAME", "cdc_management"),
    "user": os.getenv("DB_USER", "cdc_user"),
    "password": os.getenv("DB_PASSWORD", "cdc_password")
}

print("=" * 70)
print("Adding Oracle to database_type enum")
print("=" * 70)

try:
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    cursor = conn.cursor()
    
    print("\n1. Checking current enum values...")
    cursor.execute("""
        SELECT unnest(enum_range(NULL::database_type))::text;
    """)
    current_values = [row[0] for row in cursor.fetchall()]
    print(f"   Current values: {', '.join(current_values)}")
    
    if 'oracle' in current_values:
        print("\n   ✅ Oracle already exists in enum!")
    else:
        print("\n2. Adding 'oracle' to database_type enum...")
        try:
            cursor.execute("ALTER TYPE database_type ADD VALUE IF NOT EXISTS 'oracle'")
            conn.commit()
            print("   ✅ Oracle added to enum successfully!")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("   ✅ Oracle already exists in enum")
                conn.rollback()
            else:
                raise
    
    # Verify
    print("\n3. Verifying enum values...")
    cursor.execute("""
        SELECT unnest(enum_range(NULL::database_type))::text;
    """)
    updated_values = [row[0] for row in cursor.fetchall()]
    print(f"   Updated values: {', '.join(updated_values)}")
    
    if 'oracle' in updated_values:
        print("\n   ✅ Oracle is now in the enum!")
    else:
        print("\n   ⚠️  Oracle not found in enum")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 70)
    print("✅ Complete!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

