"""Create Snowflake sink connector using database connection details."""

import requests
import json
import psycopg2

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

# Database connection
DB_CONFIG = {
    "host": "72.61.233.209",
    "port": 5432,
    "database": "cdctest",
    "user": "cdc_user",
    "password": "cdc_pass"
}

print("=" * 70)
print("Creating Snowflake Sink Connector from Database")
print("=" * 70)

try:
    # Get pipeline and connection details from database
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    pipeline_id = "ae7bb432-2fa8-48eb-90a0-d6bb4c164441"
    
    cursor.execute("""
        SELECT p.name, p.target_connection_id, p.target_database, p.target_schema,
               p.kafka_topics, p.debezium_connector_name
        FROM pipelines p
        WHERE p.id = %s
    """, (pipeline_id,))
    
    pipeline = cursor.fetchone()
    if not pipeline:
        print("Pipeline not found!")
        exit(1)
    
    pipeline_name, target_conn_id, target_db, target_schema, kafka_topics, dbz_name = pipeline
    
    print(f"\n1. Pipeline: {pipeline_name}")
    print(f"   Target Database: {target_db}")
    print(f"   Target Schema: {target_schema}")
    
    # Get target connection
    cursor.execute("""
        SELECT name, database_type, host, username, password, database, schema, additional_config
        FROM connections
        WHERE id = %s
    """, (target_conn_id,))
    
    target_conn = cursor.fetchone()
    if not target_conn:
        print("Target connection not found!")
        exit(1)
    
    conn_name, db_type, host, username, password, db, schema, additional_config = target_conn
    
    print(f"   Target Connection: {conn_name} ({db_type})")
    
    # Parse additional_config
    if isinstance(additional_config, str):
        additional_config = json.loads(additional_config)
    elif additional_config is None:
        additional_config = {}
    
    account = host or additional_config.get('account', '')
    warehouse = additional_config.get('warehouse', '')
    role = additional_config.get('role', '')
    private_key = additional_config.get('private_key')
    private_key_passphrase = additional_config.get('private_key_passphrase')
    
    # Format Snowflake account URL properly for Kafka connector
    # Snowflake Kafka connector expects full URL format: https://account.snowflakecomputing.com
    # Convert account to lowercase and build full URL
    original_account = account
    
    # Remove protocol if present to get base account
    account_clean = account.replace("https://", "").replace("http://", "")
    account_clean = account_clean.replace(".snowflakecomputing.com", "")
    account_clean = account_clean.rstrip('/')
    
    # Convert to lowercase (Snowflake URLs are case-insensitive but lowercase is standard)
    account_clean = account_clean.lower()
    
    # Build full URL: https://account.snowflakecomputing.com
    account = f"https://{account_clean}.snowflakecomputing.com"
    
    print(f"   Using Snowflake URL: {account}")
    
    # Get Kafka topics - use discovered topic or from database
    if kafka_topics and len(kafka_topics) > 0:
        topics = kafka_topics
    else:
        # Discover from Debezium connector
        if dbz_name:
            dbz_config_response = requests.get(
                f"{KAFKA_CONNECT_URL}/connectors/{dbz_name}/config",
                timeout=10
            )
            if dbz_config_response.status_code == 200:
                dbz_config = dbz_config_response.json()
                topic_prefix = dbz_config.get('topic.prefix', 'ps_sn_p')
                table_include = dbz_config.get('table.include.list', 'public.projects_simple')
                if '.' in table_include:
                    schema_part, table = table_include.split('.', 1)
                    topics = [f"{topic_prefix}.{schema_part}.{table}"]
                else:
                    topics = [f"{topic_prefix}.public.{table_include}"]
            else:
                topics = ["ps_sn_p.public.projects_simple"]  # Fallback
        else:
            topics = ["ps_sn_p.public.projects_simple"]  # Fallback
    
    print(f"\n2. Kafka Topics: {topics}")
    
    # Generate sink connector name
    sink_connector_name = f"sink-{pipeline_name.lower().replace(' ', '_')}-snowflake-{(target_schema or schema or 'public').lower()}"
    
    print(f"\n3. Sink Connector Name: {sink_connector_name}")
    print(f"   Snowflake Account: {account}")
    print(f"   Database: {target_db or db}")
    print(f"   Schema: {target_schema or schema or 'public'}")
    print(f"   Warehouse: {warehouse or 'N/A'}")
    print(f"   Role: {role or 'N/A'}")
    
    # Build config
    config = {
        "connector.class": "com.snowflake.kafka.connector.SnowflakeSinkConnector",
        "tasks.max": "1",
        "topics": ",".join(topics),
        "snowflake.url.name": account,
        "snowflake.user.name": username,
        "snowflake.database.name": target_db or db,
        "snowflake.schema.name": target_schema or schema or "public",
        "buffer.count.records": "10000",
        "buffer.flush.time": "60",
        "buffer.size.bytes": "5000000",
        "key.converter": "org.apache.kafka.connect.storage.StringConverter",
        "value.converter": "com.snowflake.kafka.connector.records.SnowflakeJsonConverter",
        "errors.tolerance": "all",
        "errors.log.enable": "true",
        "errors.log.include.messages": "true",
    }
    
    # Authentication (only include the method being used, not both)
    if private_key:
        config["snowflake.private.key"] = private_key
        if private_key_passphrase:
            config["snowflake.private.key.passphrase"] = private_key_passphrase
        print(f"   Using private key authentication")
    elif password:
        config["snowflake.password"] = password
        print(f"   Using password authentication")
    else:
        print(f"   ERROR: No authentication method available!")
        exit(1)
    
    if warehouse:
        config["snowflake.warehouse.name"] = warehouse
    if role:
        config["snowflake.role.name"] = role
    
    # Add topic2table mapping
    topic2table_map = []
    for topic in topics:
        table_name = topic.split('.')[-1]
        topic2table_map.append(f"{topic}:{table_name}")
    config["snowflake.topic2table.map"] = ",".join(topic2table_map)
    
    print(f"\n4. Creating sink connector...")
    
    # Delete existing if exists
    try:
        requests.delete(f"{KAFKA_CONNECT_URL}/connectors/{sink_connector_name}", timeout=5)
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
                    print(f"      Error: {trace[:800]}")
    else:
        print(f"   ❌ Failed to create connector")
        print(f"   Response: {create_response.text}")
        try:
            error_json = create_response.json()
            print(f"   Error Details: {json.dumps(error_json, indent=2)}")
        except:
            pass
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)

