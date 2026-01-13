"""Fix PostgreSQL replication slots issue."""

import psycopg2

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
    print("="*80)
    print("PostgreSQL Replication Slots Status")
    print("="*80)
    
    # Check current replication slots
    cur.execute("""
        SELECT slot_name, slot_type, active, database, 
               pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) as lag
        FROM pg_replication_slots
        ORDER BY slot_name
    """)
    
    slots = cur.fetchall()
    print(f"\nCurrent replication slots: {len(slots)}")
    print("\nSlot Details:")
    for slot in slots:
        slot_name, slot_type, active, database, lag = slot
        print(f"  - {slot_name}")
        print(f"    Type: {slot_type}, Active: {active}, Database: {database}, Lag: {lag}")
    
    # Check max_replication_slots setting
    cur.execute("SHOW max_replication_slots")
    max_slots = cur.fetchone()[0]
    print(f"\nMax replication slots: {max_slots}")
    
    # Check if we need to drop unused slots
    print("\n" + "="*80)
    print("Checking for inactive/unused slots...")
    print("="*80)
    
    inactive_slots = [s for s in slots if not s[2]]  # active = False
    
    if inactive_slots:
        print(f"\nFound {len(inactive_slots)} inactive slots:")
        for slot in inactive_slots:
            print(f"  - {slot[0]} (inactive)")
        
        print("\n⚠ Inactive slots found. These can be dropped to free up slots.")
        print("To drop a slot, run:")
        for slot in inactive_slots:
            print(f"  SELECT pg_drop_replication_slot('{slot[0]}');")
    else:
        print("No inactive slots found.")
    
    # Check for Debezium slots specifically
    debezium_slots = [s for s in slots if 'debezium' in s[0].lower() or 'cdc' in s[0].lower()]
    if debezium_slots:
        print(f"\nFound {len(debezium_slots)} Debezium-related slots:")
        for slot in debezium_slots:
            print(f"  - {slot[0]} (Active: {slot[2]})")
    
    # Show recommendation
    print("\n" + "="*80)
    print("Recommendations")
    print("="*80)
    
    if len(slots) >= int(max_slots):
        print("⚠ All replication slots are in use!")
        print("\nOptions:")
        print("1. Drop unused/inactive slots (recommended)")
        print("2. Increase max_replication_slots in postgresql.conf")
        print("   Then restart PostgreSQL")
        
        if inactive_slots:
            print("\nTo drop inactive slots, run:")
            for slot in inactive_slots:
                print(f"   SELECT pg_drop_replication_slot('{slot[0]}');")
    else:
        print(f"✓ You have {int(max_slots) - len(slots)} free slots available")
        print("  The issue might be with a specific slot. Check Debezium connector logs.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    cur.close()
    conn.close()

