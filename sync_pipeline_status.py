"""Sync pipeline status with actual Kafka Connect connector states."""

import requests
import json

API_BASE = "http://localhost:8000/api/v1"
KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
PIPELINE_NAME = "PostgreSQL_to_S3_cdctest"

print("=" * 70)
print("Syncing Pipeline Status with Kafka Connect")
print("=" * 70)

try:
    # Get pipeline
    print("\n1. Getting pipeline...")
    response = requests.get(f"{API_BASE}/pipelines", timeout=10)
    pipelines = response.json()
    
    pipeline = None
    for p in pipelines:
        if p.get('name') == PIPELINE_NAME:
            pipeline = p
            break
    
    if not pipeline:
        print(f"Pipeline '{PIPELINE_NAME}' not found")
        exit(1)
    
    pipeline_id = pipeline['id']
    print(f"   Pipeline ID: {pipeline_id}")
    
    # Check Debezium connector
    debezium_name = f"cdc-{PIPELINE_NAME.lower().replace(' ', '_')}-pg-{pipeline.get('source_schema', 'public')}"
    print(f"\n2. Checking Debezium connector: {debezium_name}")
    
    try:
        dbz_status = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{debezium_name}/status", timeout=10)
        if dbz_status.status_code == 200:
            dbz_data = dbz_status.json()
            print(f"   ✅ Debezium connector is {dbz_data.get('connector', {}).get('state', 'UNKNOWN')}")
        else:
            print(f"   ⚠️  Debezium connector status: {dbz_status.status_code}")
    except Exception as e:
        print(f"   ❌ Error checking Debezium: {e}")
    
    # Check Sink connector - try known name first
    known_sink_name = "sink-postgresql_to_s3_cdctest-s3-public"
    print(f"\n3. Checking Sink connector: {known_sink_name}")
    
    sink_name_to_use = None
    try:
        sink_status = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{known_sink_name}/status", timeout=10)
        if sink_status.status_code == 200:
            sink_name_to_use = known_sink_name
            sink_data = sink_status.json()
            print(f"   ✅ Sink connector is {sink_data.get('connector', {}).get('state', 'UNKNOWN')}")
            
            # Update pipeline to include sink connector name
            print(f"\n4. Updating pipeline with sink connector name: {sink_name_to_use}...")
            update_data = {
                "sink_connector_name": sink_name_to_use
            }
            
            update_response = requests.put(
                f"{API_BASE}/pipelines/{pipeline_id}",
                json=update_data,
                timeout=10
            )
            
            if update_response.status_code == 200:
                print(f"   ✅ Pipeline updated successfully!")
            else:
                print(f"   ⚠️  Update response: {update_response.status_code}")
                print(f"   {update_response.text}")
        else:
            print(f"   ⚠️  Sink connector not found: {sink_status.status_code}")
    except Exception as e:
        print(f"   ❌ Error checking Sink: {e}")
    
    # Check final status
    print(f"\n5. Final pipeline status:")
    status_response = requests.get(f"{API_BASE}/pipelines/{pipeline_id}/status", timeout=10)
    if status_response.status_code == 200:
        status = status_response.json()
        print(json.dumps(status, indent=2))
    
    print("\n" + "=" * 70)
    print("✅ Sync Complete!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
