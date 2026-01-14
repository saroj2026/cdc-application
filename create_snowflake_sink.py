"""Create Snowflake sink connector for ps_sn_p pipeline."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
API_BASE = "http://localhost:8000/api/v1"
PIPELINE_ID = "ae7bb432-2fa8-48eb-90a0-d6bb4c164441"

print("=" * 70)
print("Creating Snowflake Sink Connector")
print("=" * 70)

try:
    # Get pipeline details
    print("\n1. Getting pipeline details...")
    pipeline_response = requests.get(f"{API_BASE}/pipelines/{PIPELINE_ID}", timeout=10)
    if pipeline_response.status_code == 200:
        pipeline = pipeline_response.json()
        print(f"   Pipeline: {pipeline.get('name')}")
        print(f"   Kafka Topics: {pipeline.get('kafka_topics', [])}")
        
        # Get target connection
        target_conn_id = pipeline.get('target_connection_id')
        conn_response = requests.get(f"{API_BASE}/connections/{target_conn_id}", timeout=10)
        if conn_response.status_code == 200:
            target_conn = conn_response.json()
            print(f"   Target: {target_conn.get('name')} ({target_conn.get('database_type')})")
            
            # Get Kafka topics
            kafka_topics = pipeline.get('kafka_topics', [])
            if not kafka_topics:
                print("   ⚠️  No Kafka topics found in pipeline")
                # Try to discover from Debezium connector
                dbz_name = pipeline.get('debezium_connector_name')
                if dbz_name:
                    dbz_config_response = requests.get(
                        f"{KAFKA_CONNECT_URL}/connectors/{dbz_name}/config",
                        timeout=10
                    )
                    if dbz_config_response.status_code == 200:
                        dbz_config = dbz_config_response.json()
                        topic_prefix = dbz_config.get('topic.prefix', 'ps_sn_p')
                        table_include = dbz_config.get('table.include.list', 'public.projects_simple')
                        # Extract table name
                        if '.' in table_include:
                            schema, table = table_include.split('.', 1)
                            kafka_topics = [f"{topic_prefix}.{schema}.{table}"]
                        else:
                            kafka_topics = [f"{topic_prefix}.public.{table_include}"]
                        print(f"   Discovered topics: {kafka_topics}")
            
            if kafka_topics:
                # Generate sink connector name
                pipeline_name = pipeline.get('name', 'ps_sn_p')
                target_schema = pipeline.get('target_schema') or target_conn.get('schema') or 'public'
                sink_connector_name = f"sink-{pipeline_name.lower().replace(' ', '_')}-snowflake-{target_schema.lower()}"
                
                print(f"\n2. Sink Connector Name: {sink_connector_name}")
                print(f"   Topics: {kafka_topics}")
                
                # Get Snowflake connection details
                account = target_conn.get('host') or target_conn.get('additional_config', {}).get('account', '')
                username = target_conn.get('username', '')
                password = target_conn.get('password', '')
                database = pipeline.get('target_database') or target_conn.get('database', '')
                schema = pipeline.get('target_schema') or target_conn.get('schema') or 'public'
                warehouse = target_conn.get('additional_config', {}).get('warehouse', '')
                role = target_conn.get('additional_config', {}).get('role', '')
                
                print(f"\n3. Snowflake Configuration:")
                print(f"   Account: {account}")
                print(f"   Database: {database}")
                print(f"   Schema: {schema}")
                print(f"   Warehouse: {warehouse or 'N/A'}")
                print(f"   Role: {role or 'N/A'}")
                
                # Build sink connector config
                config = {
                    "connector.class": "com.snowflake.kafka.connector.SnowflakeSinkConnector",
                    "tasks.max": "1",
                    "topics": ",".join(kafka_topics),
                    "snowflake.url.name": account,
                    "snowflake.user.name": username,
                    "snowflake.password": password,
                    "snowflake.database.name": database,
                    "snowflake.schema.name": schema,
                    "buffer.count.records": "10000",
                    "buffer.flush.time": "60",
                    "buffer.size.bytes": "5000000",
                    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
                    "value.converter": "com.snowflake.kafka.connector.records.SnowflakeJsonConverter",
                    "errors.tolerance": "all",
                    "errors.log.enable": "true",
                    "errors.log.include.messages": "true",
                }
                
                if warehouse:
                    config["snowflake.warehouse.name"] = warehouse
                if role:
                    config["snowflake.role.name"] = role
                
                # Add topic2table mapping
                topic2table_map = []
                for topic in kafka_topics:
                    # Extract table name from topic (last part after last dot)
                    table_name = topic.split('.')[-1]
                    topic2table_map.append(f"{topic}:{table_name}")
                config["snowflake.topic2table.map"] = ",".join(topic2table_map)
                
                print(f"\n4. Creating sink connector...")
                
                # Delete existing connector if it exists
                try:
                    delete_response = requests.delete(
                        f"{KAFKA_CONNECT_URL}/connectors/{sink_connector_name}",
                        timeout=10
                    )
                    if delete_response.status_code == 204:
                        print(f"   Deleted existing connector")
                except:
                    pass
                
                # Create connector
                create_data = {
                    "name": sink_connector_name,
                    "config": config
                }
                
                create_response = requests.post(
                    f"{KAFKA_CONNECT_URL}/connectors",
                    json=create_data,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                print(f"   Status Code: {create_response.status_code}")
                
                if create_response.status_code in [200, 201]:
                    result = create_response.json()
                    print(f"   ✅ Sink connector created successfully!")
                    print(f"   Name: {result.get('name', sink_connector_name)}")
                    
                    # Wait and check status
                    import time
                    time.sleep(3)
                    
                    status_response = requests.get(
                        f"{KAFKA_CONNECT_URL}/connectors/{sink_connector_name}/status",
                        timeout=10
                    )
                    if status_response.status_code == 200:
                        status = status_response.json()
                        print(f"\n5. Connector Status:")
                        print(f"   State: {status.get('connector', {}).get('state', 'N/A')}")
                        tasks = status.get('tasks', [])
                        for task in tasks:
                            print(f"   Task {task.get('id')}: {task.get('state', 'N/A')}")
                            if task.get('state') == 'FAILED':
                                trace = task.get('trace', '')
                                print(f"      Error: {trace[:500]}")
                else:
                    print(f"   ❌ Failed to create connector")
                    print(f"   Response: {create_response.text}")
                    try:
                        error_json = create_response.json()
                        print(f"   Error Details: {json.dumps(error_json, indent=2)}")
                    except:
                        pass
            else:
                print("   ❌ Cannot create sink connector: No Kafka topics available")
        else:
            print(f"   ❌ Error getting target connection: {conn_response.status_code}")
    else:
        print(f"   ❌ Error getting pipeline: {pipeline_response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)


