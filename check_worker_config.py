"""Check Kafka Connect worker configuration to understand bootstrap servers."""
import requests

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

print("=== KAFKA CONNECT WORKER CONFIGURATION ===")

# Get worker configuration
r = requests.get(f"{KAFKA_CONNECT_URL}/")
if r.status_code == 200:
    info = r.json()
    print(f"Version: {info.get('version')}")
    print(f"Commit: {info.get('commit')}")
    print(f"Kafka Cluster ID: {info.get('kafka_cluster_id')}")

# Compare sink connector (working) vs Debezium connector (failing)
print(f"\n=== COMPARING CONNECTOR CONFIGS ===")

# Sink connector (working)
sink_conn = "sink-oracle_sf_p-snow-public"
r1 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{sink_conn}/config")
sink_config = r1.json()
print(f"\nSink Connector ({sink_conn}):")
print(f"  Has bootstrap.servers: {sink_config.get('bootstrap.servers') is not None}")
print(f"  Bootstrap servers: {sink_config.get('bootstrap.servers')}")

# Debezium connector (failing)
dbz_conn = "cdc-oracle_sf_p-ora-cdc_user"
r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{dbz_conn}/config")
dbz_config = r2.json()
print(f"\nDebezium Connector ({dbz_conn}):")
print(f"  Has bootstrap.servers: {dbz_config.get('bootstrap.servers') is not None}")
print(f"  Bootstrap servers: {dbz_config.get('bootstrap.servers')}")
print(f"  Schema history bootstrap: {dbz_config.get('schema.history.internal.kafka.bootstrap.servers')}")

# Check if there are other differences
print(f"\n=== KEY DIFFERENCES ===")
if sink_config.get('bootstrap.servers') != dbz_config.get('bootstrap.servers'):
    print(f"⚠ Different bootstrap.servers:")
    print(f"  Sink: {sink_config.get('bootstrap.servers')}")
    print(f"  Debezium: {dbz_config.get('bootstrap.servers')}")
else:
    print(f"✓ bootstrap.servers matches (both inherit from worker)")

print(f"\nBoth connectors should inherit bootstrap.servers from worker configuration")
print(f"Worker config is set via CONNECT_BOOTSTRAP_SERVERS environment variable")

