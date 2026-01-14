import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-cdc_user"

print("=== CHECKING CONNECTOR TOPIC USAGE ===")

# Get connector config
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config")
config = r.json()

print(f"Connector: {CONNECTOR_NAME}")
print(f"Database server name: {config.get('database.server.name')}")
print(f"Table include list: {config.get('table.include.list')}")

# Calculate expected topic name
schema = config.get('table.include.list', '').split('.')[0] if '.' in config.get('table.include.list', '') else ''
table = config.get('table.include.list', '').split('.')[1] if '.' in config.get('table.include.list', '') else ''
server = config.get('database.server.name', '')
expected_topic = f"{server}.{schema}.{table}"

print(f"\nExpected topic: {expected_topic}")

# Get connector status
r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
status = r2.json()

print(f"\nConnector State: {status.get('connector', {}).get('state')}")
print(f"Tasks: {len(status.get('tasks', []))}")

for i, task in enumerate(status.get('tasks', [])):
    print(f"\nTask {i}:")
    print(f"  State: {task.get('state')}")
    if task.get('trace'):
        print(f"  Error: {task.get('trace')[:500]}")

# Check if topic exists (via backend)
print(f"\n=== CHECKING TOPIC FROM BACKEND ===")
try:
    import requests as req
    r3 = req.get("http://localhost:8000/api/v1/pipelines/3b06bbae-2bbc-4526-ad6f-4e5d12c14f04")
    pipeline = r3.json()
    pipeline_topics = pipeline.get('kafka_topics', [])
    print(f"Pipeline topics: {pipeline_topics}")
    
    if expected_topic in pipeline_topics:
        print(f"✓ Expected topic '{expected_topic}' is in pipeline topics")
    else:
        print(f"⚠ Expected topic '{expected_topic}' NOT in pipeline topics")
        print(f"  Pipeline has: {pipeline_topics}")
        
except Exception as e:
    print(f"Error checking pipeline: {e}")

print(f"\n=== ISSUE ANALYSIS ===")
print(f"The connector should be creating/using topic: {expected_topic}")
print(f"If the connector is failing, it might not be able to create the topic")
print(f"Possible causes:")
print(f"  1. Kafka connectivity issue (Timeout expired while fetching topic metadata)")
print(f"  2. Topic already exists but connector can't access it")
print(f"  3. Kafka broker not accessible from Kafka Connect container")

