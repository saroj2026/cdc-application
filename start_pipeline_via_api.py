#!/usr/bin/env python3
"""Start pipeline via API endpoint."""

import requests
import time

print("=" * 70)
print("STARTING ORACLE_SF_P PIPELINE VIA API")
print("=" * 70)

api_url = "http://localhost:8000"
pipeline_name = "oracle_sf_p"
kafka_connect_url = "http://72.61.233.209:8083"

print("\n1. Getting pipeline details...")
try:
    # Get all pipelines
    r = requests.get(f"{api_url}/api/pipelines", timeout=5)
    if r.status_code == 200:
        pipelines = r.json()
        pipeline = None
        for p in pipelines:
            if p.get('name') == pipeline_name:
                pipeline = p
                break
        
        if not pipeline:
            print(f"   ❌ Pipeline '{pipeline_name}' not found")
            exit(1)
        
        pipeline_id = pipeline.get('id')
        print(f"   ✅ Found pipeline: {pipeline_name} (ID: {pipeline_id})")
        print(f"   Status: {pipeline.get('status')}")
        print(f"   Mode: {pipeline.get('mode')}")
        
        print(f"\n2. Starting pipeline...")
        print("-" * 70)
        
        start_r = requests.post(f"{api_url}/api/pipelines/{pipeline_id}/start", timeout=30)
        
        if start_r.status_code == 200:
            result = start_r.json()
            print(f"   ✅ Pipeline started successfully!")
            print(f"   Status: {result.get('status', 'N/A')}")
            
            # Wait for connectors to initialize
            print(f"\n   Waiting 20 seconds for connectors to initialize...")
            time.sleep(20)
            
            # Check connector status
            print(f"\n3. Connector Status:")
            print("-" * 70)
            
            source_connector = "cdc-oracle_sf_p-ora-cdc_user"
            sink_connector = "sink-oracle_sf_p-snow-public"
            
            for connector_name in [source_connector, sink_connector]:
                try:
                    r = requests.get(f"{kafka_connect_url}/connectors/{connector_name}/status", timeout=5)
                    if r.status_code == 200:
                        status = r.json()
                        connector_state = status.get('connector', {}).get('state', 'N/A')
                        tasks = status.get('tasks', [])
                        print(f"\n   {connector_name}:")
                        print(f"     State: {connector_state}")
                        for task in tasks:
                            task_id = task.get('id', 'N/A')
                            task_state = task.get('state', 'N/A')
                            print(f"     Task {task_id}: {task_state}")
                            
                            if task_state == 'FAILED':
                                trace = task.get('trace', '')
                                if trace:
                                    print(f"       Error: {trace[:400]}")
                            elif task_state == 'RUNNING':
                                print(f"       ✅ Task is RUNNING!")
                    else:
                        print(f"   {connector_name}: Not found ({r.status_code})")
                except Exception as e:
                    print(f"   {connector_name}: Error - {e}")
        else:
            print(f"   ❌ Failed to start pipeline: {start_r.status_code}")
            print(f"   Response: {start_r.text}")
    else:
        print(f"   ❌ Error getting pipelines: {r.status_code}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("NEXT STEPS:")
print("  1. Wait 60-90 seconds for buffer flush")
print("  2. Insert/update data in Oracle")
print("  3. Check Snowflake for CDC events")
print("=" * 70)

