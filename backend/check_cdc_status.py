"""Check CDC status and configuration."""

import requests
import json

API_URL = "http://localhost:8000/api"

print("=" * 60)
print("CDC Status Check")
print("=" * 60)

# Check pipelines
print("\n1. Checking pipelines...")
response = requests.get(f"{API_URL}/pipelines")
if response.status_code == 200:
    pipelines = response.json()
    print(f"   Found {len(pipelines)} pipeline(s)\n")
    
    for pipeline in pipelines:
        print(f"   Pipeline: {pipeline.get('name')}")
        print(f"   ID: {pipeline.get('id')}")
        print(f"   Mode: {pipeline.get('mode')}")
        print(f"   Status: {pipeline.get('status')}")
        print(f"   Full Load Status: {pipeline.get('full_load_status')}")
        print(f"   CDC Status: {pipeline.get('cdc_status')}")
        print(f"   Debezium Connector: {pipeline.get('debezium_connector_name')}")
        print(f"   Sink Connector: {pipeline.get('sink_connector_name')}")
        print()
else:
    print(f"   ❌ Error: {response.status_code}")

# Check Kafka Connect
print("2. Checking Kafka Connect...")
KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
try:
    kafka_response = requests.get(f"{KAFKA_CONNECT_URL}/connectors", timeout=5)
    if kafka_response.status_code == 200:
        connectors = kafka_response.json()
        print(f"   ✅ Kafka Connect is running")
        print(f"   Active connectors: {len(connectors)}")
        if connectors:
            print(f"   Connectors: {', '.join(connectors)}")
        else:
            print("   ⚠️  No connectors configured")
    else:
        print(f"   ⚠️  Kafka Connect returned: {kafka_response.status_code}")
except requests.exceptions.ConnectionError:
    print(f"   ❌ Kafka Connect is not running or not accessible at {KAFKA_CONNECT_URL}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check Kafka
print("\n3. Checking Kafka...")
try:
    # Try to check if Kafka is accessible (basic check)
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 9092))
    sock.close()
    if result == 0:
        print("   ✅ Kafka port 9092 is accessible")
    else:
        print("   ❌ Kafka port 9092 is not accessible")
except Exception as e:
    print(f"   ⚠️  Could not check Kafka: {e}")

print("\n" + "=" * 60)
print("CDC Analysis")
print("=" * 60)

# Analyze why CDC isn't working
print("\nIssues found:")
issues = []

if pipelines:
    for pipeline in pipelines:
        mode = pipeline.get('mode', '')
        cdc_status = pipeline.get('cdc_status', '')
        debezium = pipeline.get('debezium_connector_name')
        
        if mode == 'full_load_only':
            issues.append(f"Pipeline '{pipeline.get('name')}' is in 'full_load_only' mode - CDC is disabled")
        
        if mode in ['full_load_and_cdc', 'cdc_only']:
            if not debezium:
                issues.append(f"Pipeline '{pipeline.get('name')}' has no Debezium connector configured")
            if cdc_status == 'NOT_STARTED':
                issues.append(f"Pipeline '{pipeline.get('name')}' CDC status is NOT_STARTED")

if not issues:
    print("   ✅ No obvious issues found")
else:
    for i, issue in enumerate(issues, 1):
        print(f"   {i}. {issue}")

print("\n" + "=" * 60)

