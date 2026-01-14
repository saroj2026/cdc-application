"""Check Debezium replication slot status on PostgreSQL."""

import psycopg2

VM_PG_HOST = "72.61.241.193"
VM_PG_PORT = 5432
VM_PG_DATABASE = "openmetadata_db"
VM_PG_USER = "cdc_user"
VM_PG_PASSWORD = "cdc_password"

print("=" * 60)
print("Checking Debezium Replication Slot")
print("=" * 60)

try:
    conn = psycopg2.connect(
        host=VM_PG_HOST,
        port=VM_PG_PORT,
        database=VM_PG_DATABASE,
        user=VM_PG_USER,
        password=VM_PG_PASSWORD,
        connect_timeout=10
    )
    cursor = conn.cursor()
    
    # Check all replication slots
    print("\n1. All Replication Slots:")
    cursor.execute("""
        SELECT 
            slot_name,
            plugin,
            slot_type,
            active,
            restart_lsn,
            confirmed_flush_lsn
        FROM pg_replication_slots
        ORDER BY slot_name
    """)
    
    slots = cursor.fetchall()
    if slots:
        for slot in slots:
            slot_name, plugin, slot_type, active, restart_lsn, confirmed_flush_lsn = slot
            status = "ACTIVE" if active else "INACTIVE"
            print(f"   {slot_name}:")
            print(f"     Status: {status}")
            print(f"     Plugin: {plugin}")
            print(f"     Type: {slot_type}")
            print(f"     Restart LSN: {restart_lsn}")
            print(f"     Confirmed Flush LSN: {confirmed_flush_lsn}")
            print()
    else:
        print("   No replication slots found")
    
    # Check publications
    print("\n2. Publications:")
    cursor.execute("""
        SELECT pubname, puballtables, pubinsert, pubupdate, pubdelete, pubtruncate
        FROM pg_publication
        ORDER BY pubname
    """)
    
    pubs = cursor.fetchall()
    if pubs:
        for pub in pubs:
            pubname, puballtables, pubinsert, pubupdate, pubdelete, pubtruncate = pub
            print(f"   {pubname}:")
            print(f"     All Tables: {puballtables}")
            print(f"     Insert: {pubinsert}, Update: {pubupdate}, Delete: {pubdelete}, Truncate: {pubtruncate}")
            
            # Get tables in publication
            cursor.execute("""
                SELECT schemaname, tablename
                FROM pg_publication_tables
                WHERE pubname = %s
            """, (pubname,))
            tables = cursor.fetchall()
            if tables:
                print(f"     Tables: {', '.join([f'{s}.{t}' for s, t in tables])}")
            print()
    else:
        print("   No publications found")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()


