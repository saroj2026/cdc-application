"""Find similar or duplicate pipelines by configuration."""

import requests
from collections import defaultdict
from difflib import SequenceMatcher

API_URL = "http://localhost:8000/api"

print("=" * 80)
print("Finding Similar/Duplicate Pipelines")
print("=" * 80)

# Get all pipelines
print("\n1. Fetching all pipelines...")
response = requests.get(f"{API_URL}/pipelines", timeout=10)
if response.status_code != 200:
    print(f"   [ERROR] Failed to get pipelines: {response.status_code}")
    exit(1)

pipelines = response.json()
print(f"   [OK] Found {len(pipelines)} pipeline(s)\n")

# Group by configuration (source, target, tables, mode)
config_groups = defaultdict(list)
for pipeline in pipelines:
    # Create a config key
    config_key = (
        pipeline.get('source_connection_id', ''),
        pipeline.get('target_connection_id', ''),
        tuple(sorted(pipeline.get('source_tables', []))),
        pipeline.get('mode', '')
    )
    config_groups[config_key].append(pipeline)

# Find duplicates by configuration
duplicates_by_config = {k: v for k, v in config_groups.items() if len(v) > 1}

# Find similar names (case-insensitive)
name_lower_map = defaultdict(list)
for pipeline in pipelines:
    name_lower = pipeline.get('name', '').lower().strip()
    name_lower_map[name_lower].append(pipeline)

duplicates_by_name = {k: v for k, v in name_lower_map.items() if len(v) > 1}

# Find similar names (fuzzy matching)
similar_names = []
for i, p1 in enumerate(pipelines):
    for p2 in pipelines[i+1:]:
        name1 = p1.get('name', '').lower()
        name2 = p2.get('name', '').lower()
        if name1 and name2:
            similarity = SequenceMatcher(None, name1, name2).ratio()
            if similarity > 0.8 and similarity < 1.0:  # Similar but not identical
                similar_names.append((p1, p2, similarity))

print("=" * 80)
print("Analysis Results:")
print("=" * 80)

# Show duplicates by exact configuration
if duplicates_by_config:
    print(f"\n1. Duplicates by Configuration: {len(duplicates_by_config)} group(s)")
    print("-" * 80)
    for config_key, plist in duplicates_by_config.items():
        source_conn, target_conn, tables, mode = config_key
        print(f"\n   Configuration: {mode} mode, Tables: {', '.join(tables)}")
        print(f"   Found {len(plist)} pipeline(s) with same config:")
        for p in plist:
            print(f"     - {p.get('name')} (ID: {p.get('id')[:8]}...)")
            print(f"       Status: {p.get('status')}, Created: {p.get('created_at', 'N/A')[:10]}")
else:
    print("\n1. No duplicates by exact configuration found")

# Show duplicates by name (case-insensitive)
if duplicates_by_name:
    print(f"\n2. Duplicates by Name (case-insensitive): {len(duplicates_by_name)} group(s)")
    print("-" * 80)
    for name_lower, plist in duplicates_by_name.items():
        print(f"\n   Name: '{plist[0].get('name')}'")
        print(f"   Found {len(plist)} pipeline(s):")
        for p in plist:
            print(f"     - {p.get('name')} (ID: {p.get('id')[:8]}...)")
            print(f"       Status: {p.get('status')}, Created: {p.get('created_at', 'N/A')[:10]}")
else:
    print("\n2. No duplicates by name (case-insensitive) found")

# Show similar names
if similar_names:
    print(f"\n3. Similar Names (fuzzy match >80%): {len(similar_names)} pair(s)")
    print("-" * 80)
    for p1, p2, similarity in similar_names[:10]:  # Show first 10
        print(f"\n   Similarity: {similarity:.1%}")
        print(f"     - {p1.get('name')} (ID: {p1.get('id')[:8]}...)")
        print(f"     - {p2.get('name')} (ID: {p2.get('id')[:8]}...)")
else:
    print("\n3. No similar names found")

# Summary
print("\n" + "=" * 80)
print("Summary:")
print("=" * 80)
total_config_dups = sum(len(v) - 1 for v in duplicates_by_config.values())
total_name_dups = sum(len(v) - 1 for v in duplicates_by_name.values())

print(f"Pipelines with duplicate config: {total_config_dups}")
print(f"Pipelines with duplicate names: {total_name_dups}")
print(f"Similar name pairs: {len(similar_names)}")

if duplicates_by_config or duplicates_by_name:
    print("\n💡 Recommendation: Run cleanup_duplicate_pipelines.py to remove duplicates")
else:
    print("\n✅ No obvious duplicates found!")


import requests
from collections import defaultdict
from difflib import SequenceMatcher

API_URL = "http://localhost:8000/api"

print("=" * 80)
print("Finding Similar/Duplicate Pipelines")
print("=" * 80)

# Get all pipelines
print("\n1. Fetching all pipelines...")
response = requests.get(f"{API_URL}/pipelines", timeout=10)
if response.status_code != 200:
    print(f"   [ERROR] Failed to get pipelines: {response.status_code}")
    exit(1)

pipelines = response.json()
print(f"   [OK] Found {len(pipelines)} pipeline(s)\n")

# Group by configuration (source, target, tables, mode)
config_groups = defaultdict(list)
for pipeline in pipelines:
    # Create a config key
    config_key = (
        pipeline.get('source_connection_id', ''),
        pipeline.get('target_connection_id', ''),
        tuple(sorted(pipeline.get('source_tables', []))),
        pipeline.get('mode', '')
    )
    config_groups[config_key].append(pipeline)

# Find duplicates by configuration
duplicates_by_config = {k: v for k, v in config_groups.items() if len(v) > 1}

# Find similar names (case-insensitive)
name_lower_map = defaultdict(list)
for pipeline in pipelines:
    name_lower = pipeline.get('name', '').lower().strip()
    name_lower_map[name_lower].append(pipeline)

duplicates_by_name = {k: v for k, v in name_lower_map.items() if len(v) > 1}

# Find similar names (fuzzy matching)
similar_names = []
for i, p1 in enumerate(pipelines):
    for p2 in pipelines[i+1:]:
        name1 = p1.get('name', '').lower()
        name2 = p2.get('name', '').lower()
        if name1 and name2:
            similarity = SequenceMatcher(None, name1, name2).ratio()
            if similarity > 0.8 and similarity < 1.0:  # Similar but not identical
                similar_names.append((p1, p2, similarity))

print("=" * 80)
print("Analysis Results:")
print("=" * 80)

# Show duplicates by exact configuration
if duplicates_by_config:
    print(f"\n1. Duplicates by Configuration: {len(duplicates_by_config)} group(s)")
    print("-" * 80)
    for config_key, plist in duplicates_by_config.items():
        source_conn, target_conn, tables, mode = config_key
        print(f"\n   Configuration: {mode} mode, Tables: {', '.join(tables)}")
        print(f"   Found {len(plist)} pipeline(s) with same config:")
        for p in plist:
            print(f"     - {p.get('name')} (ID: {p.get('id')[:8]}...)")
            print(f"       Status: {p.get('status')}, Created: {p.get('created_at', 'N/A')[:10]}")
else:
    print("\n1. No duplicates by exact configuration found")

# Show duplicates by name (case-insensitive)
if duplicates_by_name:
    print(f"\n2. Duplicates by Name (case-insensitive): {len(duplicates_by_name)} group(s)")
    print("-" * 80)
    for name_lower, plist in duplicates_by_name.items():
        print(f"\n   Name: '{plist[0].get('name')}'")
        print(f"   Found {len(plist)} pipeline(s):")
        for p in plist:
            print(f"     - {p.get('name')} (ID: {p.get('id')[:8]}...)")
            print(f"       Status: {p.get('status')}, Created: {p.get('created_at', 'N/A')[:10]}")
else:
    print("\n2. No duplicates by name (case-insensitive) found")

# Show similar names
if similar_names:
    print(f"\n3. Similar Names (fuzzy match >80%): {len(similar_names)} pair(s)")
    print("-" * 80)
    for p1, p2, similarity in similar_names[:10]:  # Show first 10
        print(f"\n   Similarity: {similarity:.1%}")
        print(f"     - {p1.get('name')} (ID: {p1.get('id')[:8]}...)")
        print(f"     - {p2.get('name')} (ID: {p2.get('id')[:8]}...)")
else:
    print("\n3. No similar names found")

# Summary
print("\n" + "=" * 80)
print("Summary:")
print("=" * 80)
total_config_dups = sum(len(v) - 1 for v in duplicates_by_config.values())
total_name_dups = sum(len(v) - 1 for v in duplicates_by_name.values())

print(f"Pipelines with duplicate config: {total_config_dups}")
print(f"Pipelines with duplicate names: {total_name_dups}")
print(f"Similar name pairs: {len(similar_names)}")

if duplicates_by_config or duplicates_by_name:
    print("\n💡 Recommendation: Run cleanup_duplicate_pipelines.py to remove duplicates")
else:
    print("\n✅ No obvious duplicates found!")

