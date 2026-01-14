"""Check what Kafka broker address should be used."""
import requests

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

print("=== CHECKING KAFKA BROKER ADDRESS ===")

# Check working sink connector to see what it uses
SINK_CONNECTOR = "sink-oracle_sf_p-snow-public"
print(f"Checking working sink connector: {SINK_CONNECTOR}")

try:
    r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR}/config")
    sink_config = r.json()
    
    print(f"Sink connector config keys related to Kafka:")
    for key in sorted(sink_config.keys()):
        if 'kafka' in key.lower() or 'bootstrap' in key.lower() or 'broker' in key.lower():
            print(f"  {key}: {sink_config[key]}")
    
    # Check if sink connector has bootstrap servers
    sink_bootstrap = sink_config.get('bootstrap.servers') or sink_config.get('kafka.bootstrap.servers')
    print(f"\nSink connector bootstrap servers: {sink_bootstrap}")
    
    if not sink_bootstrap:
        print("⚠ Sink connector also doesn't have bootstrap.servers explicitly set")
        print("  It inherits from Kafka Connect worker configuration")
        print("  This means the worker config should have bootstrap.servers")
        
except Exception as e:
    print(f"Error: {e}")

# Check Debezium connector
print(f"\n=== CHECKING DEBEZIUM CONNECTOR ===")
DEBEZIUM_CONNECTOR = "cdc-oracle_sf_p-ora-cdc_user"

try:
    r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{DEBEZIUM_CONNECTOR}/config")
    dbz_config = r2.json()
    
    dbz_bootstrap = dbz_config.get('bootstrap.servers') or dbz_config.get('kafka.bootstrap.servers')
    print(f"Debezium connector bootstrap servers: {dbz_bootstrap}")
    
    schema_bootstrap = dbz_config.get('schema.history.internal.kafka.bootstrap.servers')
    print(f"Schema history bootstrap: {schema_bootstrap}")
    
    if dbz_bootstrap == "kafka:29092":
        print("\n⚠ Using 'kafka:29092' - this assumes Kafka is accessible as hostname 'kafka'")
        print("  If this doesn't work, try:")
        print("    1. Check if 'kafka' hostname resolves in Kafka Connect container")
        print("    2. Try using IP address: 72.61.233.209:9092 (external)")
        print("    3. Check Docker network configuration")
        
except Exception as e:
    print(f"Error: {e}")

print(f"\n=== RECOMMENDATION ===")
print(f"If 'kafka:29092' doesn't work, the issue might be:")
print(f"  1. Docker network - Kafka Connect and Kafka are not on the same network")
print(f"  2. Hostname resolution - 'kafka' hostname doesn't resolve")
print(f"  3. Port mismatch - Kafka might not be on port 29092")
print(f"\nTry using external address: 72.61.233.209:9092")
print(f"  (This works for sink connector, so it should work for Debezium too)")

