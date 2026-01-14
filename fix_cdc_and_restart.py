#!/usr/bin/env python3
"""Fix CDC issues and restart pipeline.

This script:
1. Stops the oracle_sf_p pipeline
2. Restarts the backend
3. Starts the pipeline to verify CDC connectors are created
"""

import requests
import time
import subprocess
import sys
import os

# Pipeline ID
PIPELINE_ID = "3b06bbae-2bbc-4526-ad6f-4e5d12c14f04"
BACKEND_URL = "http://localhost:8000"
KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

def check_backend():
    """Check if backend is running."""
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return r.status_code == 200
    except:
        return False

def stop_pipeline():
    """Stop the pipeline."""
    try:
        r = requests.post(f"{BACKEND_URL}/api/v1/pipelines/{PIPELINE_ID}/stop", timeout=10)
        if r.status_code == 200:
            print("✓ Pipeline stopped")
        else:
            print(f"⚠ Pipeline stop returned {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"⚠ Could not stop pipeline: {e}")

def start_pipeline():
    """Start the pipeline."""
    try:
        r = requests.post(f"{BACKEND_URL}/api/v1/pipelines/{PIPELINE_ID}/start", timeout=30)
        if r.status_code == 200:
            print("✓ Pipeline started")
            return r.json()
        else:
            print(f"✗ Pipeline start failed: {r.status_code}")
            print(f"  Response: {r.text[:500]}")
            return None
    except Exception as e:
        print(f"✗ Could not start pipeline: {e}")
        return None

def get_pipeline_status():
    """Get pipeline status."""
    try:
        r = requests.get(f"{BACKEND_URL}/api/v1/pipelines/{PIPELINE_ID}", timeout=10)
        if r.status_code == 200:
            return r.json()
        else:
            return None
    except Exception as e:
        print(f"✗ Could not get pipeline status: {e}")
        return None

def check_kafka_connectors():
    """Check Kafka Connect connectors."""
    try:
        r = requests.get(f"{KAFKA_CONNECT_URL}/connectors", timeout=10)
        if r.status_code == 200:
            connectors = r.json()
            oracle_connectors = [c for c in connectors if 'oracle' in c.lower() or 'oracle_sf_p' in c.lower()]
            return connectors, oracle_connectors
        else:
            return [], []
    except Exception as e:
        print(f"⚠ Could not check Kafka connectors: {e}")
        return [], []

def main():
    print("=" * 60)
    print("Fixing CDC and Restarting Pipeline")
    print("=" * 60)
    
    # Step 1: Check backend
    print("\n1. Checking backend...")
    if not check_backend():
        print("✗ Backend is not running. Please start it manually.")
        print("  Command: python -m uvicorn ingestion.api:app --host 0.0.0.0 --port 8000")
        return
    print("✓ Backend is running")
    
    # Step 2: Stop pipeline
    print("\n2. Stopping pipeline...")
    stop_pipeline()
    time.sleep(3)
    
    # Step 3: Get current status
    print("\n3. Getting current pipeline status...")
    status = get_pipeline_status()
    if status:
        print(f"  Status: {status.get('status')}")
        print(f"  Full Load Status: {status.get('full_load_status')}")
        print(f"  CDC Status: {status.get('cdc_status')}")
        print(f"  Debezium Connector: {status.get('debezium_connector_name', 'None')}")
        print(f"  Sink Connector: {status.get('sink_connector_name', 'None')}")
        print(f"  Kafka Topics: {status.get('kafka_topics', [])}")
    
    # Step 4: Check existing Kafka connectors
    print("\n4. Checking existing Kafka connectors...")
    all_connectors, oracle_connectors = check_kafka_connectors()
    print(f"  Total connectors: {len(all_connectors)}")
    if oracle_connectors:
        print(f"  Oracle-related connectors: {oracle_connectors}")
    else:
        print("  No Oracle-related connectors found")
    
    # Step 5: Start pipeline
    print("\n5. Starting pipeline...")
    result = start_pipeline()
    if result:
        print(f"  Message: {result.get('message', 'N/A')}")
    
    # Step 6: Wait and check status
    print("\n6. Waiting for pipeline to initialize (30 seconds)...")
    time.sleep(30)
    
    print("\n7. Checking pipeline status after start...")
    status = get_pipeline_status()
    if status:
        print(f"  Status: {status.get('status')}")
        print(f"  Full Load Status: {status.get('full_load_status')}")
        print(f"  CDC Status: {status.get('cdc_status')}")
        print(f"  Debezium Connector: {status.get('debezium_connector_name', 'None')}")
        print(f"  Sink Connector: {status.get('sink_connector_name', 'None')}")
        print(f"  Kafka Topics: {status.get('kafka_topics', [])}")
        if status.get('error'):
            print(f"  Error: {status.get('error')[:300]}")
    
    # Step 7: Check Kafka connectors again
    print("\n8. Checking Kafka connectors after start...")
    all_connectors, oracle_connectors = check_kafka_connectors()
    print(f"  Total connectors: {len(all_connectors)}")
    if oracle_connectors:
        print(f"  Oracle-related connectors: {oracle_connectors}")
    else:
        print("  ⚠ No Oracle-related connectors found - CDC may not be working")
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)

if __name__ == "__main__":
    main()

