"""Remove temporary and debugging files."""

import os

# Files to remove (temporary debugging and fix scripts)
files_to_remove = [
    # Fix scripts (temporary)
    "fix_debezium_streaming.py",
    "fix_sink_brackets.py",
    "fix_sink_config_complete.py",
    "fix_sink_schema_enable.py",
    "fix_sink_sqlserver_schema.py",
    "fix_sink_table_format.py",
    "fix_sqlserver_table_schema.py",
    "fix_table_name_final.py",
    
    # Test scripts (temporary)
    "test_cdc_pipeline.py",
    "test_insert_and_check.py",
    "test_realtime_cdc.py",
    "test_vm_postgres_connection.py",
    
    # Check scripts (keep only essential ones)
    "check_postgres_publication.py",
    "check_sqlserver_table_schema.py",
    
    # Temporary files
    "sink_config.json",
    "verify_and_fix.py",
    "insert_test_record.py",
    "drop_sqlserver_table.py",
    "recreate_sink_connector.py",
    
    # Old documentation
    "SYSTEM_STATUS.md",
    "INSTRUCTIONS_REALTIME_CDC.md",
    "DOCKER_POSTGRES_CDC_SETUP.md",
]

# Files to keep (essential)
files_to_keep = [
    "check_realtime_cdc.py",  # Useful for verification
    "check_replication.py",   # Useful for verification
    "check_debezium_slot.py", # Useful for diagnostics
    "add_table_to_publication.sql",  # Useful SQL script
]

print("=" * 60)
print("Cleaning Up Temporary Files")
print("=" * 60)

removed_count = 0
not_found = []

for file in files_to_remove:
    if os.path.exists(file):
        try:
            os.remove(file)
            print(f"✓ Removed: {file}")
            removed_count += 1
        except Exception as e:
            print(f"✗ Error removing {file}: {e}")
    else:
        not_found.append(file)

print(f"\n✓ Removed {removed_count} files")
if not_found:
    print(f"  ({len(not_found)} files not found - already removed)")

print("\n" + "=" * 60)
print("Cleanup complete!")
print("=" * 60)


