"""Check Kafka topics directly to see if the topic exists and has messages."""
import requests
import subprocess
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
TOPIC_NAME = "oracle_sf_p.cdc_user.test"

print("=== CHECKING KAFKA TOPICS ===")

# Check via Kafka Connect REST API (if available)
print(f"\n1. Checking via Kafka Connect REST API...")
try:
    # Some Kafka Connect versions have a topics endpoint
    r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/cdc-oracle_sf_p-ora-cdc_user/topics")
    if r.status_code == 200:
        topics_data = r.json()
        print(f"Topics: {topics_data}")
        if 'topics' in topics_data and TOPIC_NAME in topics_data['topics']:
            print(f"✓ Topic {TOPIC_NAME} exists")
        else:
            print(f"⚠ Topic {TOPIC_NAME} not found in connector topics")
    else:
        print(f"Topics API returned: {r.status_code}")
except Exception as e:
    print(f"Cannot query topics via API: {e}")

# Check connector config to see what it's configured for
print(f"\n2. Checking connector configuration...")
r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/cdc-oracle_sf_p-ora-cdc_user/config")
config = r2.json()
db_server_name = config.get('database.server.name')
table_include = config.get('table.include.list', '')

print(f"Database server name: {db_server_name}")
print(f"Table include list: {table_include}")

if '.' in table_include:
    schema, table = table_include.split('.')
    expected_topic = f"{db_server_name}.{schema}.{table}"
    print(f"Expected topic format: {db_server_name}.{schema}.{table}")
    print(f"Looking for: {TOPIC_NAME}")

# Check if we can query Kafka UI (if available on port 8080)
print(f"\n3. Checking if Kafka UI is available...")
try:
    r3 = requests.get("http://72.61.233.209:8080", timeout=2)
    if r3.status_code == 200:
        print("✓ Kafka UI is available at http://72.61.233.209:8080")
        print("You can check topics there manually")
except:
    print("Kafka UI not accessible or not running")

print(f"\n=== NOTES ===")
print(f"1. The connector generates topics based on: database.server.name + schema + table")
print(f"2. Topic name format: {db_server_name}.{{schema}}.{{table}}")
print(f"3. If the topic doesn't exist yet, Debezium will create it when it starts capturing changes")
print(f"4. The connector may be RUNNING but not actively producing to the topic if:")
print(f"   - There are no changes to capture")
print(f"   - Snapshot mode is 'never' (CDC only) and no changes have occurred yet")
print(f"   - Oracle LogMiner hasn't started yet")

# Check connector status for more details
print(f"\n4. Checking connector status details...")
r4 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/cdc-oracle_sf_p-ora-cdc_user/status")
status = r4.json()
tasks = status.get('tasks', [])

if tasks and tasks[0].get('state') == 'RUNNING':
    print("✓ Connector task is RUNNING")
    print("This is good - the connector is operational")
    print("If the topic doesn't exist yet, it will be created when Debezium starts capturing changes")

