"""Restart pipeline and capture detailed error information."""

import requests
import json
import time

PIPELINE_ID = "ae7bb432-2fa8-48eb-90a0-d6bb4c164441"

print("=" * 70)
print("Restarting Pipeline with Detailed Logging")
print("=" * 70)

# First, stop the pipeline if it's running
print("\n1. Stopping pipeline if running...")
try:
    stop_response = requests.post(
        f"http://localhost:8000/api/v1/pipelines/{PIPELINE_ID}/stop",
        timeout=10
    )
    if stop_response.status_code == 200:
        print("   ✅ Pipeline stopped")
    else:
        print(f"   ⚠️  Stop response: {stop_response.status_code}")
except Exception as e:
    print(f"   ⚠️  Could not stop: {e}")

time.sleep(2)

# Get current pipeline info
print("\n2. Getting pipeline details...")
try:
    pipeline_response = requests.get(
        f"http://localhost:8000/api/v1/pipelines/{PIPELINE_ID}",
        timeout=10
    )
    if pipeline_response.status_code == 200:
        pipeline = pipeline_response.json()
        print(f"   Pipeline: {pipeline.get('name')}")
        print(f"   Status: {pipeline.get('status')}")
        print(f"   Mode: {pipeline.get('mode')}")
        print(f"   Debezium Connector: {pipeline.get('debezium_connector_name', 'N/A')}")
        print(f"   Sink Connector: {pipeline.get('sink_connector_name', 'N/A')}")
        print(f"   Kafka Topics: {pipeline.get('kafka_topics', [])}")
except Exception as e:
    print(f"   ⚠️  Error: {e}")

# Start the pipeline
print("\n3. Starting pipeline...")
try:
    start_response = requests.post(
        f"http://localhost:8000/api/v1/pipelines/{PIPELINE_ID}/start",
        timeout=180
    )
    
    print(f"   Status Code: {start_response.status_code}")
    
    if start_response.status_code == 200:
        result = start_response.json()
        print("   ✅ Pipeline started successfully!")
        print(f"   Result: {json.dumps(result, indent=2)}")
    else:
        error_detail = start_response.text
        print(f"   ❌ Error: {start_response.status_code}")
        print(f"   Response: {error_detail}")
        
        # Try to parse as JSON for better formatting
        try:
            error_json = json.loads(error_detail)
            print(f"   Error Details: {json.dumps(error_json, indent=2)}")
        except:
            pass
            
except requests.exceptions.Timeout:
    print("   ⚠️  Request timed out (pipeline may still be starting)")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Wait and check status
print("\n4. Waiting 5 seconds and checking final status...")
time.sleep(5)

try:
    status_response = requests.get(
        f"http://localhost:8000/api/v1/pipelines/{PIPELINE_ID}/status",
        timeout=15
    )
    if status_response.status_code == 200:
        status = status_response.json()
        print(f"\n   Pipeline Status: {status.get('status')}")
        print(f"   CDC Status: {status.get('cdc_status')}")
        print(f"   Full Load Status: {status.get('full_load_status')}")
        
        dbz = status.get('debezium_connector', {})
        if dbz and isinstance(dbz, dict):
            conn = dbz.get('connector', {})
            if isinstance(conn, dict):
                print(f"   Debezium: {conn.get('state', 'N/A')}")
        
        sink = status.get('sink_connector', {})
        if sink:
            if isinstance(sink, dict):
                conn = sink.get('connector', {})
                if isinstance(conn, dict):
                    print(f"   Sink: {conn.get('state', 'N/A')}")
            else:
                print(f"   Sink: {sink}")
        else:
            print("   Sink: Not created")
except Exception as e:
    print(f"   ⚠️  Could not get status: {e}")

print("\n" + "=" * 70)


