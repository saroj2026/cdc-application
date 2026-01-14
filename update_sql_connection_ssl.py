"""Update SQL Server connection to include trust_server_certificate."""

import psycopg2
import json

conn = psycopg2.connect(
    host="72.61.233.209",
    port=5432,
    database="cdctest",
    user="cdc_user",
    password="cdc_pass"
)

cur = conn.cursor()

try:
    # Update the SQL Server connection
    conn_id = "cf4850c2-6710-4971-bd59-a8fe5526ccdf"
    
    # Get current config
    cur.execute("SELECT additional_config FROM connections WHERE id = %s", (conn_id,))
    result = cur.fetchone()
    current_config = result[0] if result and result[0] else {}
    
    # Update config
    if not isinstance(current_config, dict):
        current_config = {}
    current_config["trust_server_certificate"] = True
    
    # Update database
    cur.execute(
        "UPDATE connections SET additional_config = %s WHERE id = %s",
        (json.dumps(current_config), conn_id)
    )
    conn.commit()
    print(f"✓ Updated SQL Server connection {conn_id} with trust_server_certificate=True")
    print(f"  Config: {json.dumps(current_config)}")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    cur.close()
    conn.close()

