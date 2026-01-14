#!/usr/bin/env python3
"""Check if backend and frontend are running."""

import requests
import time

def check_backend():
    """Check backend health."""
    try:
        r = requests.get('http://localhost:8000/health', timeout=5)
        if r.status_code == 200:
            print("✓ Backend is running on http://localhost:8000")
            return True
        else:
            print(f"⚠ Backend returned status {r.status_code}")
            return False
    except Exception as e:
        print(f"✗ Backend is not accessible: {e}")
        return False

def check_frontend():
    """Check frontend."""
    try:
        r = requests.get('http://localhost:3000', timeout=5)
        if r.status_code == 200:
            print("✓ Frontend is running on http://localhost:3000")
            return True
        else:
            print(f"⚠ Frontend returned status {r.status_code}")
            return False
    except Exception as e:
        print(f"✗ Frontend is not accessible: {e}")
        return False

def check_pipeline():
    """Check pipeline status."""
    try:
        r = requests.get('http://localhost:8000/api/v1/pipelines/3b06bbae-2bbc-4526-ad6f-4e5d12c14f04', timeout=10)
        if r.status_code == 200:
            p = r.json()
            print("\n=== PIPELINE STATUS ===")
            print(f"Status: {p.get('status')}")
            print(f"Full Load Status: {p.get('full_load_status')}")
            print(f"CDC Status: {p.get('cdc_status')}")
            print(f"Mode: {p.get('mode')}")
            print(f"Debezium Connector: {p.get('debezium_connector_name', 'None')}")
            print(f"Sink Connector: {p.get('sink_connector_name', 'None')}")
            print(f"Kafka Topics: {p.get('kafka_topics', [])}")
            if p.get('error'):
                print(f"Error: {p.get('error')[:200]}")
            return True
        else:
            print(f"⚠ Could not get pipeline status: {r.status_code}")
            return False
    except Exception as e:
        print(f"✗ Could not check pipeline: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Checking Services Status")
    print("=" * 60)
    
    print("\n1. Checking Backend...")
    backend_ok = check_backend()
    
    print("\n2. Checking Frontend...")
    frontend_ok = check_frontend()
    
    if backend_ok:
        print("\n3. Checking Pipeline Status...")
        check_pipeline()
    
    print("\n" + "=" * 60)
    if backend_ok and frontend_ok:
        print("✓ Both services are running!")
    else:
        print("⚠ Some services are not running")
    print("=" * 60)

