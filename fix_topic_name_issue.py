"""
Fix the topic name issue by understanding Debezium's sanitization behavior.

According to Debezium documentation:
- Debezium automatically replaces invalid characters in topic names with underscores
- c##cdc_user should become c__cdc_user (double underscore, one for each #)
- But we're using c_cdc_user (single underscore)

The issue is that Debezium generates topic names internally and may fail
before sanitization happens if the topic name is invalid.

Solution: We need to ensure the topic name matches what Debezium expects.
"""

import requests
import re

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-c_cdc_user"

# Get current config
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config")
config = r.json()

schema = "c##cdc_user"  # Original schema name
table = "test"
pipeline_name = "oracle_sf_p"

# Debezium's sanitization: replaces each invalid char with underscore
# So c##cdc_user -> c__cdc_user (double underscore)
sanitized_by_debezium = re.sub(r'[^a-zA-Z0-9._-]', '_', schema)
print(f"Original schema: {schema}")
print(f"Debezium sanitized: {sanitized_by_debezium}")
print(f"Expected topic: {pipeline_name}.{sanitized_by_debezium}.{table}")
print(f"Current topic: {pipeline_name}.c_cdc_user.{table}")

# Our sanitization: replaces multiple consecutive underscores with single
our_sanitized = re.sub(r'_+', '_', sanitized_by_debezium)
print(f"Our sanitized: {our_sanitized}")
print(f"Our topic: {pipeline_name}.{our_sanitized}.{table}")

print(f"\n=== ISSUE ===")
print(f"Debezium expects: {pipeline_name}.{sanitized_by_debezium}.{table}")
print(f"We're using: {pipeline_name}.{our_sanitized}.{table}")
print(f"Mismatch! Debezium will try to create {pipeline_name}.{sanitized_by_debezium}.{table}")
print(f"But topic exists as {pipeline_name}.{our_sanitized}.{table}")

print(f"\n=== SOLUTION ===")
print(f"We need to use the same sanitization as Debezium:")
print(f"  - Don't collapse multiple underscores")
print(f"  - Replace each invalid char with a single underscore")
print(f"  - So c##cdc_user -> c__cdc_user (not c_cdc_user)")

