#!/usr/bin/env python3
"""Fix AS400 CDC to use offset from full load instead of taking snapshot."""

import requests
import json

API_BASE = "http://localhost:8000/api/v1"
KAFKA_CONNECT = "http://72.61.233.209:8083"
PIPELINE_NAME = "AS400-S3_P"

def get_pipeline():
    """Get AS400-S3_P pipeline."""
    response = requests.get(f"{API_BASE}/pipelines")
    if response.status_code != 200:
        print(f"❌ Failed to get pipelines: {response.status_code}")
        return None
    
    pipelines = response.json()
    pipeline = next((p for p in pipelines if p.get('name') == PIPELINE_NAME), None)
    return pipeline

def get_connector_config(connector_name):
    """Get connector configuration."""
    response = requests.get(f"{KAFKA_CONNECT}/connectors/{connector_name}/config")
    if response.status_code == 200:
        return response.json()
    return None

def update_connector_for_offset_mode(connector_name, pipeline):
    """Update connector to use offset mode when full load is done."""
    config = get_connector_config(connector_name)
    if not config:
        print(f"❌ Failed to get connector config")
        return False
    
    # Check if full load is completed
    full_load_status = pipeline.get('full_load_status', '')
    full_load_lsn = pipeline.get('full_load_lsn')
    
    print(f"\n📊 Pipeline Status:")
    print(f"   Full Load Status: {full_load_status}")
    print(f"   Full Load LSN/Offset: {full_load_lsn}")
    
    # Determine correct snapshot mode
    if full_load_status == 'COMPLETED' and full_load_lsn:
        # Full load done - should use "never" or "schema_only" to start from offset
        new_snapshot_mode = "never"  # Start from stored offset, no snapshot
        print(f"\n✅ Full load completed with offset captured")
        print(f"   Should use snapshot.mode='never' to start from offset")
    else:
        # No full load or no offset - use initial snapshot
        new_snapshot_mode = "initial"
        print(f"\n⚠️  Full load not completed or no offset captured")
        print(f"   Using snapshot.mode='initial' to capture current state")
    
    current_mode = config.get('snapshot.mode', 'NOT SET')
    print(f"\n📝 Current snapshot.mode: {current_mode}")
    print(f"   Proposed snapshot.mode: {new_snapshot_mode}")
    
    if current_mode == new_snapshot_mode:
        print(f"\n✅ Snapshot mode is already correct: {new_snapshot_mode}")
        return True
    
    # Update config
    config['snapshot.mode'] = new_snapshot_mode
    
    print(f"\n🔄 Updating connector configuration...")
    response = requests.put(
        f"{KAFKA_CONNECT}/connectors/{connector_name}/config",
        json=config,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        print(f"✅ Connector configuration updated")
        print(f"   snapshot.mode changed: {current_mode} → {new_snapshot_mode}")
        
        # Restart connector
        print(f"\n🔄 Restarting connector...")
        restart_response = requests.post(f"{KAFKA_CONNECT}/connectors/{connector_name}/restart")
        if restart_response.status_code == 204:
            print(f"✅ Connector restart requested")
        else:
            print(f"⚠️  Restart response: {restart_response.status_code}")
        
        return True
    else:
        print(f"❌ Failed to update config: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def main():
    print("=" * 80)
    print("  FIXING AS400 CDC TO USE OFFSET FROM FULL LOAD")
    print("=" * 80)
    
    # Get pipeline
    print(f"\n1. Getting pipeline: {PIPELINE_NAME}")
    pipeline = get_pipeline()
    if not pipeline:
        print(f"❌ Pipeline not found: {PIPELINE_NAME}")
        return
    
    pipeline_id = pipeline.get('id')
    print(f"   ✅ Found pipeline: {pipeline_id}")
    
    # Find connector
    connector_name = f"cdc-as400-s3_p-as400-segmetriq1"
    print(f"\n2. Checking connector: {connector_name}")
    
    # Update connector
    if update_connector_for_offset_mode(connector_name, pipeline):
        print("\n" + "=" * 80)
        print("  ✅ CONFIGURATION UPDATED")
        print("=" * 80)
        print("\nThe connector will now:")
        if pipeline.get('full_load_status') == 'COMPLETED' and pipeline.get('full_load_lsn'):
            print("  ✅ Start CDC from the captured journal offset")
            print("  ✅ Skip snapshot (data already loaded via full load)")
            print("  ✅ Only capture new changes after full load")
        else:
            print("  ✅ Take initial snapshot of current data")
            print("  ✅ Then capture ongoing changes")
    else:
        print("\n" + "=" * 80)
        print("  ❌ FAILED TO UPDATE")
        print("=" * 80)

if __name__ == "__main__":
    main()

