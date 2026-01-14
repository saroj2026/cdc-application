"""Check projects_simple table structure."""

import psycopg2

DB_CONFIG = {
    "host": "72.61.233.209",
    "port": 5432,
    "database": "cdctest",
    "user": "cdc_user",
    "password": "cdc_pass"
}

conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()

# Get table structure
cursor.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'projects_simple'
    ORDER BY ordinal_position
""")

columns = cursor.fetchall()
print("Table Structure:")
for col in columns:
    print(f"  {col[0]}: {col[1]} (nullable: {col[2]})")

# Get sample row
cursor.execute("SELECT * FROM public.projects_simple LIMIT 1")
sample = cursor.fetchone()
if sample:
    print(f"\nSample row: {sample}")

cursor.close()
conn.close()


