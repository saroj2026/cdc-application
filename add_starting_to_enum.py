"""Add STARTING to PipelineStatus enum if it doesn't exist."""

import psycopg2
import os

# Database connection
conn = psycopg2.connect(
    host="72.61.233.209",
    port=5432,
    database="cdctest",
    user="cdc_user",
    password="cdc_pass"
)

cur = conn.cursor()

try:
    # Check current enum values
    cur.execute("SELECT unnest(enum_range(NULL::pipelinestatus))")
    current_values = [r[0] for r in cur.fetchall()]
    print(f"Current PipelineStatus enum values: {current_values}")
    
    # Add STARTING if it doesn't exist
    if "STARTING" not in current_values:
        print("Adding 'STARTING' to PipelineStatus enum...")
        cur.execute("ALTER TYPE pipelinestatus ADD VALUE IF NOT EXISTS 'STARTING'")
        conn.commit()
        print("✓ Added 'STARTING' to PipelineStatus enum")
    else:
        print("'STARTING' already exists in PipelineStatus enum")
    
    # Check CDCStatus enum
    cur.execute("SELECT unnest(enum_range(NULL::cdcstatus))")
    cdc_values = [r[0] for r in cur.fetchall()]
    print(f"Current CDCStatus enum values: {cdc_values}")
    
    if "STARTING" not in cdc_values:
        print("Adding 'STARTING' to CDCStatus enum...")
        cur.execute("ALTER TYPE cdcstatus ADD VALUE IF NOT EXISTS 'STARTING'")
        conn.commit()
        print("✓ Added 'STARTING' to CDCStatus enum")
    else:
        print("'STARTING' already exists in CDCStatus enum")
        
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    cur.close()
    conn.close()

