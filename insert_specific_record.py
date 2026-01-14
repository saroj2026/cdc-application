"""Insert a specific test record with project_id 8098402454."""

import psycopg2
import time
from datetime import date

DB_CONFIG = {
    "host": "72.61.233.209",
    "port": 5432,
    "database": "cdctest",
    "user": "cdc_user",
    "password": "cdc_pass"
}

PROJECT_ID = 8098402454

print("=" * 70)
print(f"Inserting Test Record with Project ID: {PROJECT_ID}")
print("=" * 70)

try:
    # Connect to PostgreSQL
    print("\n1. Connecting to PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("   ✅ Connected")
    
    # Get table structure
    print("\n2. Getting table structure...")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'projects_simple'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    column_names = [col[0] for col in columns]
    print(f"   Table columns: {', '.join(column_names)}")
    
    # Insert a new record
    print(f"\n3. Inserting new record with project_id = {PROJECT_ID}...")
    
    # Check if record exists
    cursor.execute("SELECT project_id FROM projects_simple WHERE project_id = %s", (PROJECT_ID,))
    existing = cursor.fetchone()
    
    if existing:
        # Update existing record
        print(f"   Record with project_id {PROJECT_ID} already exists, updating it...")
        cursor.execute("""
            UPDATE projects_simple 
            SET project_name = %s,
                department_id = %s,
                employee_id = %s,
                start_date = %s,
                status = %s
            WHERE project_id = %s
        """, (
            f"CDC Test Project {PROJECT_ID}",
            200,
            101,
            date(2024, 1, 15),
            f"UPDATED_{int(time.time())}",
            PROJECT_ID
        ))
        print(f"   ✅ Updated existing record")
    else:
        # Insert new record
        print(f"   Inserting new record...")
        cursor.execute("""
            INSERT INTO projects_simple 
            (project_id, project_name, department_id, employee_id, start_date, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            PROJECT_ID,
            f"CDC Test Project {PROJECT_ID}",
            200,
            101,
            date(2024, 1, 15),
            f"INSERTED_{int(time.time())}"
        ))
        print(f"   ✅ Inserted new record")
    
    conn.commit()
    
    # Verify the record
    print("\n4. Verifying inserted record...")
    cursor.execute("""
        SELECT project_id, project_name, department_id, employee_id, start_date, status
        FROM projects_simple 
        WHERE project_id = %s
    """, (PROJECT_ID,))
    
    record = cursor.fetchone()
    if record:
        print(f"   ✅ Record verified:")
        print(f"      Project ID: {record[0]}")
        print(f"      Project Name: {record[1]}")
        print(f"      Department ID: {record[2]}")
        print(f"      Employee ID: {record[3]}")
        print(f"      Start Date: {record[4]}")
        print(f"      Status: {record[5]}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 70)
    print("✅ Record inserted/updated successfully!")
    print("=" * 70)
    print(f"\nThe record with project_id {PROJECT_ID} has been inserted/updated in PostgreSQL.")
    print("This should trigger CDC and the record should appear in Snowflake within 30-60 seconds.")
    print("\nTo verify in Snowflake, run:")
    print("  python verify_snowflake_record_content.py")
    print(f"\nOr query Snowflake directly:")
    print(f"  SELECT * FROM projects_simple WHERE RECORD_CONTENT:project_id = {PROJECT_ID}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

