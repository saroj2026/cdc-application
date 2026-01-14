"""Identify duplicate pipelines."""

import requests
from collections import defaultdict

API_URL = "http://localhost:8000/api"

print("=" * 80)
print("Identifying Duplicate Pipelines")
print("=" * 80)

# Get all pipelines
print("\n1. Fetching all pipelines...")
response = requests.get(f"{API_URL}/pipelines", timeout=10)
if response.status_code != 200:
    print(f"   [ERROR] Failed to get pipelines: {response.status_code}")
    exit(1)

pipelines = response.json()
print(f"   [OK] Found {len(pipelines)} pipeline(s)\n")

# Group by name
name_groups = defaultdict(list)
for pipeline in pipelines:
    name = pipeline.get('name', '').strip()
    name_groups[name].append(pipeline)

# Find duplicates
duplicates = {name: plist for name, plist in name_groups.items() if len(plist) > 1}

if not duplicates:
    print("=" * 80)
    print("No duplicate pipeline names found!")
    print("=" * 80)
    exit(0)

print("=" * 80)
print(f"Found {len(duplicates)} duplicate name(s):")
print("=" * 80)

# Display duplicates
for name, plist in duplicates.items():
    print(f"\n'{name}' - {len(plist)} instances:")
    print("-" * 80)
    
    # Sort by created_at (newest first)
    sorted_pipelines = sorted(
        plist,
        key=lambda p: p.get('created_at', ''),
        reverse=True
    )
    
    for i, pipeline in enumerate(sorted_pipelines, 1):
        pipeline_id = pipeline.get('id')
        status = pipeline.get('status', 'UNKNOWN')
        mode = pipeline.get('mode', 'N/A')
        created = pipeline.get('created_at', 'N/A')
        full_load = pipeline.get('full_load_status', 'N/A')
        cdc = pipeline.get('cdc_status', 'N/A')
        
        # Determine which one to keep (newest, or one that's been started)
        keep_reason = ""
        if i == 1:
            keep_reason = " [KEEP - Newest]"
        elif status == "RUNNING":
            keep_reason = " [KEEP - Running]"
        elif full_load != "NOT_STARTED" or cdc != "NOT_STARTED":
            keep_reason = " [KEEP - Has progress]"
        else:
            keep_reason = " [DELETE]"
        
        print(f"  {i}. ID: {pipeline_id}")
        print(f"     Status: {status}, Mode: {mode}")
        print(f"     Full Load: {full_load}, CDC: {cdc}")
        print(f"     Created: {created}{keep_reason}")

print("\n" + "=" * 80)
print("Summary:")
print("=" * 80)
total_duplicates = sum(len(plist) - 1 for plist in duplicates.values())
print(f"Total duplicate pipelines to remove: {total_duplicates}")
print(f"Pipelines to keep: {len(duplicates)}")


import requests
from collections import defaultdict

API_URL = "http://localhost:8000/api"

print("=" * 80)
print("Identifying Duplicate Pipelines")
print("=" * 80)

# Get all pipelines
print("\n1. Fetching all pipelines...")
response = requests.get(f"{API_URL}/pipelines", timeout=10)
if response.status_code != 200:
    print(f"   [ERROR] Failed to get pipelines: {response.status_code}")
    exit(1)

pipelines = response.json()
print(f"   [OK] Found {len(pipelines)} pipeline(s)\n")

# Group by name
name_groups = defaultdict(list)
for pipeline in pipelines:
    name = pipeline.get('name', '').strip()
    name_groups[name].append(pipeline)

# Find duplicates
duplicates = {name: plist for name, plist in name_groups.items() if len(plist) > 1}

if not duplicates:
    print("=" * 80)
    print("No duplicate pipeline names found!")
    print("=" * 80)
    exit(0)

print("=" * 80)
print(f"Found {len(duplicates)} duplicate name(s):")
print("=" * 80)

# Display duplicates
for name, plist in duplicates.items():
    print(f"\n'{name}' - {len(plist)} instances:")
    print("-" * 80)
    
    # Sort by created_at (newest first)
    sorted_pipelines = sorted(
        plist,
        key=lambda p: p.get('created_at', ''),
        reverse=True
    )
    
    for i, pipeline in enumerate(sorted_pipelines, 1):
        pipeline_id = pipeline.get('id')
        status = pipeline.get('status', 'UNKNOWN')
        mode = pipeline.get('mode', 'N/A')
        created = pipeline.get('created_at', 'N/A')
        full_load = pipeline.get('full_load_status', 'N/A')
        cdc = pipeline.get('cdc_status', 'N/A')
        
        # Determine which one to keep (newest, or one that's been started)
        keep_reason = ""
        if i == 1:
            keep_reason = " [KEEP - Newest]"
        elif status == "RUNNING":
            keep_reason = " [KEEP - Running]"
        elif full_load != "NOT_STARTED" or cdc != "NOT_STARTED":
            keep_reason = " [KEEP - Has progress]"
        else:
            keep_reason = " [DELETE]"
        
        print(f"  {i}. ID: {pipeline_id}")
        print(f"     Status: {status}, Mode: {mode}")
        print(f"     Full Load: {full_load}, CDC: {cdc}")
        print(f"     Created: {created}{keep_reason}")

print("\n" + "=" * 80)
print("Summary:")
print("=" * 80)
total_duplicates = sum(len(plist) - 1 for plist in duplicates.values())
print(f"Total duplicate pipelines to remove: {total_duplicates}")
print(f"Pipelines to keep: {len(duplicates)}")

