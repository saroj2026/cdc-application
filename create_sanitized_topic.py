import requests
import json

# Kafka Admin API endpoint (if available) or use Kafka Connect
# Actually, we need to create the topic via Kafka directly
# For now, let's check if we can use Kafka Connect's topic creation

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
KAFKA_UI_URL = "http://72.61.233.209:8080"

# The topic that Debezium is trying to create (invalid)
invalid_topic = "oracle_sf_p.c##cdc_user.test"
# The topic we want (sanitized)
sanitized_topic = "oracle_sf_p.c_cdc_user.test"

print(f"=== TOPIC NAME ISSUE ===")
print(f"Debezium trying to create: {invalid_topic} (INVALID - contains ##)")
print(f"Topic we need: {sanitized_topic} (VALID)")
print(f"\nProblem: Debezium generates topic names from schema name in table.include.list")
print(f"Schema name: c##cdc_user (from Oracle)")
print(f"Debezium will create: oracle_sf_p.c##cdc_user.test (INVALID!)")
print(f"\nSolution needed: Pre-create topic or use topic routing")

# Check if topic exists
print(f"\n=== CHECKING TOPICS ===")
try:
    # Try to get topic info from Kafka UI API (if available)
    # Or check via our backend
    r = requests.get(f"http://localhost:8000/api/v1/pipelines/3b06bbae-2bbc-4526-ad6f-4e5d12c14f04")
    pipeline = r.json()
    print(f"Pipeline topics: {pipeline.get('kafka_topics', [])}")
    if sanitized_topic in pipeline.get('kafka_topics', []):
        print(f"✓ Sanitized topic exists: {sanitized_topic}")
    else:
        print(f"✗ Sanitized topic not found in pipeline")
except Exception as e:
    print(f"Error: {e}")

