import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-c_cdc_user"

print("=== DEBEZIUM CONNECTOR STATUS ===")
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
status = r.json()
print(f"State: {status.get('connector', {}).get('state')}")
print(f"Tasks: {len(status.get('tasks', []))}")
if status.get('tasks'):
    task = status['tasks'][0]
    print(f"Task State: {task.get('state')}")
    print(f"Task Worker: {task.get('worker_id')}")
    if task.get('trace'):
        print(f"\nError Trace:")
        print(task.get('trace'))

print("\n=== DEBEZIUM CONNECTOR CONFIG ===")
r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config")
config = r2.json()
print(f"Database server name: {config.get('database.server.name')}")
print(f"Topic prefix: {config.get('topic.prefix')}")
print(f"Table include list: {config.get('table.include.list')}")
print(f"Schema name in table.include.list: {config.get('table.include.list', '').split('.')[0] if '.' in config.get('table.include.list', '') else 'N/A'}")

print("\n=== CHECKING KAFKA TOPICS ===")
# Check what topics exist
try:
    # Try to list topics via Kafka Connect (if it supports it)
    # Or check via our backend
    import requests as req
    r3 = req.get("http://localhost:8000/api/v1/pipelines/3b06bbae-2bbc-4526-ad6f-4e5d12c14f04")
    pipeline = r3.json()
    print(f"Pipeline topics: {pipeline.get('kafka_topics', [])}")
    
    # Expected topic name from Debezium (based on schema name)
    # Debezium generates: {database.server.name}.{schema}.{table}
    # Schema is: c##cdc_user (from table.include.list)
    # So Debezium will try: oracle_sf_p.c##cdc_user.test (INVALID!)
    expected_invalid = "oracle_sf_p.c##cdc_user.test"
    expected_sanitized = "oracle_sf_p.c_cdc_user.test"
    print(f"\nExpected topic (invalid): {expected_invalid}")
    print(f"Expected topic (sanitized): {expected_sanitized}")
    print(f"Pipeline uses: {pipeline.get('kafka_topics', [])}")
except Exception as e:
    print(f"Error checking pipeline: {e}")

