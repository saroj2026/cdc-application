"""Check if projects_simple table exists in PostgreSQL."""

import psycopg2

try:
    conn = psycopg2.connect(
        host="72.61.233.209",
        port=5432,
        user="cdc_user",
        password="cdc_pass",
        database="cdctest"
    )
    
    cur = conn.cursor()
    
    # Check if table exists
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'projects_simple';
    """)
    
    table = cur.fetchone()
    if table:
        print(f"✅ Table 'public.projects_simple' exists")
        
        # Get column info
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' 
            AND table_name = 'projects_simple'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        print(f"\nColumns ({len(columns)}):")
        for col in columns:
            print(f"  - {col[0]} ({col[1]}, nullable: {col[2]})")
        
        # Get row count
        cur.execute("SELECT COUNT(*) FROM public.projects_simple;")
        count = cur.fetchone()[0]
        print(f"\nRow count: {count}")
    else:
        print("❌ Table 'public.projects_simple' does not exist")
        print("\nAvailable tables in public schema:")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        for t in tables:
            print(f"  - {t[0]}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")


import psycopg2

try:
    conn = psycopg2.connect(
        host="72.61.233.209",
        port=5432,
        user="cdc_user",
        password="cdc_pass",
        database="cdctest"
    )
    
    cur = conn.cursor()
    
    # Check if table exists
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'projects_simple';
    """)
    
    table = cur.fetchone()
    if table:
        print(f"✅ Table 'public.projects_simple' exists")
        
        # Get column info
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' 
            AND table_name = 'projects_simple'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        print(f"\nColumns ({len(columns)}):")
        for col in columns:
            print(f"  - {col[0]} ({col[1]}, nullable: {col[2]})")
        
        # Get row count
        cur.execute("SELECT COUNT(*) FROM public.projects_simple;")
        count = cur.fetchone()[0]
        print(f"\nRow count: {count}")
    else:
        print("❌ Table 'public.projects_simple' does not exist")
        print("\nAvailable tables in public schema:")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        for t in tables:
            print(f"  - {t[0]}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")

