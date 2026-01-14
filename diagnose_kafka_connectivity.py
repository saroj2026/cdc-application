"""Diagnose Kafka connectivity issue for Debezium connector."""
import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-cdc_user"

print("=== DIAGNOSING KAFKA CONNECTIVITY ===")

# Get connector config
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config")
config = r.json()

print("=== CONNECTOR CONFIGURATION ===")
print(f"Connector class: {config.get('connector.class')}")
print(f"Database server name: {config.get('database.server.name')}")
print(f"Table include list: {config.get('table.include.list')}")

# Check for Kafka bootstrap servers
print(f"\n=== KAFKA CONFIGURATION ===")
bootstrap_servers = config.get('bootstrap.servers') or config.get('kafka.bootstrap.servers')
print(f"Bootstrap servers: {bootstrap_servers}")

schema_bootstrap = config.get('schema.history.internal.kafka.bootstrap.servers')
print(f"Schema history bootstrap: {schema_bootstrap}")

# Check Kafka Connect worker configuration
print(f"\n=== KAFKA CONNECT WORKER CONFIG ===")
try:
    # Try to get worker configuration (if available)
    r2 = requests.get(f"{KAFKA_CONNECT_URL}/")
    print(f"Kafka Connect root: {r2.status_code}")
except Exception as e:
    print(f"Error: {e}")

# Compare with working sink connector
print(f"\n=== COMPARING WITH WORKING SINK CONNECTOR ===")
SINK_CONNECTOR = "sink-oracle_sf_p-snow-public"
try:
    r3 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR}/config")
    sink_config = r3.json()
    sink_bootstrap = sink_config.get('bootstrap.servers') or sink_config.get('kafka.bootstrap.servers')
    print(f"Sink connector bootstrap servers: {sink_bootstrap}")
    
    if sink_bootstrap and not bootstrap_servers:
        print(f"⚠ Debezium connector missing bootstrap servers!")
        print(f"  Sink connector has: {sink_bootstrap}")
        print(f"  Debezium connector has: {bootstrap_servers}")
        print(f"  This might be the issue!")
except Exception as e:
    print(f"Error checking sink connector: {e}")

print(f"\n=== ANALYSIS ===")
print(f"The error 'Timeout expired while fetching topic metadata' means:")
print(f"  - Debezium connector cannot reach Kafka brokers")
print(f"  - This happens when trying to create/access topics")
print(f"\nPossible causes:")
print(f"  1. Missing bootstrap.servers in connector config")
print(f"  2. Wrong bootstrap server address (should be kafka:29092 from inside container)")
print(f"  3. Network connectivity issue between Kafka Connect and Kafka")
print(f"  4. Kafka broker not accessible")

print(f"\n=== RECOMMENDATION ===")
if not bootstrap_servers:
    print(f"⚠ Debezium connector is missing bootstrap.servers configuration!")
    print(f"  Connectors typically inherit this from Kafka Connect worker config")
    print(f"  But Debezium might need it explicitly set")
    print(f"  Should be: kafka:29092 (Docker internal) or 72.61.233.209:9092 (external)")

