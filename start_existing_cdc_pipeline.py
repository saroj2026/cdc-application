"""Start the existing CDC pipeline."""

import requests

API_URL = "http://localhost:8000/api"

print("=" * 60)
print("Start Existing CDC Pipeline")
print("=" * 60)

# Find the CDC pipeline
print("\n1. Finding CDC pipeline...")
response = requests.get(f"{API_URL}/pipelines")
if response.status_code != 200:
    print(f"❌ Error: {response.status_code}")
    exit(1)

pipelines = response.json()
cdc_pipeline = next((p for p in pipelines if 'CDC' in p.get('name', '') and p.get('mode') == 'full_load_and_cdc'), None)

if not cdc_pipeline:
    print("   ⚠️  CDC pipeline not found")
    print("   Available pipelines:")
    for p in pipelines:
        print(f"      - {p.get('name')} (mode: {p.get('mode')})")
    exit(1)

pipeline_id = cdc_pipeline.get('id')
print(f"   ✅ Found: {cdc_pipeline.get('name')}")
print(f"   ID: {pipeline_id}")
print(f"   Mode: {cdc_pipeline.get('mode')}")
print(f"   Status: {cdc_pipeline.get('status')}")

# Start the pipeline
print(f"\n2. Starting pipeline...")
start_response = requests.post(f"{API_URL}/pipelines/{pipeline_id}/start")

if start_response.status_code == 200:
    result = start_response.json()
    print(f"   ✅ Pipeline started!")
    print(f"   Status: {result.get('status')}")
    print(f"   Full Load: {result.get('full_load', {}).get('success', False)}")
    
    debezium = result.get('debezium_connector', {})
    print(f"   Debezium Connector: {debezium.get('name', 'Not created')}")
    print(f"   Debezium Status: {debezium.get('status', 'N/A')}")
    
    sink = result.get('sink_connector', {})
    print(f"   Sink Connector: {sink.get('name', 'Not created')}")
    print(f"   Sink Status: {sink.get('status', 'N/A')}")
    if sink.get('message'):
        print(f"   Sink Message: {sink.get('message')}")
    
    kafka_topics = result.get('kafka_topics', [])
    if kafka_topics:
        print(f"   Kafka Topics: {', '.join(kafka_topics)}")
    
    if result.get('message'):
        print(f"\n   Message: {result.get('message')}")
    
    print("\n" + "=" * 60)
    print("✅ CDC Pipeline Started!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Make changes to the department table in PostgreSQL")
    print("2. Changes will be captured in Kafka topics")
    print("3. To write to S3, you'll need to implement a consumer or use S3 sink")
else:
    print(f"   ❌ Failed: {start_response.status_code}")
    print(f"   Response: {start_response.text}")


import requests

API_URL = "http://localhost:8000/api"

print("=" * 60)
print("Start Existing CDC Pipeline")
print("=" * 60)

# Find the CDC pipeline
print("\n1. Finding CDC pipeline...")
response = requests.get(f"{API_URL}/pipelines")
if response.status_code != 200:
    print(f"❌ Error: {response.status_code}")
    exit(1)

pipelines = response.json()
cdc_pipeline = next((p for p in pipelines if 'CDC' in p.get('name', '') and p.get('mode') == 'full_load_and_cdc'), None)

if not cdc_pipeline:
    print("   ⚠️  CDC pipeline not found")
    print("   Available pipelines:")
    for p in pipelines:
        print(f"      - {p.get('name')} (mode: {p.get('mode')})")
    exit(1)

pipeline_id = cdc_pipeline.get('id')
print(f"   ✅ Found: {cdc_pipeline.get('name')}")
print(f"   ID: {pipeline_id}")
print(f"   Mode: {cdc_pipeline.get('mode')}")
print(f"   Status: {cdc_pipeline.get('status')}")

# Start the pipeline
print(f"\n2. Starting pipeline...")
start_response = requests.post(f"{API_URL}/pipelines/{pipeline_id}/start")

if start_response.status_code == 200:
    result = start_response.json()
    print(f"   ✅ Pipeline started!")
    print(f"   Status: {result.get('status')}")
    print(f"   Full Load: {result.get('full_load', {}).get('success', False)}")
    
    debezium = result.get('debezium_connector', {})
    print(f"   Debezium Connector: {debezium.get('name', 'Not created')}")
    print(f"   Debezium Status: {debezium.get('status', 'N/A')}")
    
    sink = result.get('sink_connector', {})
    print(f"   Sink Connector: {sink.get('name', 'Not created')}")
    print(f"   Sink Status: {sink.get('status', 'N/A')}")
    if sink.get('message'):
        print(f"   Sink Message: {sink.get('message')}")
    
    kafka_topics = result.get('kafka_topics', [])
    if kafka_topics:
        print(f"   Kafka Topics: {', '.join(kafka_topics)}")
    
    if result.get('message'):
        print(f"\n   Message: {result.get('message')}")
    
    print("\n" + "=" * 60)
    print("✅ CDC Pipeline Started!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Make changes to the department table in PostgreSQL")
    print("2. Changes will be captured in Kafka topics")
    print("3. To write to S3, you'll need to implement a consumer or use S3 sink")
else:
    print(f"   ❌ Failed: {start_response.status_code}")
    print(f"   Response: {start_response.text}")

