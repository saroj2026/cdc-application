"""Check all pipelines and their status."""

import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000/api"
API_V1_URL = "http://localhost:8000/api/v1"

print("=" * 80)
print("Pipeline Status Check")
print("=" * 80)

# Get all pipelines
print("\n1. Fetching all pipelines from database...")
try:
    response = requests.get(f"{API_URL}/pipelines", timeout=10)
    if response.status_code == 200:
        pipelines = response.json()
        print(f"   [OK] Found {len(pipelines)} pipeline(s)\n")
    else:
        print(f"   [ERROR] Failed to get pipelines: {response.status_code}")
        print(f"   Response: {response.text[:300]}")
        exit(1)
except Exception as e:
    print(f"   [ERROR] Exception: {e}")
    exit(1)

if not pipelines:
    print("   No pipelines found in database.")
    exit(0)

# Get connections for reference
print("2. Fetching connections...")
try:
    conn_response = requests.get(f"{API_V1_URL}/connections", timeout=10)
    if conn_response.status_code == 200:
        connections = conn_response.json()
        conn_dict = {c.get('id'): c.get('name') for c in connections}
        print(f"   [OK] Found {len(connections)} connection(s)\n")
    else:
        conn_dict = {}
        print(f"   [WARNING] Could not fetch connections\n")
except:
    conn_dict = {}

# Display pipelines
print("=" * 80)
print(f"{'ID':<38} {'Name':<40} {'Status':<12} {'Mode':<20}")
print("=" * 80)

for pipeline in pipelines:
    pipeline_id = pipeline.get('id', 'N/A')[:36]
    name = pipeline.get('name', 'N/A')
    if len(name) > 38:
        name = name[:35] + "..."
    status = pipeline.get('status', 'UNKNOWN')
    mode = pipeline.get('mode', 'N/A')
    
    # Color coding for status
    status_display = status
    if status == "RUNNING":
        status_display = f"[RUNNING]"
    elif status == "STOPPED":
        status_display = f"[STOPPED]"
    elif status == "ERROR":
        status_display = f"[ERROR]"
    
    print(f"{pipeline_id:<38} {name:<40} {status_display:<12} {mode:<20}")

print("=" * 80)

# Detailed view for specific pipelines
print("\n3. Detailed Pipeline Information:")
print("-" * 80)

# Show details for first 5 pipelines or all if less than 5
show_count = min(5, len(pipelines))
for i, pipeline in enumerate(pipelines[:show_count]):
    print(f"\nPipeline {i+1}: {pipeline.get('name')}")
    print(f"  ID: {pipeline.get('id')}")
    print(f"  Status: {pipeline.get('status')}")
    print(f"  Mode: {pipeline.get('mode')}")
    print(f"  Full Load Status: {pipeline.get('full_load_status', 'N/A')}")
    print(f"  CDC Status: {pipeline.get('cdc_status', 'N/A')}")
    
    # Source connection
    source_conn_id = pipeline.get('source_connection_id')
    source_name = conn_dict.get(source_conn_id, source_conn_id[:8] + "..." if source_conn_id else "N/A")
    print(f"  Source: {source_name}")
    
    # Target connection
    target_conn_id = pipeline.get('target_connection_id')
    target_name = conn_dict.get(target_conn_id, target_conn_id[:8] + "..." if target_conn_id else "N/A")
    print(f"  Target: {target_name}")
    
    # Tables
    source_tables = pipeline.get('source_tables', [])
    if source_tables:
        print(f"  Source Tables: {', '.join(source_tables)}")
    
    # Connectors
    debezium_conn = pipeline.get('debezium_connector_name')
    sink_conn = pipeline.get('sink_connector_name')
    if debezium_conn:
        print(f"  Debezium Connector: {debezium_conn}")
    if sink_conn:
        print(f"  Sink Connector: {sink_conn}")

if len(pipelines) > show_count:
    print(f"\n... and {len(pipelines) - show_count} more pipeline(s)")

# Summary statistics
print("\n" + "=" * 80)
print("Summary Statistics:")
print("-" * 80)

status_counts = {}
mode_counts = {}
for pipeline in pipelines:
    status = pipeline.get('status', 'UNKNOWN')
    mode = pipeline.get('mode', 'N/A')
    status_counts[status] = status_counts.get(status, 0) + 1
    mode_counts[mode] = mode_counts.get(mode, 0) + 1

print("\nBy Status:")
for status, count in sorted(status_counts.items()):
    print(f"  {status}: {count}")

print("\nBy Mode:")
for mode, count in sorted(mode_counts.items()):
    print(f"  {mode}: {count}")

# Check for S3 pipelines
s3_pipelines = [p for p in pipelines if 's3' in p.get('name', '').lower() or 'S3' in p.get('name', '')]
if s3_pipelines:
    print(f"\nS3 Pipelines: {len(s3_pipelines)}")
    for p in s3_pipelines[:3]:
        print(f"  - {p.get('name')} ({p.get('status')})")

print("\n" + "=" * 80)
print("Check complete!")
print("=" * 80)


import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000/api"
API_V1_URL = "http://localhost:8000/api/v1"

print("=" * 80)
print("Pipeline Status Check")
print("=" * 80)

# Get all pipelines
print("\n1. Fetching all pipelines from database...")
try:
    response = requests.get(f"{API_URL}/pipelines", timeout=10)
    if response.status_code == 200:
        pipelines = response.json()
        print(f"   [OK] Found {len(pipelines)} pipeline(s)\n")
    else:
        print(f"   [ERROR] Failed to get pipelines: {response.status_code}")
        print(f"   Response: {response.text[:300]}")
        exit(1)
except Exception as e:
    print(f"   [ERROR] Exception: {e}")
    exit(1)

if not pipelines:
    print("   No pipelines found in database.")
    exit(0)

# Get connections for reference
print("2. Fetching connections...")
try:
    conn_response = requests.get(f"{API_V1_URL}/connections", timeout=10)
    if conn_response.status_code == 200:
        connections = conn_response.json()
        conn_dict = {c.get('id'): c.get('name') for c in connections}
        print(f"   [OK] Found {len(connections)} connection(s)\n")
    else:
        conn_dict = {}
        print(f"   [WARNING] Could not fetch connections\n")
except:
    conn_dict = {}

# Display pipelines
print("=" * 80)
print(f"{'ID':<38} {'Name':<40} {'Status':<12} {'Mode':<20}")
print("=" * 80)

for pipeline in pipelines:
    pipeline_id = pipeline.get('id', 'N/A')[:36]
    name = pipeline.get('name', 'N/A')
    if len(name) > 38:
        name = name[:35] + "..."
    status = pipeline.get('status', 'UNKNOWN')
    mode = pipeline.get('mode', 'N/A')
    
    # Color coding for status
    status_display = status
    if status == "RUNNING":
        status_display = f"[RUNNING]"
    elif status == "STOPPED":
        status_display = f"[STOPPED]"
    elif status == "ERROR":
        status_display = f"[ERROR]"
    
    print(f"{pipeline_id:<38} {name:<40} {status_display:<12} {mode:<20}")

print("=" * 80)

# Detailed view for specific pipelines
print("\n3. Detailed Pipeline Information:")
print("-" * 80)

# Show details for first 5 pipelines or all if less than 5
show_count = min(5, len(pipelines))
for i, pipeline in enumerate(pipelines[:show_count]):
    print(f"\nPipeline {i+1}: {pipeline.get('name')}")
    print(f"  ID: {pipeline.get('id')}")
    print(f"  Status: {pipeline.get('status')}")
    print(f"  Mode: {pipeline.get('mode')}")
    print(f"  Full Load Status: {pipeline.get('full_load_status', 'N/A')}")
    print(f"  CDC Status: {pipeline.get('cdc_status', 'N/A')}")
    
    # Source connection
    source_conn_id = pipeline.get('source_connection_id')
    source_name = conn_dict.get(source_conn_id, source_conn_id[:8] + "..." if source_conn_id else "N/A")
    print(f"  Source: {source_name}")
    
    # Target connection
    target_conn_id = pipeline.get('target_connection_id')
    target_name = conn_dict.get(target_conn_id, target_conn_id[:8] + "..." if target_conn_id else "N/A")
    print(f"  Target: {target_name}")
    
    # Tables
    source_tables = pipeline.get('source_tables', [])
    if source_tables:
        print(f"  Source Tables: {', '.join(source_tables)}")
    
    # Connectors
    debezium_conn = pipeline.get('debezium_connector_name')
    sink_conn = pipeline.get('sink_connector_name')
    if debezium_conn:
        print(f"  Debezium Connector: {debezium_conn}")
    if sink_conn:
        print(f"  Sink Connector: {sink_conn}")

if len(pipelines) > show_count:
    print(f"\n... and {len(pipelines) - show_count} more pipeline(s)")

# Summary statistics
print("\n" + "=" * 80)
print("Summary Statistics:")
print("-" * 80)

status_counts = {}
mode_counts = {}
for pipeline in pipelines:
    status = pipeline.get('status', 'UNKNOWN')
    mode = pipeline.get('mode', 'N/A')
    status_counts[status] = status_counts.get(status, 0) + 1
    mode_counts[mode] = mode_counts.get(mode, 0) + 1

print("\nBy Status:")
for status, count in sorted(status_counts.items()):
    print(f"  {status}: {count}")

print("\nBy Mode:")
for mode, count in sorted(mode_counts.items()):
    print(f"  {mode}: {count}")

# Check for S3 pipelines
s3_pipelines = [p for p in pipelines if 's3' in p.get('name', '').lower() or 'S3' in p.get('name', '')]
if s3_pipelines:
    print(f"\nS3 Pipelines: {len(s3_pipelines)}")
    for p in s3_pipelines[:3]:
        print(f"  - {p.get('name')} ({p.get('status')})")

print("\n" + "=" * 80)
print("Check complete!")
print("=" * 80)

