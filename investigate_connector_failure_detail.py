"""Investigate why Debezium connector is failing after removing bootstrap.servers."""
import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
DEBEZIUM_CONNECTOR = "cdc-oracle_sf_p-ora-cdc_user"
SINK_CONNECTOR = "sink-oracle_sf_p-snow-public"

print("=== DETAILED FAILURE INVESTIGATION ===")

# Get Debezium connector status with full error
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{DEBEZIUM_CONNECTOR}/status")
dbz_status = r.json()

print(f"\n1. DEBEZIUM CONNECTOR STATUS:")
print(f"   Connector state: {dbz_status.get('connector', {}).get('state')}")
tasks = dbz_status.get('tasks', [])
print(f"   Number of tasks: {len(tasks)}")

if tasks:
    task = tasks[0]
    print(f"\n   Task 0:")
    print(f"     State: {task.get('state')}")
    print(f"     ID: {task.get('id')}")
    if task.get('trace'):
        trace = task.get('trace')
        print(f"\n     Full Error Trace:")
        print(f"     {trace[:1000]}")
        
        # Check for specific error patterns
        if "bootstrap.servers" in trace.lower():
            print(f"\n     ⚠ Error mentions bootstrap.servers")
        if "kafka:29092" in trace:
            print(f"     ⚠ Error mentions kafka:29092")
        if "timeout" in trace.lower():
            print(f"     ⚠ Error is a timeout")

# Get connector configs
print(f"\n2. CONFIGURATION COMPARISON:")

r1 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{DEBEZIUM_CONNECTOR}/config")
dbz_config = r1.json()

r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR}/config")
sink_config = r2.json()

print(f"\n   Debezium Connector:")
print(f"     bootstrap.servers: {dbz_config.get('bootstrap.servers')}")
print(f"     schema.history.internal.kafka.bootstrap.servers: {dbz_config.get('schema.history.internal.kafka.bootstrap.servers')}")
print(f"     database.server.name: {dbz_config.get('database.server.name')}")
print(f"     table.include.list: {dbz_config.get('table.include.list')}")

print(f"\n   Sink Connector:")
print(f"     bootstrap.servers: {sink_config.get('bootstrap.servers')}")
print(f"     topics: {sink_config.get('topics')}")

# Check if schema history bootstrap servers is the issue
print(f"\n3. SCHEMA HISTORY BOOTSTRAP SERVERS:")
schema_history_bs = dbz_config.get('schema.history.internal.kafka.bootstrap.servers')
print(f"   Debezium uses: {schema_history_bs}")
print(f"   This is used for schema history storage")

# Check if we need to check working PostgreSQL connector for comparison
print(f"\n4. CHECKING WORKING POSTGRESQL CONNECTOR:")
r3 = requests.get(f"{KAFKA_CONNECT_URL}/connectors")
connectors = r3.json()
pg_connectors = [c for c in connectors if c.startswith('cdc-') and 'pg-' in c]
if pg_connectors:
    pg_conn = pg_connectors[0]
    print(f"   Found PostgreSQL connector: {pg_conn}")
    r4 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{pg_conn}/config")
    pg_config = r4.json()
    print(f"     bootstrap.servers: {pg_config.get('bootstrap.servers')}")
    print(f"     schema.history.internal.kafka.bootstrap.servers: {pg_config.get('schema.history.internal.kafka.bootstrap.servers')}")
    
    r5 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{pg_conn}/status")
    pg_status = r5.json()
    print(f"     State: {pg_status.get('connector', {}).get('state')}")
    if pg_status.get('tasks'):
        print(f"     Task 0 state: {pg_status['tasks'][0].get('state')}")

