"""Check which Oracle user is configured in the connection."""
import psycopg2
import json

DATABASE_URL = "postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest"

print("=== CHECKING ORACLE CONNECTION USER ===")

# Connect to PostgreSQL to get Oracle connection details
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Find Oracle connection
cursor.execute("SELECT id, name, username, database, schema, additional_config FROM connections WHERE database_type = 'oracle'")
oracle_connections = cursor.fetchall()

if oracle_connections:
    for conn_id, name, username, database, schema, additional_config in oracle_connections:
        print(f"\nConnection: {name} (ID: {conn_id})")
        print(f"Username: {username}")
        print(f"Database: {database}")
        print(f"Schema: {schema}")
        if additional_config:
            try:
                config = json.loads(additional_config) if isinstance(additional_config, str) else additional_config
                print(f"Additional config: {config}")
            except:
                print(f"Additional config: {additional_config}")
else:
    print("No Oracle connections found")

cursor.close()
conn.close()

# Also check what the connector is actually using
print(f"\n=== CHECKING CONNECTOR CONFIGURATION ===")
import requests
KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/cdc-oracle_sf_p-ora-cdc_user/config")
config = r.json()

print(f"Connector database user: {config.get('database.user')}")
print(f"Connector database dbname: {config.get('database.dbname')}")
print(f"Connector table include list: {config.get('table.include.list')}")

