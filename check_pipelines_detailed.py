"""Check pipelines with detailed query."""

import requests
import json

API_URL = "http://localhost:8000/api"

print("=" * 80)
print("Detailed Pipeline Check")
print("=" * 80)

# Try different endpoints
endpoints = [
    ("/pipelines", "All pipelines"),
    ("/pipelines?skip=0&limit=100", "Pipelines with pagination"),
]

for endpoint, description in endpoints:
    print(f"\n{description}: {endpoint}")
    try:
        response = requests.get(f"{API_URL}{endpoint}", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"   Found {len(data)} pipeline(s)")
                if len(data) > 0:
                    print(f"   First pipeline: {data[0].get('name', 'N/A')}")
            elif isinstance(data, dict):
                print(f"   Response is dict with keys: {list(data.keys())}")
                if 'items' in data:
                    print(f"   Found {len(data['items'])} pipeline(s) in 'items'")
                if 'total' in data:
                    print(f"   Total: {data['total']}")
            else:
                print(f"   Response type: {type(data)}")
                print(f"   Response: {str(data)[:200]}")
        else:
            print(f"   Error: {response.text[:300]}")
    except Exception as e:
        print(f"   Exception: {e}")

# Check individual pipeline
print("\n" + "=" * 80)
print("Checking specific pipeline from pgAdmin...")
print("=" * 80)

# Try to get a pipeline by name
test_names = [
    "PostgreSQL_to_S3_Department_CDC",
    "PIPELINE-SAR",
    "Cloud_pipeline",
    "Test_CDC_S3_1767334253"
]

for name in test_names:
    print(f"\nSearching for: {name}")
    try:
        # Try to get all and filter
        response = requests.get(f"{API_URL}/pipelines", timeout=10)
        if response.status_code == 200:
            pipelines = response.json()
            found = [p for p in pipelines if p.get('name') == name]
            if found:
                p = found[0]
                print(f"   [FOUND] ID: {p.get('id')}")
                print(f"          Status: {p.get('status')}")
                print(f"          Mode: {p.get('mode')}")
            else:
                print(f"   [NOT FOUND] in API response")
    except Exception as e:
        print(f"   Exception: {e}")

print("\n" + "=" * 80)


import requests
import json

API_URL = "http://localhost:8000/api"

print("=" * 80)
print("Detailed Pipeline Check")
print("=" * 80)

# Try different endpoints
endpoints = [
    ("/pipelines", "All pipelines"),
    ("/pipelines?skip=0&limit=100", "Pipelines with pagination"),
]

for endpoint, description in endpoints:
    print(f"\n{description}: {endpoint}")
    try:
        response = requests.get(f"{API_URL}{endpoint}", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"   Found {len(data)} pipeline(s)")
                if len(data) > 0:
                    print(f"   First pipeline: {data[0].get('name', 'N/A')}")
            elif isinstance(data, dict):
                print(f"   Response is dict with keys: {list(data.keys())}")
                if 'items' in data:
                    print(f"   Found {len(data['items'])} pipeline(s) in 'items'")
                if 'total' in data:
                    print(f"   Total: {data['total']}")
            else:
                print(f"   Response type: {type(data)}")
                print(f"   Response: {str(data)[:200]}")
        else:
            print(f"   Error: {response.text[:300]}")
    except Exception as e:
        print(f"   Exception: {e}")

# Check individual pipeline
print("\n" + "=" * 80)
print("Checking specific pipeline from pgAdmin...")
print("=" * 80)

# Try to get a pipeline by name
test_names = [
    "PostgreSQL_to_S3_Department_CDC",
    "PIPELINE-SAR",
    "Cloud_pipeline",
    "Test_CDC_S3_1767334253"
]

for name in test_names:
    print(f"\nSearching for: {name}")
    try:
        # Try to get all and filter
        response = requests.get(f"{API_URL}/pipelines", timeout=10)
        if response.status_code == 200:
            pipelines = response.json()
            found = [p for p in pipelines if p.get('name') == name]
            if found:
                p = found[0]
                print(f"   [FOUND] ID: {p.get('id')}")
                print(f"          Status: {p.get('status')}")
                print(f"          Mode: {p.get('mode')}")
            else:
                print(f"   [NOT FOUND] in API response")
    except Exception as e:
        print(f"   Exception: {e}")

print("\n" + "=" * 80)

