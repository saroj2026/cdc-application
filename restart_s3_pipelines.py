"""Stop and restart S3 pipelines to enable CDC."""

import requests
import time
import sys

API_BASE = "http://localhost:8000/api/v1"

print("=" * 70)
print("Restarting S3 Pipelines to Enable CDC")
print("=" * 70)

try:
    # Get all pipelines
    print("\n1. Fetching pipelines...")
    response = requests.get(f"{API_BASE}/pipelines", timeout=10)
    
    if response.status_code != 200:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   Response: {response.text}")
        sys.exit(1)
    
    pipelines = response.json()
    print(f"   ✅ Found {len(pipelines)} pipeline(s)")
    
    # Find S3 pipelines
    s3_pipelines = []
    for pipeline in pipelines:
        # Get target connection to check if it's S3
        try:
            target_conn_response = requests.get(
                f"{API_BASE}/connections/{pipeline['target_connection_id']}",
                timeout=10
            )
            if target_conn_response.status_code == 200:
                target_conn = target_conn_response.json()
                db_type = str(target_conn.get('database_type', '')).lower()
                if db_type in ['s3', 'aws_s3']:
                    # Check if mode is FULL_LOAD_AND_CDC
                    pipeline_mode = str(pipeline.get('mode', '')).lower()
                    if pipeline_mode in ['full_load_and_cdc', 'cdc_only']:
                        s3_pipelines.append(pipeline)
        except Exception as e:
            print(f"   ⚠️  Could not check connection for pipeline {pipeline.get('name')}: {e}")
            continue
    
    if not s3_pipelines:
        print("\n   ⚠️  No S3 pipelines with CDC enabled found.")
        sys.exit(0)
    
    print(f"\n2. Found {len(s3_pipelines)} S3 pipeline(s) with CDC enabled:\n")
    for pipeline in s3_pipelines:
        print(f"   - {pipeline['name']} (ID: {pipeline['id']})")
        print(f"     Status: {pipeline.get('status', 'unknown')}")
        print(f"     Mode: {pipeline.get('mode', 'unknown')}")
        print()
    
    # Stop running pipelines
    print("3. Stopping running pipelines...\n")
    for pipeline in s3_pipelines:
        pipeline_id = pipeline['id']
        pipeline_name = pipeline['name']
        status = pipeline.get('status', '').upper()
        
        if status in ['RUNNING', 'STARTING', 'ACTIVE']:
            print(f"   Stopping {pipeline_name}...")
            try:
                stop_response = requests.post(
                    f"{API_BASE}/pipelines/{pipeline_id}/stop",
                    timeout=30
                )
                if stop_response.status_code == 200:
                    print(f"   ✅ {pipeline_name} stopped successfully")
                    # Wait a bit for cleanup
                    time.sleep(2)
                else:
                    print(f"   ⚠️  Stop response: {stop_response.status_code}")
                    print(f"   Response: {stop_response.text}")
            except Exception as e:
                print(f"   ⚠️  Error stopping {pipeline_name}: {e}")
        else:
            print(f"   ℹ️  {pipeline_name} is already {status}")
    
    # Wait a bit before restarting
    print("\n4. Waiting 3 seconds before restarting...")
    time.sleep(3)
    
    # Start pipelines
    print("\n5. Starting pipelines with CDC enabled...\n")
    for pipeline in s3_pipelines:
        pipeline_id = pipeline['id']
        pipeline_name = pipeline['name']
        
        print(f"   Starting {pipeline_name}...")
        try:
            start_response = requests.post(
                f"{API_BASE}/pipelines/{pipeline_id}/start",
                timeout=60
            )
            
            if start_response.status_code == 200:
                result = start_response.json()
                print(f"   ✅ {pipeline_name} started successfully")
                print(f"      Status: {result.get('status', 'unknown')}")
                print(f"      Message: {result.get('message', 'No message')}")
                
                # Check if CDC is enabled
                if 'debezium_connector' in result:
                    dbz_status = result['debezium_connector'].get('status', 'unknown')
                    print(f"      Debezium Connector: {dbz_status}")
                
                if 'sink_connector' in result:
                    sink_status = result['sink_connector'].get('status', 'unknown')
                    print(f"      Sink Connector: {sink_status}")
                
                print()
            else:
                print(f"   ❌ Error starting {pipeline_name}: {start_response.status_code}")
                print(f"   Response: {start_response.text}")
                print()
        except Exception as e:
            print(f"   ❌ Error starting {pipeline_name}: {e}")
            print()
    
    print("=" * 70)
    print("✅ Pipeline Restart Complete")
    print("=" * 70)
    print("\n📊 Next Steps:")
    print("   1. Check the pipeline status in the frontend")
    print("   2. Wait for full load to complete")
    print("   3. CDC should automatically start after full load")
    print("   4. Monitor CDC events in the Analytics page")
    print("   5. Check S3 bucket for CDC event files (JSON format)")
    print("=" * 70)
    
except requests.exceptions.ConnectionError:
    print("\n❌ Could not connect to backend API at http://localhost:8000")
    print("   Make sure the backend is running: ./start_backend.sh")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()


