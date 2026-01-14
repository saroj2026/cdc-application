"""Check what bootstrap servers the Kafka Connect worker is using."""
import requests

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

print("=== KAFKA CONNECT WORKER INFO ===")

# Get worker info
r = requests.get(f"{KAFKA_CONNECT_URL}/")
if r.status_code == 200:
    info = r.json()
    print(f"Version: {info.get('version')}")
    print(f"Kafka Cluster ID: {info.get('kafka_cluster_id')}")

# Check sink connector (working) - it inherits from worker
print(f"\n=== SINK CONNECTOR (WORKING) ===")
sink_conn = "sink-oracle_sf_p-snow-public"
r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{sink_conn}/config")
sink_config = r2.json()
print(f"Sink connector bootstrap.servers: {sink_config.get('bootstrap.servers')}")
print(f"(Sink connector inherits from worker - this shows worker's bootstrap.servers)")

# Check Oracle connector
print(f"\n=== ORACLE CONNECTOR ===")
ora_conn = "cdc-oracle_sf_p-ora-cdc_user"
r3 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{ora_conn}/config")
ora_config = r3.json()
print(f"Oracle connector bootstrap.servers: {ora_config.get('bootstrap.servers')}")
print(f"Oracle connector schema.history bootstrap: {ora_config.get('schema.history.internal.kafka.bootstrap.servers')}")

# Check connector status
r4 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{ora_conn}/status")
ora_status = r4.json()
tasks = ora_status.get('tasks', [])
if tasks:
    print(f"\nOracle connector task state: {tasks[0].get('state')}")
    if tasks[0].get('trace'):
        print(f"Error: {tasks[0].get('trace')[:400]}")

print(f"\n=== ANALYSIS ===")
print(f"The worker's CONNECT_BOOTSTRAP_SERVERS environment variable determines")
print(f"what bootstrap.servers connectors inherit.")
print(f"If the worker is using 'kafka:29092' but the container is 'kafka-cdc',")
print(f"the worker itself cannot connect to Kafka, which would cause this error.")

