#!/usr/bin/env python3
"""Restart pipeline and monitor CDC connector creation."""

import requests
import time
import json

PIPELINE_ID = "3b06bbae-2bbc-4526-ad6f-4e5d12c14f04"
BACKEND_URL = "http://localhost:8000"
KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

def get_pipeline_status():
    """Get pipeline status."""
    try:
        r = requests.get(f"{BACKEND_URL}/api/v1/pipelines/{PIPELINE_ID}", timeout=10)
        if r.status_code == 200:
            return r.json()
        else:
            return None
    except Exception as e:
        print(f"✗ Error getting pipeline status: {e}")
        return None

def stop_pipeline():
    """Stop the pipeline."""
    try:
        r = requests.post(f"{BACKEND_URL}/api/v1/pipelines/{PIPELINE_ID}/stop", timeout=10)
        if r.status_code == 200:
            print("✓ Pipeline stopped")
            return True
        else:
            print(f"⚠ Stop returned {r.status_code}: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"⚠ Could not stop pipeline: {e}")
        return False

def start_pipeline():
    """Start the pipeline."""
    try:
        print("Starting pipeline...")
        r = requests.post(f"{BACKEND_URL}/api/v1/pipelines/{PIPELINE_ID}/start", timeout=60)
        if r.status_code == 200:
            result = r.json()
            print("✓ Pipeline start initiated")
            print(f"  Message: {result.get('message', 'N/A')}")
            return True
        else:
            print(f"✗ Pipeline start failed: {r.status_code}")
            print(f"  Response: {r.text[:500]}")
            return False
    except Exception as e:
        print(f"✗ Could not start pipeline: {e}")
        return False

def check_kafka_connectors():
    """Check Kafka Connect connectors."""
    try:
        r = requests.get(f"{KAFKA_CONNECT_URL}/connectors", timeout=10)
        if r.status_code == 200:
            connectors = r.json()
            oracle_connectors = [c for c in connectors if 'oracle' in c.lower() or 'oracle_sf_p' in c.lower() or PIPELINE_ID[:8] in c.lower()]
            return connectors, oracle_connectors
        else:
            return [], []
    except Exception as e:
        print(f"⚠ Could not check Kafka connectors: {e}")
        return [], []

def get_connector_status(connector_name):
    """Get connector status."""
    try:
        r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{connector_name}/status", timeout=10)
        if r.status_code == 200:
            return r.json()
        else:
            return None
    except Exception as e:
        return None

def main():
    print("=" * 70)
    print("Restarting Pipeline and Monitoring CDC Connector Creation")
    print("=" * 70)
    
    # Step 1: Get current status
    print("\n1. Current Pipeline Status:")
    status = get_pipeline_status()
    if status:
        print(f"   Status: {status.get('status')}")
        print(f"   Full Load: {status.get('full_load_status')}")
        print(f"   CDC Status: {status.get('cdc_status')}")
        print(f"   Mode: {status.get('mode')}")
        print(f"   Debezium Connector: {status.get('debezium_connector_name', 'None')}")
        print(f"   Sink Connector: {status.get('sink_connector_name', 'None')}")
        print(f"   Kafka Topics: {status.get('kafka_topics', [])}")
    
    # Step 2: Check existing Kafka connectors
    print("\n2. Existing Kafka Connectors:")
    all_connectors, oracle_connectors = check_kafka_connectors()
    print(f"   Total connectors: {len(all_connectors)}")
    if oracle_connectors:
        print(f"   Oracle-related connectors: {oracle_connectors}")
        for conn_name in oracle_connectors:
            conn_status = get_connector_status(conn_name)
            if conn_status:
                state = conn_status.get('connector', {}).get('state', 'UNKNOWN')
                print(f"     - {conn_name}: {state}")
    else:
        print("   No Oracle-related connectors found")
    
    # Step 3: Stop pipeline
    print("\n3. Stopping Pipeline...")
    stop_pipeline()
    time.sleep(3)
    
    # Step 4: Start pipeline
    print("\n4. Starting Pipeline...")
    start_pipeline()
    
    # Step 5: Monitor progress
    print("\n5. Monitoring Pipeline Progress...")
    print("   (This may take 30-60 seconds for connectors to be created)")
    
    max_wait = 90  # Maximum wait time in seconds
    check_interval = 5  # Check every 5 seconds
    elapsed = 0
    
    while elapsed < max_wait:
        time.sleep(check_interval)
        elapsed += check_interval
        
        status = get_pipeline_status()
        if status:
            print(f"\n   [{elapsed}s] Status Check:")
            print(f"      Status: {status.get('status')}")
            print(f"      CDC Status: {status.get('cdc_status')}")
            print(f"      Debezium: {status.get('debezium_connector_name', 'None')}")
            print(f"      Sink: {status.get('sink_connector_name', 'None')}")
            print(f"      Topics: {len(status.get('kafka_topics', []))} topics")
            
            # Check if connectors are created
            if status.get('debezium_connector_name') and status.get('sink_connector_name'):
                print("\n   ✓ Both connectors are created!")
                
                # Check connector status in Kafka Connect
                dbz_name = status.get('debezium_connector_name')
                sink_name = status.get('sink_connector_name')
                
                if dbz_name:
                    dbz_status = get_connector_status(dbz_name)
                    if dbz_status:
                        dbz_state = dbz_status.get('connector', {}).get('state', 'UNKNOWN')
                        print(f"      Debezium connector state: {dbz_state}")
                
                if sink_name:
                    sink_status = get_connector_status(sink_name)
                    if sink_status:
                        sink_state = sink_status.get('connector', {}).get('state', 'UNKNOWN')
                        print(f"      Sink connector state: {sink_state}")
                
                if status.get('kafka_topics'):
                    print(f"      Kafka Topics: {status.get('kafka_topics')}")
                
                break
        
        if elapsed % 15 == 0:
            # Check Kafka connectors directly
            all_connectors, oracle_connectors = check_kafka_connectors()
            if oracle_connectors:
                print(f"   [{elapsed}s] Found Oracle connectors in Kafka Connect: {oracle_connectors}")
    
    # Final status
    print("\n6. Final Pipeline Status:")
    status = get_pipeline_status()
    if status:
        print(f"   Status: {status.get('status')}")
        print(f"   Full Load: {status.get('full_load_status')}")
        print(f"   CDC Status: {status.get('cdc_status')}")
        print(f"   Debezium Connector: {status.get('debezium_connector_name', 'None')}")
        print(f"   Sink Connector: {status.get('sink_connector_name', 'None')}")
        print(f"   Kafka Topics: {status.get('kafka_topics', [])}")
        if status.get('error'):
            print(f"   Error: {status.get('error')[:300]}")
    
    # Final Kafka connector check
    print("\n7. Final Kafka Connector Check:")
    all_connectors, oracle_connectors = check_kafka_connectors()
    print(f"   Total connectors: {len(all_connectors)}")
    if oracle_connectors:
        print(f"   Oracle-related connectors: {oracle_connectors}")
        for conn_name in oracle_connectors:
            conn_status = get_connector_status(conn_name)
            if conn_status:
                state = conn_status.get('connector', {}).get('state', 'UNKNOWN')
                tasks = conn_status.get('tasks', [])
                print(f"     - {conn_name}: {state}")
                if tasks:
                    for i, task in enumerate(tasks):
                        task_state = task.get('state', 'UNKNOWN')
                        task_id = task.get('id', i)
                        print(f"       Task {task_id}: {task_state}")
    else:
        print("   ⚠ No Oracle-related connectors found")
    
    print("\n" + "=" * 70)
    print("Done!")
    print("=" * 70)

if __name__ == "__main__":
    main()

