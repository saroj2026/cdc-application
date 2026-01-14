import requests
import json

KAFKA_UI_URL = "http://72.61.233.209:8080"
KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

print("=== CHECKING KAFKA TOPICS ===")
# Try to get topics from Kafka UI API or check what topics exist
# The topic that Debezium is trying to create: oracle_sf_p.c##cdc_user.test (INVALID)
# The topic that exists: oracle_sf_p.c_cdc_user.test (SANITIZED)

# Check connector status to see what it's trying to do
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-c_cdc_user"
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
status = r.json()

print(f"Connector State: {status.get('connector', {}).get('state')}")
print(f"Tasks: {len(status.get('tasks', []))}")
if status.get('tasks'):
    task = status['tasks'][0]
    print(f"Task State: {task.get('state')}")
    if task.get('trace'):
        print(f"Task Error: {task.get('trace')[:500]}")

# Check what topic Debezium is trying to use
# Debezium generates: {database.server.name}.{schema}.{table}
# From config: database.server.name = oracle_sf_p, schema = c##cdc_user, table = test
# Expected: oracle_sf_p.c##cdc_user.test (INVALID!)

print(f"\n=== TOPIC NAME ANALYSIS ===")
print(f"Debezium will try to create: oracle_sf_p.c##cdc_user.test (INVALID - contains ##)")
print(f"Topic that exists: oracle_sf_p.c_cdc_user.test (SANITIZED)")
print(f"\nProblem: Debezium generates topic names from schema in table.include.list")
print(f"Schema in table.include.list: c##cdc_user (actual Oracle schema)")
print(f"Debezium doesn't sanitize topic names before trying to create them")
print(f"\nSolution: Need to pre-create topic OR configure Debezium to use sanitized schema name")
