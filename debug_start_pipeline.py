"""Debug pipeline start issue."""

import requests
import json

API_URL = "http://localhost:8000/api"
API_V1_URL = "http://localhost:8000/api/v1"

# Get pipeline
pipeline_id = "5ff86ed7-c619-46cd-a0de-af02281a73af"

print(f"1. Getting pipeline {pipeline_id}...")
r = requests.get(f"{API_URL}/pipelines/{pipeline_id}")
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    pipeline = r.json()
    print(f"   Name: {pipeline.get('name')}")
    print(f"   Status: {pipeline.get('status')}")

print(f"\n2. Getting connections...")
r = requests.get(f"{API_V1_URL}/connections")
connections = r.json()
postgres_conn = next((c for c in connections if c.get('database_type') == 'postgresql'), None)
s3_conn = next((c for c in connections if c.get('database_type') == 's3'), None)
print(f"   Postgres: {postgres_conn.get('id') if postgres_conn else 'Not found'}")
print(f"   S3: {s3_conn.get('id') if s3_conn else 'Not found'}")

print(f"\n3. Starting pipeline...")
r = requests.post(f"{API_URL}/pipelines/{pipeline_id}/start", timeout=60)
print(f"   Status: {r.status_code}")
print(f"   Response: {r.text[:500]}")


import requests
import json

API_URL = "http://localhost:8000/api"
API_V1_URL = "http://localhost:8000/api/v1"

# Get pipeline
pipeline_id = "5ff86ed7-c619-46cd-a0de-af02281a73af"

print(f"1. Getting pipeline {pipeline_id}...")
r = requests.get(f"{API_URL}/pipelines/{pipeline_id}")
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    pipeline = r.json()
    print(f"   Name: {pipeline.get('name')}")
    print(f"   Status: {pipeline.get('status')}")

print(f"\n2. Getting connections...")
r = requests.get(f"{API_V1_URL}/connections")
connections = r.json()
postgres_conn = next((c for c in connections if c.get('database_type') == 'postgresql'), None)
s3_conn = next((c for c in connections if c.get('database_type') == 's3'), None)
print(f"   Postgres: {postgres_conn.get('id') if postgres_conn else 'Not found'}")
print(f"   S3: {s3_conn.get('id') if s3_conn else 'Not found'}")

print(f"\n3. Starting pipeline...")
r = requests.post(f"{API_URL}/pipelines/{pipeline_id}/start", timeout=60)
print(f"   Status: {r.status_code}")
print(f"   Response: {r.text[:500]}")

