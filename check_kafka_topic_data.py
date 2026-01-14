"""Check what data is actually in the Kafka topic."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
PIPELINE_NAME = "pg_to_mssql_projects_simple"
CONNECTOR_NAME = f"cdc-{PIPELINE_NAME}-pg-public"
EXPECTED_TOPIC = f"{PIPELINE_NAME}.public.projects_simple"

print("=" * 70)
print("CHECKING KAFKA TOPIC DATA")
print("=" * 70)

# Get connector config
print(f"\n1. Debezium Connector: {CONNECTOR_NAME}")
try:
    config = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config").json()
    table_include = config.get("table.include.list", "NOT SET")
    topic_prefix = config.get("topic.prefix", "NOT SET")
    
    print(f"   Table Include List: {table_include}")
    print(f"   Topic Prefix: {topic_prefix}")
    print(f"   Expected Topic: {EXPECTED_TOPIC}")
except Exception as e:
    print(f"   Error: {e}")

# Check connector status
print(f"\n2. Connector Status:")
try:
    status = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status").json()
    connector_state = status.get("connector", {}).get("state")
    print(f"   State: {connector_state}")
    
    tasks = status.get("tasks", [])
    for task in tasks:
        print(f"   Task {task.get('id')}: {task.get('state')}")
        if task.get('state') == 'FAILED':
            print(f"      Error: {task.get('trace', 'No trace')[:200]}")
except Exception as e:
    print(f"   Error: {e}")

print(f"\n3. To check actual Kafka topic data:")
print(f"   You need Kafka CLI tools or Kafka UI.")
print(f"   Expected topic: {EXPECTED_TOPIC}")
print(f"\n   If you see 'id', 'name', 'location' in the topic:")
print(f"   - The topic might be wrong (check topic name)")
print(f"   - The publication might include multiple tables")
print(f"   - The table.include.list might be incorrect")

print(f"\n4. Possible Issues:")
print(f"   - Publication includes ALL tables (puballtables=true)")
print(f"   - Wrong table in table.include.list")
print(f"   - Multiple topics being consumed")
print(f"   - Looking at wrong topic name")

print("\n" + "=" * 70)
print("RECOMMENDATION:")
print("=" * 70)
print("\n1. Verify the publication only includes projects_simple:")
print("   SELECT * FROM pg_publication_tables WHERE pubname = 'pg_to_mssql_projects_simple_pub';")
print("\n2. Check if publication includes all tables:")
print("   SELECT puballtables FROM pg_publication WHERE pubname = 'pg_to_mssql_projects_simple_pub';")
print("\n3. If publication includes all tables, recreate it with only projects_simple")
print("\n4. Verify the Kafka topic name matches the expected topic")


