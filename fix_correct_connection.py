"""Fix the correct SQL Server connection used by final_test pipeline."""

import psycopg2
import json

print("=" * 80)
print("Fixing Correct SQL Server Connection")
print("=" * 80)

target_conn_id = "b875c98a-0aed-40a6-88be-e1213efcf0b4"  # MS-SQL connection ID from pipeline

try:
    conn = psycopg2.connect(
        host="72.61.233.209",
        port=5432,
        user="cdc_user",
        password="cdc_pass",
        database="cdctest"
    )
    cur = conn.cursor()
    
    # Get current connection
    print(f"\n1. Getting connection: {target_conn_id}...")
    cur.execute("""
        SELECT id, name, database_type, additional_config
        FROM connections 
        WHERE id = %s;
    """, (target_conn_id,))
    
    row = cur.fetchone()
    if row:
        print(f"   [OK] Found: {row[1]} ({row[2]})")
        print(f"   Current additional_config: {row[3]}")
        
        # Update additional_config
        additional_config = row[3] or {}
        additional_config['trust_server_certificate'] = True
        additional_config['encrypt'] = False
        
        print(f"\n2. Updating connection...")
        cur.execute("""
            UPDATE connections 
            SET additional_config = %s
            WHERE id = %s;
        """, (json.dumps(additional_config), target_conn_id))
        
        conn.commit()
        print(f"   [OK] Updated additional_config:")
        print(f"      trust_server_certificate: {additional_config.get('trust_server_certificate')}")
        print(f"      encrypt: {additional_config.get('encrypt')}")
        
        # Verify
        cur.execute("""
            SELECT additional_config
            FROM connections 
            WHERE id = %s;
        """, (target_conn_id,))
        
        updated = cur.fetchone()
        print(f"\n3. Verifying update...")
        print(f"   Updated config: {updated[0]}")
        
    else:
        print(f"   [ERROR] Connection not found")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"   [ERROR] Exception: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("Connection Fixed!")
print("=" * 80)


import psycopg2
import json

print("=" * 80)
print("Fixing Correct SQL Server Connection")
print("=" * 80)

target_conn_id = "b875c98a-0aed-40a6-88be-e1213efcf0b4"  # MS-SQL connection ID from pipeline

try:
    conn = psycopg2.connect(
        host="72.61.233.209",
        port=5432,
        user="cdc_user",
        password="cdc_pass",
        database="cdctest"
    )
    cur = conn.cursor()
    
    # Get current connection
    print(f"\n1. Getting connection: {target_conn_id}...")
    cur.execute("""
        SELECT id, name, database_type, additional_config
        FROM connections 
        WHERE id = %s;
    """, (target_conn_id,))
    
    row = cur.fetchone()
    if row:
        print(f"   [OK] Found: {row[1]} ({row[2]})")
        print(f"   Current additional_config: {row[3]}")
        
        # Update additional_config
        additional_config = row[3] or {}
        additional_config['trust_server_certificate'] = True
        additional_config['encrypt'] = False
        
        print(f"\n2. Updating connection...")
        cur.execute("""
            UPDATE connections 
            SET additional_config = %s
            WHERE id = %s;
        """, (json.dumps(additional_config), target_conn_id))
        
        conn.commit()
        print(f"   [OK] Updated additional_config:")
        print(f"      trust_server_certificate: {additional_config.get('trust_server_certificate')}")
        print(f"      encrypt: {additional_config.get('encrypt')}")
        
        # Verify
        cur.execute("""
            SELECT additional_config
            FROM connections 
            WHERE id = %s;
        """, (target_conn_id,))
        
        updated = cur.fetchone()
        print(f"\n3. Verifying update...")
        print(f"   Updated config: {updated[0]}")
        
    else:
        print(f"   [ERROR] Connection not found")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"   [ERROR] Exception: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("Connection Fixed!")
print("=" * 80)

