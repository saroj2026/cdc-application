#!/usr/bin/env python3
"""Get full task error trace."""

import requests
import json

print("=" * 70)
print("GETTING FULL TASK ERROR TRACE")
print("=" * 70)

kafka_connect_url = "http://72.61.233.209:8083"
sink_connector_name = "sink-oracle_sf_p-snow-public"

print("\n1. Getting task status...")
try:
    r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector_name}/tasks/0/status", timeout=5)
    if r.status_code == 200:
        task_status = r.json()
        print(f"   Task state: {task_status.get('state', 'N/A')}")
        print(f"   Worker ID: {task_status.get('worker_id', 'N/A')}")
        
        trace = task_status.get('trace', '')
        if trace:
            print(f"\n   Full Error Trace:")
            print("-" * 70)
            print(trace)
            print("-" * 70)
            
            # Check for specific error patterns
            if "ExtractNewRecordState" in trace:
                print("\n   ⚠ Error related to ExtractNewRecordState transform")
                print("   This might mean the Debezium transform library is not available")
            if "snowflake" in trace.lower():
                print("\n   ⚠ Error related to Snowflake connection/operation")
            if "topic" in trace.lower():
                print("\n   ⚠ Error related to topic mapping")
        else:
            print("   ⚠ No error trace available")
    else:
        print(f"   ❌ Error: {r.status_code}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n2. Getting connector configuration...")
try:
    r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector_name}/config", timeout=5)
    if r.status_code == 200:
        config = r.json()
        print(f"   Topics: {config.get('topics', 'N/A')}")
        print(f"   Topic2Table map: {config.get('snowflake.topic2table.map', 'N/A')}")
        print(f"   Transforms: {config.get('transforms', 'N/A')}")
        if config.get('transforms'):
            print(f"   Unwrap type: {config.get('transforms.unwrap.type', 'N/A')}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)

