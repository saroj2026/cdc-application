"""Insert a test row using correct table structure."""

import psycopg2
import time

DB_CONFIG = {
    "host": "72.61.233.209",
    "port": 5432,
    "database": "cdctest",
    "user": "cdc_user",
    "password": "cdc_pass"
}

print("=" * 70)
print("Inserting Test Row to Trigger CDC")
print("=" * 70)

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Get table structure first
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'projects_simple'
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    col_names = [col[0] for col in columns]
    
    print(f"\nTable columns: {', '.join(col_names)}")
    
    # Update an existing row to trigger CDC
    cursor.execute("""
        UPDATE public.projects_simple 
        SET status = 'UPDATED_' || EXTRACT(EPOCH FROM NOW())::bigint::text
        WHERE project_id = (SELECT MAX(project_id) FROM public.projects_simple)
        RETURNING project_id, project_name
    """)
    updated = cursor.fetchone()
    if updated:
        conn.commit()
        print(f"\n✅ Updated row:")
        print(f"   Project ID: {updated[0]}")
        print(f"   Project Name: {updated[1]}")
        print(f"   This should trigger CDC and create the Kafka topic")
    else:
        # If no rows, insert a new one
        print("\n⚠️  No rows to update, inserting new row...")
        cursor.execute("""
            SELECT COALESCE(MAX(project_id), 0) FROM public.projects_simple
        """)
        max_id = cursor.fetchone()[0]
        new_id = max_id + 1
        
        cursor.execute("""
            INSERT INTO public.projects_simple (project_id, project_name, status) 
            VALUES (%s, %s, %s)
            RETURNING project_id
        """, (new_id, f'CDC_TEST_{new_id}', 'ACTIVE'))
        inserted = cursor.fetchone()
        conn.commit()
        print(f"✅ Inserted row with Project ID: {inserted[0]}")
    
    # Wait for CDC
    print(f"\nWaiting 3 seconds for Debezium to process...")
    time.sleep(3)
    
    cursor.close()
    conn.close()
    
    print(f"\n✅ Change applied! Check Kafka UI Topics page for 'ps_sn_p.public.projects_simple'")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)

