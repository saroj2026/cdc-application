"""Fix PostgreSQL table REPLICA IDENTITY for CDC."""

import psycopg2

print("=" * 80)
print("Fixing PostgreSQL REPLICA IDENTITY for CDC")
print("=" * 80)

try:
    conn = psycopg2.connect(
        host="72.61.233.209",
        port=5432,
        user="cdc_user",
        password="cdc_pass",
        database="cdctest"
    )
    cur = conn.cursor()
    
    # Check current REPLICA IDENTITY
    print("\n1. Checking current REPLICA IDENTITY...")
    cur.execute("""
        SELECT relreplident 
        FROM pg_class 
        WHERE relname = 'projects_simple';
    """)
    current_identity = cur.fetchone()
    print(f"   Current: {current_identity}")
    
    # Check if table has primary key
    print("\n2. Checking for primary key...")
    cur.execute("""
        SELECT a.attname
        FROM pg_index i
        JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
        WHERE i.indrelid = 'public.projects_simple'::regclass
        AND i.indisprimary;
    """)
    pk = cur.fetchone()
    
    if pk:
        print(f"   [OK] Primary key found: {pk[0]}")
        print("\n3. Setting REPLICA IDENTITY to FULL (for UPDATE/DELETE support)...")
        cur.execute("ALTER TABLE public.projects_simple REPLICA IDENTITY FULL;")
        conn.commit()
        print("   [OK] REPLICA IDENTITY set to FULL")
    else:
        print("   [WARNING] No primary key found")
        print("   Setting REPLICA IDENTITY to FULL (works without PK)...")
        cur.execute("ALTER TABLE public.projects_simple REPLICA IDENTITY FULL;")
        conn.commit()
        print("   [OK] REPLICA IDENTITY set to FULL")
    
    # Verify
    print("\n4. Verifying REPLICA IDENTITY...")
    cur.execute("""
        SELECT relreplident 
        FROM pg_class 
        WHERE relname = 'projects_simple';
    """)
    new_identity = cur.fetchone()
    print(f"   New: {new_identity}")
    
    # relreplident values: 'd'=default, 'n'=nothing, 'f'=full, 'i'=index
    if new_identity[0] == 'f':
        print("   [OK] REPLICA IDENTITY is FULL - CDC will work for INSERT, UPDATE, and DELETE")
    else:
        print(f"   [WARNING] REPLICA IDENTITY is {new_identity[0]} - may need to be 'f' for full CDC")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ REPLICA IDENTITY configured!")
    print("=" * 80)
    print("\nNote: You may need to restart the Debezium connector for changes to take effect.")
    print("Or wait a moment and the connector will pick up the change automatically.")
    
except Exception as e:
    print(f"❌ Error: {e}")


import psycopg2

print("=" * 80)
print("Fixing PostgreSQL REPLICA IDENTITY for CDC")
print("=" * 80)

try:
    conn = psycopg2.connect(
        host="72.61.233.209",
        port=5432,
        user="cdc_user",
        password="cdc_pass",
        database="cdctest"
    )
    cur = conn.cursor()
    
    # Check current REPLICA IDENTITY
    print("\n1. Checking current REPLICA IDENTITY...")
    cur.execute("""
        SELECT relreplident 
        FROM pg_class 
        WHERE relname = 'projects_simple';
    """)
    current_identity = cur.fetchone()
    print(f"   Current: {current_identity}")
    
    # Check if table has primary key
    print("\n2. Checking for primary key...")
    cur.execute("""
        SELECT a.attname
        FROM pg_index i
        JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
        WHERE i.indrelid = 'public.projects_simple'::regclass
        AND i.indisprimary;
    """)
    pk = cur.fetchone()
    
    if pk:
        print(f"   [OK] Primary key found: {pk[0]}")
        print("\n3. Setting REPLICA IDENTITY to FULL (for UPDATE/DELETE support)...")
        cur.execute("ALTER TABLE public.projects_simple REPLICA IDENTITY FULL;")
        conn.commit()
        print("   [OK] REPLICA IDENTITY set to FULL")
    else:
        print("   [WARNING] No primary key found")
        print("   Setting REPLICA IDENTITY to FULL (works without PK)...")
        cur.execute("ALTER TABLE public.projects_simple REPLICA IDENTITY FULL;")
        conn.commit()
        print("   [OK] REPLICA IDENTITY set to FULL")
    
    # Verify
    print("\n4. Verifying REPLICA IDENTITY...")
    cur.execute("""
        SELECT relreplident 
        FROM pg_class 
        WHERE relname = 'projects_simple';
    """)
    new_identity = cur.fetchone()
    print(f"   New: {new_identity}")
    
    # relreplident values: 'd'=default, 'n'=nothing, 'f'=full, 'i'=index
    if new_identity[0] == 'f':
        print("   [OK] REPLICA IDENTITY is FULL - CDC will work for INSERT, UPDATE, and DELETE")
    else:
        print(f"   [WARNING] REPLICA IDENTITY is {new_identity[0]} - may need to be 'f' for full CDC")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ REPLICA IDENTITY configured!")
    print("=" * 80)
    print("\nNote: You may need to restart the Debezium connector for changes to take effect.")
    print("Or wait a moment and the connector will pick up the change automatically.")
    
except Exception as e:
    print(f"❌ Error: {e}")

