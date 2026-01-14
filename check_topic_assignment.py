"""Check if the Oracle connector is actually using the Kafka topic."""
import requests

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-cdc_user"
TOPIC_NAME = "oracle_sf_p.cdc_user.test"

print("=== CHECKING TOPIC ASSIGNMENT ===")

# Check connector config
r1 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config")
config = r1.json()

print(f"\n=== CONNECTOR CONFIGURATION ===")
print(f"Connector: {CONNECTOR_NAME}")
print(f"Database server name: {config.get('database.server.name')}")
print(f"Table include list: {config.get('table.include.list')}")
print(f"Schema history bootstrap: {config.get('schema.history.internal.kafka.bootstrap.servers')}")
print(f"Schema history topic: {config.get('schema.history.internal.kafka.topic')}")

# Expected topic based on config
db_server_name = config.get('database.server.name')
table_include = config.get('table.include.list', '')
if '.' in table_include:
    schema, table = table_include.split('.')
    expected_topic = f"{db_server_name}.{schema}.{table}"
    print(f"\nExpected topic: {expected_topic}")
    print(f"Actual topic: {TOPIC_NAME}")
    if expected_topic == TOPIC_NAME:
        print("✓ Topic name matches expected format")
    else:
        print("⚠ Topic name mismatch!")

# Check connector status
r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
status = r2.json()

print(f"\n=== CONNECTOR STATUS ===")
print(f"Connector state: {status.get('connector', {}).get('state')}")
tasks = status.get('tasks', [])

if tasks:
    for i, task in enumerate(tasks):
        task_state = task.get('state')
        task_id = task.get('id')
        print(f"\nTask {i} (ID: {task_id}):")
        print(f"  State: {task_state}")
        
        # Check if task has worker_id (means it's assigned)
        worker_id = task.get('worker_id')
        if worker_id:
            print(f"  Worker ID: {worker_id} (task is assigned)")
        else:
            print(f"  ⚠ No worker ID (task may not be assigned)")
        
        if task_state == 'FAILED':
            error = task.get('trace', 'Unknown error')
            print(f"  Error: {error[:600]}")

# Check if topic exists via Kafka Connect (if possible)
print(f"\n=== CHECKING KAFKA TOPICS ===")
try:
    # Try to get connector topics (some Kafka Connect versions support this)
    r3 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/topics")
    if r3.status_code == 200:
        topics = r3.json()
        print(f"Topics used by connector: {topics}")
        if TOPIC_NAME in topics.get('topics', []):
            print(f"✓ Topic {TOPIC_NAME} is assigned to connector")
        else:
            print(f"⚠ Topic {TOPIC_NAME} not in connector's topics list")
    else:
        print("Cannot query connector topics (API not available)")
except:
    print("Cannot query connector topics")

# Check connector info (might show topics)
try:
    r4 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}")
    if r4.status_code == 200:
        info = r4.json()
        print(f"\nConnector info:")
        if 'topics' in info:
            print(f"Topics: {info.get('topics')}")
except:
    pass

print(f"\n=== SUMMARY ===")
print(f"Expected topic: {TOPIC_NAME}")
print(f"Connector state: {status.get('connector', {}).get('state')}")
if tasks:
    print(f"Task state: {tasks[0].get('state')}")
    if tasks[0].get('state') == 'RUNNING':
        print("Connector is RUNNING but may not be consuming from topic yet")
        print("This could be normal if there are no changes to capture")

