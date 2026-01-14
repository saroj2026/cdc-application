"""Delete old duplicate topics that are no longer needed."""
import requests
import json

KAFKA_UI_URL = "http://72.61.233.209:8080"
KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

# Old topics to delete (from old schema)
OLD_TOPICS = [
    "oracle_sf_p.c_cdc_user.test",  # From old schema c##cdc_user (sanitized to c__cdc_user)
]

# Current topic (should be kept)
CURRENT_TOPIC = "oracle_sf_p.cdc_user.test"

print("=== DELETING OLD DUPLICATE TOPICS ===")
print(f"Topics to delete: {OLD_TOPICS}")
print(f"Topic to keep: {CURRENT_TOPIC}")

# Note: Kafka UI doesn't provide a direct API to delete topics
# Topics are usually deleted via Kafka Admin API or Kafka tools
# For now, we'll document which topics should be deleted

print("\n⚠ Note: Kafka topics cannot be deleted via Kafka Connect REST API")
print("Topics need to be deleted using:")
print("  1. Kafka Admin API")
print("  2. kafka-topics.sh command")
print("  3. Kafka UI (if it has delete functionality)")

print(f"\n=== TOPICS TO DELETE ===")
for topic in OLD_TOPICS:
    print(f"  - {topic}")
    print(f"    Reason: Old schema name (c##cdc_user -> c__cdc_user)")
    print(f"    Replaced by: {CURRENT_TOPIC}")

print(f"\n=== TOPIC TO KEEP ===")
print(f"  - {CURRENT_TOPIC}")
print(f"    Reason: Current schema name (cdc_user)")

print(f"\n=== MANUAL DELETION INSTRUCTIONS ===")
print("To delete old topics, you can:")
print("1. Use Kafka UI: Select the topics and click 'Delete selected topics'")
print("2. Use kafka-topics.sh:")
for topic in OLD_TOPICS:
    print(f"   kafka-topics.sh --delete --topic {topic} --bootstrap-server 72.61.233.209:9092")
print("3. Use Kafka Admin API (programmatically)")

# Check if we can access Kafka Admin API via Kafka Connect
print(f"\n=== CHECKING IF TOPICS CAN BE DELETED ===")
print("Checking connector status to ensure it's not using old topics...")

CONNECTOR_NAME = "cdc-oracle_sf_p-ora-cdc_user"
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config")
config = r.json()
schema = config.get('table.include.list', '').split('.')[0] if '.' in config.get('table.include.list', '') else ''
table = config.get('table.include.list', '').split('.')[1] if '.' in config.get('table.include.list', '') else ''
server = config.get('database.server.name', '')
expected_topic = f"{server}.{schema}.{table}"

print(f"Connector is using topic: {expected_topic}")
if expected_topic == CURRENT_TOPIC:
    print("✓ Connector is using the correct topic - safe to delete old topics")
else:
    print(f"⚠ Connector is using {expected_topic} - check before deleting")

