"""Check available PostgreSQL databases."""

import psycopg2

try:
    # Connect to PostgreSQL server (not a specific database)
    conn = psycopg2.connect(
        host="72.61.233.209",
        port=5432,
        user="cdc_user",
        password="cdc_pass",
        database="postgres"  # Connect to default postgres database
    )
    
    cur = conn.cursor()
    cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname;")
    databases = cur.fetchall()
    
    print("Available PostgreSQL databases:")
    for db in databases:
        print(f"  - {db[0]}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")


import psycopg2

try:
    # Connect to PostgreSQL server (not a specific database)
    conn = psycopg2.connect(
        host="72.61.233.209",
        port=5432,
        user="cdc_user",
        password="cdc_pass",
        database="postgres"  # Connect to default postgres database
    )
    
    cur = conn.cursor()
    cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname;")
    databases = cur.fetchall()
    
    print("Available PostgreSQL databases:")
    for db in databases:
        print(f"  - {db[0]}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")

