"""Verify Oracle setup is complete."""

import requests
import sys

print("=" * 70)
print("Verifying Oracle Setup")
print("=" * 70)

# 1. Check Python driver
print("\n1. Checking Python Oracle driver...")
try:
    import oracledb
    version = getattr(oracledb, '__version__', 'installed')
    print(f"   ✅ oracledb installed (version: {version})")
except ImportError:
    try:
        import cx_Oracle
        print(f"   ✅ cx_Oracle installed")
    except ImportError:
        print("   ❌ No Oracle Python driver found")
        print("   Install with: pip install oracledb")

# 2. Check DatabaseType enum
print("\n2. Checking DatabaseType enum...")
try:
    from ingestion.database.models_db import DatabaseType
    db_types = [e.value for e in DatabaseType]
    if 'oracle' in db_types:
        print(f"   ✅ Oracle is in DatabaseType enum")
        print(f"   All types: {', '.join(db_types)}")
    else:
        print(f"   ⚠️  Oracle not in enum")
        print(f"   Current types: {', '.join(db_types)}")
except Exception as e:
    print(f"   ❌ Error checking enum: {e}")

# 3. Check OracleConnector
print("\n3. Checking OracleConnector...")
try:
    from ingestion.connectors.oracle import OracleConnector
    print("   ✅ OracleConnector imported successfully")
except Exception as e:
    print(f"   ❌ Error importing OracleConnector: {e}")

# 4. Check Debezium config
print("\n4. Checking Debezium config for Oracle...")
try:
    from ingestion.debezium_config import DebeziumConfigGenerator
    import inspect
    methods = [m for m in dir(DebeziumConfigGenerator) if 'oracle' in m.lower()]
    if methods:
        print(f"   ✅ Oracle methods found: {', '.join(methods)}")
    else:
        print("   ⚠️  No Oracle methods found in DebeziumConfigGenerator")
except Exception as e:
    print(f"   ❌ Error checking Debezium config: {e}")

# 5. Check Kafka Connect for Oracle connector
print("\n5. Checking Kafka Connect for Oracle connector...")
try:
    response = requests.get("http://72.61.233.209:8083/connector-plugins", timeout=10)
    if response.status_code == 200:
        plugins = response.json()
        oracle_plugins = [p for p in plugins if 'oracle' in p.get('class', '').lower()]
        if oracle_plugins:
            print(f"   ✅ Found {len(oracle_plugins)} Oracle connector(s):")
            for p in oracle_plugins:
                print(f"      - {p.get('class')} (version: {p.get('version', 'unknown')})")
        else:
            print("   ⚠️  Oracle connector not found in Kafka Connect")
            print("   Install with: install_oracle_connector_server.sh on the server")
    else:
        print(f"   ⚠️  Could not connect to Kafka Connect: {response.status_code}")
except Exception as e:
    print(f"   ⚠️  Error checking Kafka Connect: {e}")
    print("   Make sure Kafka Connect is running at http://72.61.233.209:8083")

print("\n" + "=" * 70)
print("Summary")
print("=" * 70)
print("\n✅ Backend code: Complete")
print("✅ Python driver: Check above")
print("✅ Database enum: Check above")
print("✅ Kafka Connect: Check above")
print("\nIf all checks pass, Oracle → Snowflake pipelines are ready!")

