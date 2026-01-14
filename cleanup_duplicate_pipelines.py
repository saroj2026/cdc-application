"""Clean up duplicate pipelines - keeps the newest or most active one."""

import requests
from collections import defaultdict
import sys

API_URL = "http://localhost:8000/api"

print("=" * 80)
print("Cleanup Duplicate Pipelines")
print("=" * 80)

# Get all pipelines
print("\n1. Fetching all pipelines...")
response = requests.get(f"{API_URL}/pipelines", timeout=10)
if response.status_code != 200:
    print(f"   [ERROR] Failed to get pipelines: {response.status_code}")
    exit(1)

pipelines = response.json()
print(f"   [OK] Found {len(pipelines)} pipeline(s)\n")

# Group by name (case-insensitive)
name_groups = defaultdict(list)
for pipeline in pipelines:
    name = pipeline.get('name', '').strip().lower()
    name_groups[name].append(pipeline)

# Group by configuration (source, target, tables, mode)
config_groups = defaultdict(list)
for pipeline in pipelines:
    config_key = (
        pipeline.get('source_connection_id', ''),
        pipeline.get('target_connection_id', ''),
        tuple(sorted(pipeline.get('source_tables', []))),
        pipeline.get('mode', '')
    )
    config_groups[config_key].append(pipeline)

# Find duplicates by name
name_duplicates = {name: plist for name, plist in name_groups.items() if len(plist) > 1}

# Find duplicates by configuration
config_duplicates = {k: v for k, v in config_groups.items() if len(v) > 1}

# Combine both types
all_duplicate_groups = {}
for name, plist in name_duplicates.items():
    all_duplicate_groups[f"name:{name}"] = plist
for config, plist in config_duplicates.items():
    # Only add if not already covered by name duplicates
    config_str = f"config:{config[3]}:{','.join(config[2])}"
    if config_str not in all_duplicate_groups:
        all_duplicate_groups[config_str] = plist

duplicates = all_duplicate_groups

if not duplicates:
    print("=" * 80)
    print("No duplicate pipelines found!")
    print("=" * 80)
    exit(0)

print("=" * 80)
print(f"Found {len(duplicates)} duplicate group(s)")
print(f"  - Name duplicates: {len(name_duplicates)}")
print(f"  - Config duplicates: {len(config_duplicates)}")
print("=" * 80)

# Determine which pipelines to delete
pipelines_to_delete = []
pipelines_to_keep = []

for name, plist in duplicates.items():
    # Sort by priority:
    # 1. Running pipelines
    # 2. Pipelines with progress (full load or CDC started)
    # 3. Newest created
    def sort_key(p):
        status = p.get('status', '')
        full_load = p.get('full_load_status', 'NOT_STARTED')
        cdc = p.get('cdc_status', 'NOT_STARTED')
        created = p.get('created_at', '')
        
        # Priority score (higher = keep)
        priority = 0
        if status == "RUNNING":
            priority += 1000
        if full_load != "NOT_STARTED":
            priority += 100
        if cdc != "NOT_STARTED":
            priority += 100
        # Newer = higher priority (if created_at is sortable)
        
        return (-priority, created)  # Negative for descending
    
    sorted_pipelines = sorted(plist, key=sort_key, reverse=True)
    
    # Keep the first one (highest priority)
    keep = sorted_pipelines[0]
    pipelines_to_keep.append(keep)
    
    # Delete the rest
    for p in sorted_pipelines[1:]:
        pipelines_to_delete.append(p)

# Display what will be deleted
print("\n" + "=" * 80)
print("Pipelines to KEEP:")
print("=" * 80)
for pipeline in pipelines_to_keep:
    print(f"  - {pipeline.get('name')} (ID: {pipeline.get('id')})")
    print(f"    Status: {pipeline.get('status')}, Created: {pipeline.get('created_at', 'N/A')}")

print("\n" + "=" * 80)
print("Pipelines to DELETE:")
print("=" * 80)
for pipeline in pipelines_to_delete:
    print(f"  - {pipeline.get('name')} (ID: {pipeline.get('id')})")
    print(f"    Status: {pipeline.get('status')}, Created: {pipeline.get('created_at', 'N/A')}")

# Confirm deletion
print("\n" + "=" * 80)
print(f"Summary: {len(pipelines_to_keep)} to keep, {len(pipelines_to_delete)} to delete")
print("=" * 80)

if not pipelines_to_delete:
    print("\nNo pipelines to delete!")
    exit(0)

# Check if we should proceed
print("\n⚠️  WARNING: This will DELETE the pipelines listed above!")
response = input("\nDo you want to proceed? (yes/no): ").strip().lower()

if response not in ['yes', 'y']:
    print("\nCleanup cancelled.")
    exit(0)

# Delete pipelines
print("\n" + "=" * 80)
print("Deleting pipelines...")
print("=" * 80)

deleted_count = 0
failed_count = 0

for pipeline in pipelines_to_delete:
    pipeline_id = pipeline.get('id')
    pipeline_name = pipeline.get('name')
    
    try:
        # Try to delete via API (soft delete by default)
        delete_response = requests.delete(f"{API_URL}/pipelines/{pipeline_id}?hard_delete=true", timeout=10)
        
        if delete_response.status_code in [200, 204]:
            print(f"   [OK] Deleted: {pipeline_name} ({pipeline_id})")
            deleted_count += 1
        elif delete_response.status_code == 404:
            print(f"   [INFO] Already deleted: {pipeline_name} ({pipeline_id})")
            deleted_count += 1
        else:
            print(f"   [ERROR] Failed to delete {pipeline_name}: {delete_response.status_code}")
            print(f"          Response: {delete_response.text[:200]}")
            failed_count += 1
    except Exception as e:
        print(f"   [ERROR] Exception deleting {pipeline_name}: {e}")
        failed_count += 1

print("\n" + "=" * 80)
print("Cleanup Complete!")
print("=" * 80)
print(f"Deleted: {deleted_count}")
print(f"Failed: {failed_count}")
print(f"Kept: {len(pipelines_to_keep)}")

if failed_count > 0:
    print("\n⚠️  Some pipelines could not be deleted. They may need to be deleted manually.")
    print("   Check the errors above for details.")


import requests
from collections import defaultdict
import sys

API_URL = "http://localhost:8000/api"

print("=" * 80)
print("Cleanup Duplicate Pipelines")
print("=" * 80)

# Get all pipelines
print("\n1. Fetching all pipelines...")
response = requests.get(f"{API_URL}/pipelines", timeout=10)
if response.status_code != 200:
    print(f"   [ERROR] Failed to get pipelines: {response.status_code}")
    exit(1)

pipelines = response.json()
print(f"   [OK] Found {len(pipelines)} pipeline(s)\n")

# Group by name (case-insensitive)
name_groups = defaultdict(list)
for pipeline in pipelines:
    name = pipeline.get('name', '').strip().lower()
    name_groups[name].append(pipeline)

# Group by configuration (source, target, tables, mode)
config_groups = defaultdict(list)
for pipeline in pipelines:
    config_key = (
        pipeline.get('source_connection_id', ''),
        pipeline.get('target_connection_id', ''),
        tuple(sorted(pipeline.get('source_tables', []))),
        pipeline.get('mode', '')
    )
    config_groups[config_key].append(pipeline)

# Find duplicates by name
name_duplicates = {name: plist for name, plist in name_groups.items() if len(plist) > 1}

# Find duplicates by configuration
config_duplicates = {k: v for k, v in config_groups.items() if len(v) > 1}

# Combine both types
all_duplicate_groups = {}
for name, plist in name_duplicates.items():
    all_duplicate_groups[f"name:{name}"] = plist
for config, plist in config_duplicates.items():
    # Only add if not already covered by name duplicates
    config_str = f"config:{config[3]}:{','.join(config[2])}"
    if config_str not in all_duplicate_groups:
        all_duplicate_groups[config_str] = plist

duplicates = all_duplicate_groups

if not duplicates:
    print("=" * 80)
    print("No duplicate pipelines found!")
    print("=" * 80)
    exit(0)

print("=" * 80)
print(f"Found {len(duplicates)} duplicate group(s)")
print(f"  - Name duplicates: {len(name_duplicates)}")
print(f"  - Config duplicates: {len(config_duplicates)}")
print("=" * 80)

# Determine which pipelines to delete
pipelines_to_delete = []
pipelines_to_keep = []

for name, plist in duplicates.items():
    # Sort by priority:
    # 1. Running pipelines
    # 2. Pipelines with progress (full load or CDC started)
    # 3. Newest created
    def sort_key(p):
        status = p.get('status', '')
        full_load = p.get('full_load_status', 'NOT_STARTED')
        cdc = p.get('cdc_status', 'NOT_STARTED')
        created = p.get('created_at', '')
        
        # Priority score (higher = keep)
        priority = 0
        if status == "RUNNING":
            priority += 1000
        if full_load != "NOT_STARTED":
            priority += 100
        if cdc != "NOT_STARTED":
            priority += 100
        # Newer = higher priority (if created_at is sortable)
        
        return (-priority, created)  # Negative for descending
    
    sorted_pipelines = sorted(plist, key=sort_key, reverse=True)
    
    # Keep the first one (highest priority)
    keep = sorted_pipelines[0]
    pipelines_to_keep.append(keep)
    
    # Delete the rest
    for p in sorted_pipelines[1:]:
        pipelines_to_delete.append(p)

# Display what will be deleted
print("\n" + "=" * 80)
print("Pipelines to KEEP:")
print("=" * 80)
for pipeline in pipelines_to_keep:
    print(f"  - {pipeline.get('name')} (ID: {pipeline.get('id')})")
    print(f"    Status: {pipeline.get('status')}, Created: {pipeline.get('created_at', 'N/A')}")

print("\n" + "=" * 80)
print("Pipelines to DELETE:")
print("=" * 80)
for pipeline in pipelines_to_delete:
    print(f"  - {pipeline.get('name')} (ID: {pipeline.get('id')})")
    print(f"    Status: {pipeline.get('status')}, Created: {pipeline.get('created_at', 'N/A')}")

# Confirm deletion
print("\n" + "=" * 80)
print(f"Summary: {len(pipelines_to_keep)} to keep, {len(pipelines_to_delete)} to delete")
print("=" * 80)

if not pipelines_to_delete:
    print("\nNo pipelines to delete!")
    exit(0)

# Check if we should proceed
print("\n⚠️  WARNING: This will DELETE the pipelines listed above!")
response = input("\nDo you want to proceed? (yes/no): ").strip().lower()

if response not in ['yes', 'y']:
    print("\nCleanup cancelled.")
    exit(0)

# Delete pipelines
print("\n" + "=" * 80)
print("Deleting pipelines...")
print("=" * 80)

deleted_count = 0
failed_count = 0

for pipeline in pipelines_to_delete:
    pipeline_id = pipeline.get('id')
    pipeline_name = pipeline.get('name')
    
    try:
        # Try to delete via API (soft delete by default)
        delete_response = requests.delete(f"{API_URL}/pipelines/{pipeline_id}?hard_delete=true", timeout=10)
        
        if delete_response.status_code in [200, 204]:
            print(f"   [OK] Deleted: {pipeline_name} ({pipeline_id})")
            deleted_count += 1
        elif delete_response.status_code == 404:
            print(f"   [INFO] Already deleted: {pipeline_name} ({pipeline_id})")
            deleted_count += 1
        else:
            print(f"   [ERROR] Failed to delete {pipeline_name}: {delete_response.status_code}")
            print(f"          Response: {delete_response.text[:200]}")
            failed_count += 1
    except Exception as e:
        print(f"   [ERROR] Exception deleting {pipeline_name}: {e}")
        failed_count += 1

print("\n" + "=" * 80)
print("Cleanup Complete!")
print("=" * 80)
print(f"Deleted: {deleted_count}")
print(f"Failed: {failed_count}")
print(f"Kept: {len(pipelines_to_keep)}")

if failed_count > 0:
    print("\n⚠️  Some pipelines could not be deleted. They may need to be deleted manually.")
    print("   Check the errors above for details.")

