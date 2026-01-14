"""Investigate what changed and why Debezium connector is failing."""
import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
DEBEZIUM_CONNECTOR = "cdc-oracle_sf_p-ora-cdc_user"
SINK_CONNECTOR = "sink-oracle_sf_p-snow-public"

print("=== INVESTIGATING DEBEZIUM CONNECTOR FAILURE ===")

# Get Debezium connector config
print(f"\n1. DEBEZIUM CONNECTOR CONFIG:")
r1 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{DEBEZIUM_CONNECTOR}/config")
dbz_config = r1.json()

print(f"   Bootstrap servers: {dbz_config.get('bootstrap.servers')}")
print(f"   Schema history bootstrap: {dbz_config.get('schema.history.internal.kafka.bootstrap.servers')}")
print(f"   Database server name: {dbz_config.get('database.server.name')}")
print(f"   Table include list: {dbz_config.get('table.include.list')}")

# Get Sink connector config (working)
print(f"\n2. SINK CONNECTOR CONFIG (WORKING):")
r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR}/config")
sink_config = r2.json()

print(f"   Bootstrap servers: {sink_config.get('bootstrap.servers')}")
print(f"   Topics: {sink_config.get('topics')}")

# Compare
print(f"\n3. COMPARISON:")
print(f"   Debezium has bootstrap.servers: {dbz_config.get('bootstrap.servers') is not None}")
print(f"   Sink has bootstrap.servers: {sink_config.get('bootstrap.servers') is not None}")
print(f"   Debezium bootstrap: {dbz_config.get('bootstrap.servers')}")
print(f"   Sink bootstrap: {sink_config.get('bootstrap.servers')}")

# Check connector statuses
print(f"\n4. CONNECTOR STATUSES:")
r3 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{DEBEZIUM_CONNECTOR}/status")
dbz_status = r3.json()
print(f"   Debezium state: {dbz_status.get('connector', {}).get('state')}")
print(f"   Debezium tasks: {len(dbz_status.get('tasks', []))}")
if dbz_status.get('tasks'):
    print(f"   Debezium task state: {dbz_status['tasks'][0].get('state')}")
    if dbz_status['tasks'][0].get('trace'):
        print(f"   Debezium error: {dbz_status['tasks'][0].get('trace')[:400]}")

r4 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR}/status")
sink_status = r4.json()
print(f"   Sink state: {sink_status.get('connector', {}).get('state')}")
print(f"   Sink tasks: {len(sink_status.get('tasks', []))}")
if sink_status.get('tasks'):
    print(f"   Sink task state: {sink_status['tasks'][0].get('state')}")

print(f"\n5. ANALYSIS:")
print(f"   The sink connector works WITHOUT explicit bootstrap.servers")
print(f"   It inherits from Kafka Connect worker configuration")
print(f"   Debezium connector has bootstrap.servers={dbz_config.get('bootstrap.servers')}")
print(f"   If this address is wrong (e.g., 'kafka:29092' not resolving), it will fail")

print(f"\n6. POTENTIAL ISSUE:")
if dbz_config.get('bootstrap.servers') == 'kafka:29092':
    print(f"   ⚠ Using 'kafka:29092' - this might not resolve from Kafka Connect container")
    print(f"   The hostname 'kafka' might not be in /etc/hosts or Docker network")
    print(f"   Solution: Remove bootstrap.servers or use external address")
elif dbz_config.get('bootstrap.servers'):
    print(f"   Using: {dbz_config.get('bootstrap.servers')}")
    print(f"   Check if this address is accessible from Kafka Connect container")
else:
    print(f"   No bootstrap.servers set (inherits from worker)")

