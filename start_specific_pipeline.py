"""Start a specific pipeline by name."""

import requests
import sys
import json

API_BASE = "http://localhost:8000/api/v1"
PIPELINE_NAME = "PostgreSQL_to_S3_cdctest"

print("=" * 70)
print(f"Starting Pipeline: {PIPELINE_NAME}")
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
    
    # Find the specific pipeline
    target_pipeline = None
    for pipeline in pipelines:
        if pipeline.get('name') == PIPELINE_NAME:
            target_pipeline = pipeline
            break
    
    if not target_pipeline:
        print(f"\n❌ Pipeline '{PIPELINE_NAME}' not found.")
        print("\nAvailable pipelines:")
        for p in pipelines:
            print(f"  - {p.get('name')}")
        sys.exit(1)
    
    pipeline_id = target_pipeline['id']
    print(f"\n2. Found pipeline:")
    print(f"   Name: {target_pipeline.get('name')}")
    print(f"   ID: {pipeline_id}")
    print(f"   Status: {target_pipeline.get('status')}")
    print(f"   Mode: {target_pipeline.get('mode')}")
    print(f"   Full Load Status: {target_pipeline.get('full_load_status')}")
    print(f"   CDC Status: {target_pipeline.get('cdc_status')}")
    
    # Stop pipeline if running
    current_status = target_pipeline.get('status', '').upper()
    if current_status in ['RUNNING', 'STARTING', 'ACTIVE']:
        print(f"\n3. Stopping pipeline (current status: {current_status})...")
        try:
            stop_response = requests.post(
                f"{API_BASE}/pipelines/{pipeline_id}/stop",
                timeout=30
            )
            if stop_response.status_code == 200:
                print(f"   ✅ Pipeline stopped successfully")
                import time
                time.sleep(3)
            else:
                print(f"   ⚠️  Stop response: {stop_response.status_code}")
        except Exception as e:
            print(f"   ⚠️  Error stopping: {e}")
    else:
        print(f"\n3. Pipeline is already {current_status}")
    
    # Start pipeline
    print(f"\n4. Starting pipeline...")
    try:
        start_response = requests.post(
            f"{API_BASE}/pipelines/{pipeline_id}/start",
            timeout=120  # Longer timeout for full load + CDC setup
        )
        
        print(f"   Status Code: {start_response.status_code}")
        
        if start_response.status_code == 200:
            result = start_response.json()
            print(f"\n   ✅ Pipeline started successfully!")
            print(f"\n   Result:")
            print(json.dumps(result, indent=2))
            
            print(f"\n   Summary:")
            print(f"      Status: {result.get('status', 'unknown')}")
            print(f"      Message: {result.get('message', 'No message')}")
            
            if 'full_load' in result:
                fl = result['full_load']
                print(f"      Full Load Status: {fl.get('status', 'unknown')}")
                if 'rows_transferred' in fl:
                    print(f"      Rows Transferred: {fl.get('rows_transferred', 0)}")
            
            if 'debezium_connector' in result:
                dbz = result['debezium_connector']
                print(f"      Debezium Connector: {dbz.get('status', 'unknown')}")
                if 'name' in dbz:
                    print(f"      Debezium Connector Name: {dbz.get('name')}")
            
            if 'sink_connector' in result:
                sink = result['sink_connector']
                print(f"      Sink Connector: {sink.get('status', 'unknown')}")
                if 'name' in sink:
                    print(f"      Sink Connector Name: {sink.get('name')}")
            
            if 'kafka_topics' in result:
                topics = result.get('kafka_topics', [])
                print(f"      Kafka Topics: {len(topics)} topic(s)")
                if topics:
                    print(f"         {', '.join(topics[:5])}{'...' if len(topics) > 5 else ''}")
        else:
            print(f"\n   ❌ Error starting pipeline: {start_response.status_code}")
            print(f"\n   Error Response:")
            try:
                error_data = start_response.json()
                print(json.dumps(error_data, indent=2))
                
                # Extract detailed error if available
                detail = error_data.get('detail', '')
                if detail:
                    print(f"\n   Detailed Error: {detail}")
            except:
                print(f"   {start_response.text}")
    
    except requests.exceptions.Timeout:
        print(f"\n   ⚠️  Request timed out (pipeline may still be starting)")
        print(f"   Check pipeline status in the frontend or use:")
        print(f"   GET {API_BASE}/pipelines/{pipeline_id}/status")
    except Exception as e:
        print(f"\n   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("Complete")
    print("=" * 70)
    
except requests.exceptions.ConnectionError:
    print("\n❌ Could not connect to backend API at http://localhost:8000")
    print("   Make sure the backend is running: ./start_backend.sh")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()


