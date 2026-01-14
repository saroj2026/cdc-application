"""Check connectors via Kafka Connect API (simulating Kafka UI check)."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
KAFKA_UI_URL = "http://72.61.233.209:8080"

print("=" * 70)
print("Kafka Connect Connectors Check")
print("=" * 70)

try:
    # List all connectors
    print("\n1. All Connectors:")
    response = requests.get(f"{KAFKA_CONNECT_URL}/connectors", timeout=10)
    
    if response.status_code == 200:
        connectors = response.json()
        print(f"   Found {len(connectors)} connectors:")
        for conn_name in connectors:
            print(f"      - {conn_name}")
    else:
        print(f"   Error: {response.status_code} - {response.text}")
        connectors = []
    
    # Check Debezium connectors
    print("\n2. Debezium Connectors:")
    debezium_connectors = [c for c in connectors if c.startswith("cdc-")]
    if debezium_connectors:
        for conn_name in debezium_connectors:
            print(f"\n   {conn_name}:")
            try:
                # Get status
                status_response = requests.get(
                    f"{KAFKA_CONNECT_URL}/connectors/{conn_name}/status",
                    timeout=10
                )
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"      State: {status.get('connector', {}).get('state', 'N/A')}")
                    print(f"      Worker: {status.get('connector', {}).get('worker_id', 'N/A')}")
                    
                    tasks = status.get('tasks', [])
                    print(f"      Tasks: {len(tasks)}")
                    for task in tasks:
                        print(f"         Task {task.get('id')}: {task.get('state', 'N/A')}")
                else:
                    print(f"      Status Error: {status_response.status_code}")
                
                # Get config
                config_response = requests.get(
                    f"{KAFKA_CONNECT_URL}/connectors/{conn_name}/config",
                    timeout=10
                )
                if config_response.status_code == 200:
                    config = config_response.json()
                    print(f"      Database: {config.get('database.dbname', 'N/A')}")
                    print(f"      Schema: {config.get('schema.include.list', config.get('schema.whitelist', 'N/A'))}")
                    print(f"      Tables: {config.get('table.include.list', config.get('table.whitelist', 'N/A'))}")
                    print(f"      Topic Prefix: {config.get('topic.prefix', 'N/A')}")
            except Exception as e:
                print(f"      Error: {e}")
    else:
        print("   No Debezium connectors found")
    
    # Check Sink connectors
    print("\n3. Sink Connectors:")
    sink_connectors = [c for c in connectors if c.startswith("sink-")]
    if sink_connectors:
        for conn_name in sink_connectors:
            print(f"\n   {conn_name}:")
            try:
                # Get status
                status_response = requests.get(
                    f"{KAFKA_CONNECT_URL}/connectors/{conn_name}/status",
                    timeout=10
                )
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"      State: {status.get('connector', {}).get('state', 'N/A')}")
                    print(f"      Worker: {status.get('connector', {}).get('worker_id', 'N/A')}")
                    
                    tasks = status.get('tasks', [])
                    print(f"      Tasks: {len(tasks)}")
                    for task in tasks:
                        print(f"         Task {task.get('id')}: {task.get('state', 'N/A')}")
                        if task.get('state') == 'FAILED':
                            print(f"            Error: {task.get('trace', 'N/A')[:200]}")
                else:
                    print(f"      Status Error: {status_response.status_code}")
                
                # Get config
                config_response = requests.get(
                    f"{KAFKA_CONNECT_URL}/connectors/{conn_name}/config",
                    timeout=10
                )
                if config_response.status_code == 200:
                    config = config_response.json()
                    connector_class = config.get('connector.class', 'N/A')
                    print(f"      Type: {connector_class}")
                    
                    if 'snowflake' in connector_class.lower():
                        print(f"      Snowflake Account: {config.get('snowflake.url.name', 'N/A')}")
                        print(f"      Database: {config.get('snowflake.database.name', 'N/A')}")
                        print(f"      Schema: {config.get('snowflake.schema.name', 'N/A')}")
                        print(f"      Warehouse: {config.get('snowflake.warehouse.name', 'N/A')}")
                        print(f"      Topics: {config.get('topics', 'N/A')}")
                    elif 's3' in connector_class.lower():
                        print(f"      S3 Bucket: {config.get('s3.bucket.name', 'N/A')}")
                        print(f"      S3 Prefix: {config.get('s3.prefix', 'N/A')}")
                        print(f"      Topics: {config.get('topics', 'N/A')}")
                    else:
                        print(f"      Topics: {config.get('topics', 'N/A')}")
            except Exception as e:
                print(f"      Error: {e}")
    else:
        print("   No Sink connectors found")
    
    # Check for ps_sn_p specific connectors
    print("\n4. ps_sn_p Pipeline Connectors:")
    ps_sn_p_connectors = [c for c in connectors if 'ps_sn_p' in c.lower()]
    if ps_sn_p_connectors:
        for conn_name in ps_sn_p_connectors:
            print(f"   Found: {conn_name}")
    else:
        print("   No ps_sn_p connectors found")
    
    # Check connector plugins
    print("\n5. Available Connector Plugins:")
    plugins_response = requests.get(f"{KAFKA_CONNECT_URL}/connector-plugins", timeout=10)
    if plugins_response.status_code == 200:
        plugins = plugins_response.json()
        snowflake_plugins = [p for p in plugins if 'snowflake' in p.get('class', '').lower()]
        debezium_plugins = [p for p in plugins if 'debezium' in p.get('class', '').lower()]
        
        print(f"   Total plugins: {len(plugins)}")
        print(f"   Debezium plugins: {len(debezium_plugins)}")
        print(f"   Snowflake plugins: {len(snowflake_plugins)}")
        
        if snowflake_plugins:
            for plugin in snowflake_plugins:
                print(f"      - {plugin.get('class')} (v{plugin.get('version', 'N/A')})")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Kafka UI URL: http://72.61.233.209:8080")
print("=" * 70)


