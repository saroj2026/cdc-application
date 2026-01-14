"""Create Snowflake sink connector using backend's sink_config logic."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ingestion.sink_config import SinkConfigGenerator
from ingestion.models import Connection
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
print("Creating Snowflake Sink Connector (Using Backend Logic)")
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
    
    # Get target connection
    cursor.execute("""
        SELECT id, name, database_type, connection_type, host, port, username, password, database, schema, additional_config
        FROM connections
        WHERE id = %s
    """, (target_conn_id,))
    
    target_conn_row = cursor.fetchone()
    if not target_conn_row:
        print("Target connection not found!")
        exit(1)
    
    conn_id, conn_name, db_type, conn_type, host, port, username, password, db, schema, additional_config = target_conn_row
    
    # Parse additional_config
    if isinstance(additional_config, str):
        additional_config = json.loads(additional_config)
    elif additional_config is None:
        additional_config = {}
    
    # Create Connection object
    connection = Connection(
        id=conn_id,
        name=conn_name,
        database_type=db_type,
        connection_type=conn_type or "source",
        host=host,
        port=port or 443,
        username=username,
        password=password,
        database=db,
        schema=schema,
        additional_config=additional_config
    )
    
    # Get Kafka topics
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
    
    print(f"   Kafka Topics: {topics}")
    
    # Generate sink connector name
    sink_connector_name = f"sink-{pipeline_name.lower().replace(' ', '_')}-snowflake-{(target_schema or schema or 'public').lower()}"
    
    print(f"\n2. Generating sink config using backend logic...")
    
    # Use backend's sink config generator
    sink_config = SinkConfigGenerator.generate_sink_config(
        connector_name=sink_connector_name,
        target_connection=connection,
        target_database=target_db or db,
        target_schema=target_schema or schema or "public",
        kafka_topics=topics,
        table_mapping=None,
        batch_size=10000,
        insert_mode="insert",
        pk_mode="record_key"
    )
    
    print(f"   Config generated successfully")
    print(f"   Connector Name: {sink_connector_name}")
    print(f"   Account: {sink_config.get('snowflake.url.name', 'N/A')}")
    print(f"   Auth Method: {'Private Key' if 'snowflake.private.key' in sink_config else 'Password'}")
    
    # Create connector
    print(f"\n3. Creating sink connector...")
    
    # Delete existing if exists
    try:
        requests.delete(f"{KAFKA_CONNECT_URL}/connectors/{sink_connector_name}", timeout=5)
    except:
        pass
    
    create_data = {
        "name": sink_connector_name,
        "config": sink_config
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
            print(f"\n4. Connector Status:")
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

