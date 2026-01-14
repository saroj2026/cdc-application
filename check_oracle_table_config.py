#!/usr/bin/env python3
"""Check Oracle table configuration vs actual topic names."""

import requests

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
SOURCE_CONNECTOR = "cdc-oracle_sf_p-ora-cdc_user"

print("=" * 70)
print("CHECKING ORACLE CONFIGURATION VS TOPIC NAMES")
print("=" * 70)

# Get connector config
print("\n1. Source Connector Configuration:")
try:
    r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{SOURCE_CONNECTOR}/config")
    if r.status_code == 200:
        config = r.json()
        db_server_name = config.get('database.server.name')
        table_include_list = config.get('table.include.list')
        
        print(f"   Database server name: {db_server_name}")
        print(f"   Table include list: {table_include_list}")
        
        # Expected topic name based on config
        # Format: {database.server.name}.{schema}.{table}
        # Oracle creates UPPERCASE schema/table names in topics
        if table_include_list:
            parts = table_include_list.split('.')
            if len(parts) == 2:
                schema = parts[0].upper()  # Oracle uppercases schema
                table = parts[1].upper()   # Oracle uppercases table
                expected_topic = f"{db_server_name}.{schema}.{table}"
                print(f"\n   Expected topic (Oracle creates UPPERCASE):")
                print(f"     {expected_topic}")
                
                # Also show what lowercase would be
                schema_lower = parts[0].lower()
                table_lower = parts[1].lower()
                lowercase_topic = f"{db_server_name}.{schema_lower}.{table_lower}"
                print(f"\n   If lowercase (wrong):")
                print(f"     {lowercase_topic}")
    else:
        print(f"   Error: {r.status_code} - {r.text}")
except Exception as e:
    print(f"   Error: {e}")

# Check actual topics
print("\n2. Actual Kafka Topics:")
try:
    r = requests.get("http://72.61.233.209:8080/api/clusters/local/topics")
    if r.status_code == 200:
        topics = r.json()
        oracle_topics = [t for t in topics if 'oracle_sf_p' in t]
        
        print(f"   Oracle-related topics found:")
        for topic in sorted(oracle_topics):
            # Check if uppercase or lowercase
            if 'CDC_USER' in topic:
                print(f"     ✓ {topic} (UPPERCASE - correct)")
            elif 'cdc_user' in topic:
                print(f"     ⚠ {topic} (lowercase - wrong)")
            else:
                print(f"     - {topic}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 70)
print("ANALYSIS:")
print("=" * 70)
print("  Oracle Debezium connector creates topics with UPPERCASE schema/table names")
print("  If table.include.list = 'cdc_user.test' (lowercase)")
print("  Oracle will create topic: 'oracle_sf_p.CDC_USER.TEST' (UPPERCASE)")
print("  This is CORRECT behavior - Oracle uppercases identifiers in topic names")
print("=" * 70)

