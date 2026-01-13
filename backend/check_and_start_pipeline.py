"""Quick script to check pipelines and start one."""
import requests
import sys

BASE_URL = "http://localhost:8000"

# Get all pipelines
response = requests.get(f"{BASE_URL}/api/pipelines")
if response.status_code != 200:
    print(f"Error: {response.status_code}")
    sys.exit(1)

pipelines = response.json()
print(f"\nFound {len(pipelines)} pipeline(s):\n")

for i, p in enumerate(pipelines, 1):
    print(f"{i}. {p.get('name')}")
    print(f"   ID: {p.get('id')}")
    print(f"   Status: {p.get('status')}")
    print(f"   Full Load Status: {p.get('full_load_status')}")
    print(f"   CDC Status: {p.get('cdc_status')}")
    print()

if not pipelines:
    print("No pipelines found. Please create a pipeline first.")
    sys.exit(0)

# Use first pipeline or find final_test2/final_test
pipeline = None
for name in ["final_test2", "final_test"]:
    for p in pipelines:
        if p.get("name") == name:
            pipeline = p
            break
    if pipeline:
        break

if not pipeline:
    pipeline = pipelines[0]

print(f"Using pipeline: {pipeline.get('name')} (ID: {pipeline.get('id')})")
print(f"Current status: {pipeline.get('status')}, Full Load: {pipeline.get('full_load_status')}")

# Stop if running
if pipeline.get('status') in ['RUNNING', 'STARTING']:
    print("\nStopping pipeline...")
    stop_resp = requests.post(f"{BASE_URL}/api/pipelines/{pipeline.get('id')}/stop")
    if stop_resp.status_code == 200:
        print("✓ Stopped")
    else:
        print(f"⚠ Stop response: {stop_resp.status_code}")

# Start pipeline
print("\nStarting pipeline...")
start_resp = requests.post(f"{BASE_URL}/api/pipelines/{pipeline.get('id')}/start")
if start_resp.status_code == 200:
    result = start_resp.json()
    print("✓ Pipeline start requested")
    print(f"  Message: {result.get('message', 'OK')}")
    if result.get('full_load'):
        fl = result['full_load']
        print(f"  Full Load: success={fl.get('success')}, tables={fl.get('tables_transferred')}, rows={fl.get('total_rows')}")
else:
    print(f"✗ Failed to start: {start_resp.status_code}")
    print(f"  Response: {start_resp.text}")

import requests
import sys

BASE_URL = "http://localhost:8000"

# Get all pipelines
response = requests.get(f"{BASE_URL}/api/pipelines")
if response.status_code != 200:
    print(f"Error: {response.status_code}")
    sys.exit(1)

pipelines = response.json()
print(f"\nFound {len(pipelines)} pipeline(s):\n")

for i, p in enumerate(pipelines, 1):
    print(f"{i}. {p.get('name')}")
    print(f"   ID: {p.get('id')}")
    print(f"   Status: {p.get('status')}")
    print(f"   Full Load Status: {p.get('full_load_status')}")
    print(f"   CDC Status: {p.get('cdc_status')}")
    print()

if not pipelines:
    print("No pipelines found. Please create a pipeline first.")
    sys.exit(0)

# Use first pipeline or find final_test2/final_test
pipeline = None
for name in ["final_test2", "final_test"]:
    for p in pipelines:
        if p.get("name") == name:
            pipeline = p
            break
    if pipeline:
        break

if not pipeline:
    pipeline = pipelines[0]

print(f"Using pipeline: {pipeline.get('name')} (ID: {pipeline.get('id')})")
print(f"Current status: {pipeline.get('status')}, Full Load: {pipeline.get('full_load_status')}")

# Stop if running
if pipeline.get('status') in ['RUNNING', 'STARTING']:
    print("\nStopping pipeline...")
    stop_resp = requests.post(f"{BASE_URL}/api/pipelines/{pipeline.get('id')}/stop")
    if stop_resp.status_code == 200:
        print("✓ Stopped")
    else:
        print(f"⚠ Stop response: {stop_resp.status_code}")

# Start pipeline
print("\nStarting pipeline...")
start_resp = requests.post(f"{BASE_URL}/api/pipelines/{pipeline.get('id')}/start")
if start_resp.status_code == 200:
    result = start_resp.json()
    print("✓ Pipeline start requested")
    print(f"  Message: {result.get('message', 'OK')}")
    if result.get('full_load'):
        fl = result['full_load']
        print(f"  Full Load: success={fl.get('success')}, tables={fl.get('tables_transferred')}, rows={fl.get('total_rows')}")
else:
    print(f"✗ Failed to start: {start_resp.status_code}")
    print(f"  Response: {start_resp.text}")

