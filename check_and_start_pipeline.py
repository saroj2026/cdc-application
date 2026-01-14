#!/usr/bin/env python3
"""Check pipeline status and start it if stopped."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ingestion.database.session import get_db
from ingestion.database.models_db import PipelineModel
from ingestion.cdc_manager import CDCManager
import requests

print("=" * 70)
print("CHECKING AND STARTING ORACLE_SF_P PIPELINE")
print("=" * 70)

pipeline_name = "oracle_sf_p"

try:
    db = next(get_db())
    
    # Get pipeline from database
    pipeline_model = db.query(PipelineModel).filter_by(name=pipeline_name).first()
    
    if not pipeline_model:
        print(f"❌ Pipeline '{pipeline_name}' not found in database")
        exit(1)
    
    print(f"\n1. Pipeline Status:")
    print(f"   Name: {pipeline_model.name}")
    print(f"   Status: {pipeline_model.status}")
    print(f"   Mode: {pipeline_model.mode}")
    print(f"   Full Load Status: {pipeline_model.full_load_status}")
    
    # Check connector status
    kafka_connect_url = "http://72.61.233.209:8083"
    sink_connector_name = "sink-oracle_sf_p-snow-public"
    source_connector_name = "cdc-oracle_sf_p-ora-cdc_user"
    
    print(f"\n2. Connector Status:")
    print("-" * 70)
    
    for connector_name in [source_connector_name, sink_connector_name]:
        try:
            r = requests.get(f"{kafka_connect_url}/connectors/{connector_name}/status", timeout=5)
            if r.status_code == 200:
                status = r.json()
                connector_state = status.get('connector', {}).get('state', 'N/A')
                print(f"   {connector_name}: {connector_state}")
            else:
                print(f"   {connector_name}: Not found ({r.status_code})")
        except Exception as e:
            print(f"   {connector_name}: Error - {e}")
    
    # Start pipeline if stopped
    if pipeline_model.status in ['STOPPED', 'FAILED', 'PAUSED']:
        print(f"\n3. Starting pipeline...")
        print("-" * 70)
        
        cdc_manager = CDCManager(db)
        
        try:
            result = cdc_manager.start_pipeline(pipeline_model.id)
            
            if result.get('success'):
                print(f"   ✅ Pipeline started successfully!")
                print(f"   Status: {result.get('status', 'N/A')}")
                
                # Wait a bit for connectors to initialize
                import time
                print(f"\n   Waiting 15 seconds for connectors to initialize...")
                time.sleep(15)
                
                # Check connector status again
                print(f"\n4. Connector Status After Start:")
                print("-" * 70)
                
                for connector_name in [source_connector_name, sink_connector_name]:
                    try:
                        r = requests.get(f"{kafka_connect_url}/connectors/{connector_name}/status", timeout=5)
                        if r.status_code == 200:
                            status = r.json()
                            connector_state = status.get('connector', {}).get('state', 'N/A')
                            tasks = status.get('tasks', [])
                            print(f"\n   {connector_name}:")
                            print(f"     State: {connector_state}")
                            for task in tasks:
                                task_state = task.get('state', 'N/A')
                                task_id = task.get('id', 'N/A')
                                print(f"     Task {task_id}: {task_state}")
                                if task_state == 'FAILED':
                                    trace = task.get('trace', '')
                                    if trace:
                                        print(f"       Error: {trace[:300]}")
                        else:
                            print(f"   {connector_name}: Not found ({r.status_code})")
                    except Exception as e:
                        print(f"   {connector_name}: Error - {e}")
            else:
                print(f"   ❌ Failed to start pipeline: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"   ❌ Error starting pipeline: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"\n3. Pipeline is already {pipeline_model.status}")
        print(f"   No action needed")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print("\n" + "=" * 70)
print("NEXT STEPS:")
print("  1. Wait 60-90 seconds for buffer flush")
print("  2. Insert/update data in Oracle")
print("  3. Check Snowflake for CDC events")
print("=" * 70)
