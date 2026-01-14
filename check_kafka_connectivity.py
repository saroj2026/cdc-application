"""Check Kafka connectivity from Kafka Connect perspective."""
import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
KAFKA_BROKER = "72.61.233.209:9092"  # External broker
KAFKA_INTERNAL = "kafka:29092"  # Internal Docker network

print("=== CHECKING KAFKA CONNECTIVITY ===")

# Check Kafka Connect is accessible
try:
    r = requests.get(f"{KAFKA_CONNECT_URL}/", timeout=5)
    print(f"✓ Kafka Connect is accessible: {KAFKA_CONNECT_URL}")
except Exception as e:
    print(f"✗ Kafka Connect not accessible: {e}")
    exit(1)

# Check connector config for bootstrap servers
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-cdc_user"
r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config")
config = r2.json()

print(f"\n=== CONNECTOR KAFKA CONFIG ===")
# Check for bootstrap servers in config
bootstrap_servers = config.get('bootstrap.servers') or config.get('kafka.bootstrap.servers')
print(f"Bootstrap servers in config: {bootstrap_servers}")

# Check schema history bootstrap servers
schema_bootstrap = config.get('schema.history.internal.kafka.bootstrap.servers')
print(f"Schema history bootstrap: {schema_bootstrap}")

print(f"\n=== EXPECTED CONFIGURATION ===")
print(f"Kafka Connect runs in Docker container")
print(f"From inside container, Kafka should be accessible as: kafka:29092")
print(f"External access: {KAFKA_BROKER}")
print(f"\nThe connector needs to connect to Kafka to:")
print(f"  1. Create/access topics")
print(f"  2. Store schema history")
print(f"  3. Store offsets")

print(f"\n=== ISSUE ===")
print(f"The error 'Timeout expired while fetching topic metadata' suggests:")
print(f"  - Kafka Connect container cannot reach Kafka brokers")
print(f"  - Bootstrap servers configuration might be wrong")
print(f"  - Network connectivity issue between containers")

# Check if we can list topics (if Kafka Connect exposes this)
try:
    # Some Kafka Connect setups expose a topics endpoint
    r3 = requests.get(f"{KAFKA_CONNECT_URL}/topics", timeout=5)
    topics = r3.json()
    print(f"\n✓ Can list topics via Kafka Connect: {len(topics)} topics")
    if 'oracle_sf_p.cdc_user.test' in topics:
        print(f"  ✓ Topic 'oracle_sf_p.cdc_user.test' exists!")
    else:
        print(f"  ⚠ Topic 'oracle_sf_p.cdc_user.test' NOT found in list")
        print(f"  Available topics (first 10): {topics[:10]}")
except Exception as e:
    print(f"\n⚠ Cannot list topics via Kafka Connect API: {e}")
    print(f"  (This is normal - Kafka Connect may not expose topics endpoint)")

