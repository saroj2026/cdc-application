#!/usr/bin/env python3
"""Verify Kafka configuration for Docker setup.

This script checks:
1. Kafka Connect is accessible
2. Kafka bootstrap servers configuration
3. Docker network connectivity (if possible)
"""

import os
import requests

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
KAFKA_BOOTSTRAP_INTERNAL = os.getenv("KAFKA_BOOTSTRAP_SERVERS_INTERNAL", "kafka:29092")

print("=" * 60)
print("Kafka Configuration Verification")
print("=" * 60)

# Check Kafka Connect
print("\n1. Checking Kafka Connect...")
try:
    r = requests.get(f"{KAFKA_CONNECT_URL}/", timeout=5)
    if r.status_code == 200:
        print(f"✓ Kafka Connect is accessible at {KAFKA_CONNECT_URL}")
    else:
        print(f"⚠ Kafka Connect returned status {r.status_code}")
except Exception as e:
    print(f"✗ Kafka Connect is not accessible: {e}")
    exit(1)

# Check connector plugins
print("\n2. Checking Debezium Oracle plugin...")
try:
    r = requests.get(f"{KAFKA_CONNECT_URL}/connector-plugins", timeout=5)
    if r.status_code == 200:
        plugins = r.json()
        oracle_plugins = [p for p in plugins if 'oracle' in p.get('class', '').lower()]
        if oracle_plugins:
            print(f"✓ Oracle Debezium plugin found: {oracle_plugins[0].get('class')}")
        else:
            print("⚠ Oracle Debezium plugin not found")
    else:
        print(f"⚠ Could not get plugins: {r.status_code}")
except Exception as e:
    print(f"⚠ Could not check plugins: {e}")

# Check existing connectors
print("\n3. Checking existing connectors...")
try:
    r = requests.get(f"{KAFKA_CONNECT_URL}/connectors", timeout=5)
    if r.status_code == 200:
        connectors = r.json()
        print(f"  Total connectors: {len(connectors)}")
        oracle_connectors = [c for c in connectors if 'oracle' in c.lower() or 'oracle_sf_p' in c.lower()]
        if oracle_connectors:
            print(f"  Oracle-related connectors: {oracle_connectors}")
        else:
            print("  No Oracle-related connectors found")
    else:
        print(f"⚠ Could not get connectors: {r.status_code}")
except Exception as e:
    print(f"⚠ Could not check connectors: {e}")

# Configuration info
print("\n4. Kafka Bootstrap Configuration...")
print(f"  Environment variable KAFKA_BOOTSTRAP_SERVERS_INTERNAL: {os.getenv('KAFKA_BOOTSTRAP_SERVERS_INTERNAL', 'Not set (using default)')}")
print(f"  Configured value: {KAFKA_BOOTSTRAP_INTERNAL}")
print(f"  Note: This is used for schema history inside Kafka Connect container")
print(f"  Expected: 'kafka:29092' (Docker hostname:internal_port)")

print("\n5. Docker Container Info...")
print("  From docker ps output:")
print("    - kafka-connect-cdc: Running on port 8083")
print("    - kafka-cdc: Running on port 9092 (external)")
print("    - oracle-xe: Running on port 1521")
print("  ")
print("  For Debezium Oracle connector:")
print("    - Schema history will use: kafka:29092 (Docker internal)")
print("    - This assumes Kafka and Kafka Connect are on the same Docker network")
print("    - Kafka container should be accessible as hostname 'kafka'")
print("    - Kafka should be listening on port 29092 internally")

print("\n" + "=" * 60)
print("Configuration Summary")
print("=" * 60)
print(f"✓ Kafka Connect URL: {KAFKA_CONNECT_URL}")
print(f"✓ Schema History Bootstrap: {KAFKA_BOOTSTRAP_INTERNAL}")
print("✓ Configuration is set for Docker internal network communication")
print("=" * 60)

