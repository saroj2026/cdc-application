"""Check pipeline mode value."""

import requests

API_URL = "http://localhost:8000/api"

pipeline_id = "07cd7358-0c80-4c6f-9e2a-8cf5d8845017"

print("=" * 80)
print("Checking Pipeline Mode")
print("=" * 80)

response = requests.get(f"{API_URL}/pipelines/{pipeline_id}")
if response.status_code == 200:
    pipeline = response.json()
    print(f"\nPipeline: {pipeline.get('name')}")
    print(f"Mode: {pipeline.get('mode')}")
    print(f"Mode type: {type(pipeline.get('mode'))}")
    print(f"Full load status: {pipeline.get('full_load_status')}")
    print(f"Full load LSN: {pipeline.get('full_load_lsn')}")
    print(f"CDC status: {pipeline.get('cdc_status')}")
    
    mode = pipeline.get('mode')
    if mode == "full_load_and_cdc":
        print("\n✅ Mode is 'full_load_and_cdc'")
    elif mode == "full_load_only":
        print("\n⚠️  Mode is 'full_load_only' (CDC disabled)")
    elif mode == "cdc_only":
        print("\n✅ Mode is 'cdc_only'")
    else:
        print(f"\n⚠️  Unknown mode: {mode}")
else:
    print(f"Error: {response.status_code}")


import requests

API_URL = "http://localhost:8000/api"

pipeline_id = "07cd7358-0c80-4c6f-9e2a-8cf5d8845017"

print("=" * 80)
print("Checking Pipeline Mode")
print("=" * 80)

response = requests.get(f"{API_URL}/pipelines/{pipeline_id}")
if response.status_code == 200:
    pipeline = response.json()
    print(f"\nPipeline: {pipeline.get('name')}")
    print(f"Mode: {pipeline.get('mode')}")
    print(f"Mode type: {type(pipeline.get('mode'))}")
    print(f"Full load status: {pipeline.get('full_load_status')}")
    print(f"Full load LSN: {pipeline.get('full_load_lsn')}")
    print(f"CDC status: {pipeline.get('cdc_status')}")
    
    mode = pipeline.get('mode')
    if mode == "full_load_and_cdc":
        print("\n✅ Mode is 'full_load_and_cdc'")
    elif mode == "full_load_only":
        print("\n⚠️  Mode is 'full_load_only' (CDC disabled)")
    elif mode == "cdc_only":
        print("\n✅ Mode is 'cdc_only'")
    else:
        print(f"\n⚠️  Unknown mode: {mode}")
else:
    print(f"Error: {response.status_code}")

