"""Verify pipeline status from database and API."""
import sys
import requests
import json

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"
PIPELINE_ID = "79ba9d9e-5561-456d-8115-1d70466dfb67"

print("=" * 80)
print("Verifying Pipeline Status")
print("=" * 80)
print()

# Get all pipelines
print("1. Getting all pipelines from API...")
try:
    response = requests.get(f"{BASE_URL}/api/pipelines")
    response.raise_for_status()
    pipelines = response.json()
    
    final_test = [p for p in pipelines if p.get('name') == 'final_test']
    if final_test:
        p = final_test[0]
        print(f"   ✅ Found pipeline: {p.get('name')}")
        print(f"      ID: {p.get('id')}")
        print(f"      Status: {p.get('status')}")
        print(f"      Full Load Status: {p.get('full_load_status')}")
        print(f"      CDC Status: {p.get('cdc_status')}")
        print(f"      Mode: {p.get('mode')}")
        print(f"      Source Tables: {p.get('source_tables')}")
        print()
        
        if p.get('full_load_status') == 'COMPLETED':
            print("   ✅ Full load status is COMPLETED in database!")
        elif p.get('full_load_status') == 'NOT_STARTED':
            print("   ⚠️  Full load status is still NOT_STARTED")
            print("      This means the status wasn't persisted or pipeline wasn't started")
        elif p.get('full_load_status') == 'FAILED':
            print("   ❌ Full load status is FAILED")
        elif p.get('full_load_status') == 'IN_PROGRESS':
            print("   ⏳ Full load status is IN_PROGRESS")
    else:
        print("   ❌ Pipeline 'final_test' not found")
        
except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("Status Verification Complete")
print("=" * 80)

import sys
import requests
import json

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"
PIPELINE_ID = "79ba9d9e-5561-456d-8115-1d70466dfb67"

print("=" * 80)
print("Verifying Pipeline Status")
print("=" * 80)
print()

# Get all pipelines
print("1. Getting all pipelines from API...")
try:
    response = requests.get(f"{BASE_URL}/api/pipelines")
    response.raise_for_status()
    pipelines = response.json()
    
    final_test = [p for p in pipelines if p.get('name') == 'final_test']
    if final_test:
        p = final_test[0]
        print(f"   ✅ Found pipeline: {p.get('name')}")
        print(f"      ID: {p.get('id')}")
        print(f"      Status: {p.get('status')}")
        print(f"      Full Load Status: {p.get('full_load_status')}")
        print(f"      CDC Status: {p.get('cdc_status')}")
        print(f"      Mode: {p.get('mode')}")
        print(f"      Source Tables: {p.get('source_tables')}")
        print()
        
        if p.get('full_load_status') == 'COMPLETED':
            print("   ✅ Full load status is COMPLETED in database!")
        elif p.get('full_load_status') == 'NOT_STARTED':
            print("   ⚠️  Full load status is still NOT_STARTED")
            print("      This means the status wasn't persisted or pipeline wasn't started")
        elif p.get('full_load_status') == 'FAILED':
            print("   ❌ Full load status is FAILED")
        elif p.get('full_load_status') == 'IN_PROGRESS':
            print("   ⏳ Full load status is IN_PROGRESS")
    else:
        print("   ❌ Pipeline 'final_test' not found")
        
except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("Status Verification Complete")
print("=" * 80)

