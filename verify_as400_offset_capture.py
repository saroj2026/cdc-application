#!/usr/bin/env python3
"""Verify AS400 offset capture after full load."""

import requests
import time

API_BASE = "http://localhost:8000/api/v1"
PIPELINE_NAME = "AS400-S3_P"

def get_pipeline():
    """Get AS400-S3_P pipeline."""
    response = requests.get(f"{API_BASE}/pipelines")
    if response.status_code != 200:
        print(f"❌ Failed to get pipelines: {response.status_code}")
        return None
    
    pipelines = response.json()
    return next((p for p in pipelines if p.get('name') == PIPELINE_NAME), None)

def check_offset_capture():
    """Check if offset was captured after full load."""
    print("=" * 80)
    print("  VERIFYING AS400 OFFSET CAPTURE")
    print("=" * 80)
    
    pipeline = get_pipeline()
    if not pipeline:
        print("❌ Pipeline not found")
        return
    
    pipeline_id = pipeline.get('id')
    full_load_status = pipeline.get('full_load_status')
    full_load_lsn = pipeline.get('full_load_lsn')
    cdc_status = pipeline.get('cdc_status')
    
    print(f"\n📊 Pipeline: {pipeline.get('name')} (ID: {pipeline_id})")
    print(f"   Full Load Status: {full_load_status}")
    print(f"   Full Load LSN/Offset: {full_load_lsn}")
    print(f"   CDC Status: {cdc_status}")
    
    if full_load_status == 'COMPLETED':
        if full_load_lsn:
            print(f"\n✅ SUCCESS: Offset captured after full load!")
            print(f"   Offset: {full_load_lsn}")
            print(f"\n   This means:")
            print(f"   - Full load completed successfully")
            print(f"   - Journal offset was captured")
            print(f"   - Next CDC start will use snapshot.mode='never'")
            print(f"   - CDC will start from this offset (no duplicates)")
        else:
            print(f"\n⚠️  WARNING: Full load completed but offset NOT captured")
            print(f"   This means:")
            print(f"   - Full load completed")
            print(f"   - But extract_lsn_offset() may have failed")
            print(f"   - Or LSN extraction returned None")
            print(f"   - CDC will use snapshot.mode='initial' (may have duplicates)")
            print(f"\n   Checking backend logs would help diagnose why offset wasn't captured")
    else:
        print(f"\n⏳ Full load is still in progress or not started")
        print(f"   Status: {full_load_status}")
        print(f"   Wait for full load to complete, then check again")
    
    # Check connector config
    print(f"\n🔍 Checking connector configuration...")
    try:
        response = requests.get("http://72.61.233.209:8083/connectors/cdc-as400-s3_p-as400-segmetriq1/config")
        if response.status_code == 200:
            config = response.json()
            snapshot_mode = config.get('snapshot.mode', 'NOT SET')
            db_schema = config.get('database.schema', 'NOT SET')
            
            print(f"   snapshot.mode: {snapshot_mode}")
            print(f"   database.schema: {db_schema}")
            
            if full_load_lsn and snapshot_mode == 'never':
                print(f"\n✅ Perfect! Connector configured to use offset")
            elif not full_load_lsn and snapshot_mode == 'initial':
                print(f"\n✅ Correct! Connector using initial snapshot (no offset available)")
            elif full_load_lsn and snapshot_mode == 'initial':
                print(f"\n⚠️  Note: Offset exists but connector using initial snapshot")
                print(f"   This is OK for first run, but next restart should use 'never'")
    except Exception as e:
        print(f"   ⚠️  Could not check connector config: {e}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    check_offset_capture()

