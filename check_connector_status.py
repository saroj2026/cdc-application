import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
PIPELINE_ID = "3b06bbae-2bbc-4526-ad6f-4e5d12c14f04"

# Get all connectors
print("=== ALL CONNECTORS ===")
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors")
connectors = r.json()
print(f"Total connectors: {len(connectors)}")

# Find Oracle connectors
oracle_conns = [c for c in connectors if 'oracle' in c.lower()]
print(f"\nOracle connectors: {oracle_conns}")

# Check each Oracle connector
for conn_name in oracle_conns:
    print(f"\n=== CONNECTOR: {conn_name} ===")
    try:
        # Get status
        r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{conn_name}/status")
        status = r2.json()
        print(f"State: {status.get('connector', {}).get('state')}")
        print(f"Tasks: {len(status.get('tasks', []))}")
        if status.get('tasks'):
            print(f"Task State: {status['tasks'][0].get('state')}")
        
        # Get config
        r3 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{conn_name}/config")
        config = r3.json()
        print(f"Snapshot mode: {config.get('snapshot.mode')}")
        print(f"Connection adapter: {config.get('database.connection.adapter')}")
    except Exception as e:
        print(f"Error: {e}")

# Check pipeline status
print(f"\n=== PIPELINE STATUS ===")
r4 = requests.get(f"http://localhost:8000/api/v1/pipelines/{PIPELINE_ID}")
pipeline = r4.json()
print(f"Status: {pipeline.get('status')}")
print(f"CDC Status: {pipeline.get('cdc_status')}")
print(f"Debezium Connector: {pipeline.get('debezium_connector_name')}")
print(f"Sink Connector: {pipeline.get('sink_connector_name')}")
print(f"Kafka Topics: {pipeline.get('kafka_topics', [])}")
