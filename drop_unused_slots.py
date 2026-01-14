"""Drop unused replication slots to free up space."""

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

# Slots to drop (keeping only the most recent ones if needed)
slots_to_drop = [
    'cdc_pipeline_69342174175733d321678743',
    'cdc_pipeline_6944026692fd18503e230dce',
    'cdc_slot_dept_full_load',
    'debezium',  # Old generic slot
    'final_test_slot',
    'new_cloud_slot',
    'new_pipeline_slot',
    'p_department_full_load_slot',
    'p_test5_slot',
    'sa_pipeline_2_slot'
]

print("="*80)
print("Dropping Unused Replication Slots")
print("="*80)

dropped_count = 0
failed_count = 0

for slot_name in slots_to_drop:
    try:
        print(f"\nDropping slot: {slot_name}...")
        cur.execute(f"SELECT pg_drop_replication_slot('{slot_name}')")
        conn.commit()
        print(f"  ✓ Dropped successfully")
        dropped_count += 1
    except psycopg2.Error as e:
        error_msg = str(e)
        if "does not exist" in error_msg:
            print(f"  - Slot doesn't exist (already dropped)")
        else:
            print(f"  ✗ Error: {error_msg}")
            failed_count += 1
        conn.rollback()

print("\n" + "="*80)
print("Summary")
print("="*80)
print(f"Successfully dropped: {dropped_count} slots")
print(f"Failed: {failed_count} slots")

# Check remaining slots
cur.execute("SELECT COUNT(*) FROM pg_replication_slots")
remaining = cur.fetchone()[0]
print(f"Remaining slots: {remaining}")

cur.close()
conn.close()

print("\n✓ Done! You can now restart the Debezium connector.")

