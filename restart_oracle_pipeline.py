"""Restart the oracle_sf_p pipeline to apply the bootstrap.servers fix."""
import requests
import time

BACKEND_URL = "http://localhost:8000"

# Find oracle_sf_p pipeline ID
def find_oracle_pipeline():
    r = requests.get(f"{BACKEND_URL}/api/v1/pipelines")
    if r.status_code != 200:
        return None
    pipelines = r.json()
    oracle_pipelines = [p for p in pipelines if 'oracle' in p.get('name', '').lower() and 'sf' in p.get('name', '').lower()]
    return oracle_pipelines[0]['id'] if oracle_pipelines else None

print("=== RESTARTING ORACLE PIPELINE ===")

PIPELINE_ID = find_oracle_pipeline()
if not PIPELINE_ID:
    print("Error: Could not find oracle_sf_p pipeline")
    exit(1)

print(f"Found pipeline ID: {PIPELINE_ID}")

# First, get the pipeline to check its current status
r = requests.get(f"{BACKEND_URL}/api/v1/pipelines/{PIPELINE_ID}")
if r.status_code != 200:
    print(f"Error getting pipeline: {r.status_code}")
    print(r.text)
    exit(1)

pipeline = r.json()
print(f"Pipeline: {pipeline.get('name')}")
print(f"Current status: {pipeline.get('status')}")
print(f"CDC status: {pipeline.get('cdc_status')}")

# Stop the pipeline
print(f"\n1. Stopping pipeline...")
r = requests.post(f"{BACKEND_URL}/api/v1/pipelines/{PIPELINE_ID}/stop")
if r.status_code not in [200, 404]:
    print(f"Error stopping pipeline: {r.status_code}")
    print(r.text)
    exit(1)
print("Pipeline stopped")

# Wait a bit for connectors to stop
print("Waiting 5 seconds for connectors to stop...")
time.sleep(5)

# Start the pipeline again
print(f"\n2. Starting pipeline...")
r = requests.post(f"{BACKEND_URL}/api/v1/pipelines/{PIPELINE_ID}/start")
if r.status_code not in [200, 201]:
    print(f"Error starting pipeline: {r.status_code}")
    print(r.text)
    exit(1)
print("Pipeline started")

# Wait a bit for connectors to start
print("Waiting 10 seconds for connectors to start...")
time.sleep(10)

# Check the pipeline status
print(f"\n3. Checking pipeline status...")
r = requests.get(f"{BACKEND_URL}/api/v1/pipelines/{PIPELINE_ID}")
if r.status_code == 200:
    pipeline = r.json()
    print(f"Pipeline status: {pipeline.get('status')}")
    print(f"CDC status: {pipeline.get('cdc_status')}")
    print(f"Debezium connector: {pipeline.get('debezium_connector_name')}")
    print(f"Sink connector: {pipeline.get('sink_connector_name')}")

print("\n✓ Pipeline restarted successfully")
