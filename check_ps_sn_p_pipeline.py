"""Check ps_sn_p pipeline configuration."""

import requests
import json

API_BASE_URL = "http://localhost:8000/api/v1"
PIPELINE_NAME = "ps_sn_p"

print("=" * 70)
print(f"Checking Pipeline: {PIPELINE_NAME}")
print("=" * 70)

try:
    # Get all pipelines
    response = requests.get(f"{API_BASE_URL}/pipelines", timeout=10)
    pipelines = response.json() if response.status_code == 200 else []
    
    pipeline = None
    for p in pipelines:
        if p.get("name") == PIPELINE_NAME:
            pipeline = p
            break
    
    if not pipeline:
        print(f"\n❌ Pipeline '{PIPELINE_NAME}' not found")
        print("\nAvailable pipelines:")
        for p in pipelines:
            print(f"  - {p.get('name')} (ID: {p.get('id')})")
        exit(1)
    
    print(f"\n✅ Found pipeline: {pipeline.get('id')}")
    print("\n" + "=" * 70)
    print("PIPELINE CONFIGURATION")
    print("=" * 70)
    
    print(f"\nBasic Info:")
    print(f"  Name: {pipeline.get('name')}")
    print(f"  ID: {pipeline.get('id')}")
    print(f"  Status: {pipeline.get('status')}")
    print(f"  Mode: {pipeline.get('mode')}")
    print(f"  Full Load Status: {pipeline.get('full_load_status')}")
    print(f"  CDC Status: {pipeline.get('cdc_status')}")
    
    print(f"\nSource Configuration:")
    print(f"  Connection ID: {pipeline.get('source_connection_id')}")
    print(f"  Database: {pipeline.get('source_database')}")
    print(f"  Schema: {pipeline.get('source_schema')}")
    print(f"  Tables: {pipeline.get('source_tables')}")
    
    print(f"\nTarget Configuration:")
    print(f"  Connection ID: {pipeline.get('target_connection_id')}")
    print(f"  Database: {pipeline.get('target_database')}")
    print(f"  Schema: {pipeline.get('target_schema')}")
    print(f"  Tables: {pipeline.get('target_tables')}")
    print(f"  Auto Create Target: {pipeline.get('auto_create_target')}")
    
    # Get source connection details
    print(f"\n" + "=" * 70)
    print("SOURCE CONNECTION DETAILS")
    print("=" * 70)
    try:
        source_conn_id = pipeline.get('source_connection_id')
        conn_response = requests.get(f"{API_BASE_URL}/connections", timeout=10)
        connections = conn_response.json() if conn_response.status_code == 200 else []
        
        source_conn = None
        for conn in connections:
            if conn.get('id') == source_conn_id:
                source_conn = conn
                break
        
        if source_conn:
            print(f"\n  Name: {source_conn.get('name')}")
            print(f"  Type: {source_conn.get('database_type')}")
            print(f"  Host: {source_conn.get('host')}")
            print(f"  Port: {source_conn.get('port')}")
            print(f"  Database: {source_conn.get('database')}")
            print(f"  Schema: {source_conn.get('schema')}")
            print(f"  Username: {source_conn.get('username')}")
        else:
            print(f"  ⚠️  Source connection not found")
    except Exception as e:
        print(f"  ⚠️  Error getting source connection: {e}")
    
    # Get target connection details
    print(f"\n" + "=" * 70)
    print("TARGET CONNECTION DETAILS (Snowflake)")
    print("=" * 70)
    try:
        target_conn_id = pipeline.get('target_connection_id')
        conn_response = requests.get(f"{API_BASE_URL}/connections", timeout=10)
        connections = conn_response.json() if conn_response.status_code == 200 else []
        
        target_conn = None
        for conn in connections:
            if conn.get('id') == target_conn_id:
                target_conn = conn
                break
        
        if target_conn:
            print(f"\n  Name: {target_conn.get('name')}")
            print(f"  Type: {target_conn.get('database_type')}")
            print(f"  Host/Account: {target_conn.get('host')}")
            print(f"  Database: {target_conn.get('database')}")
            print(f"  Schema: {target_conn.get('schema')}")
            print(f"  Username: {target_conn.get('username')}")
            print(f"  Additional Config Keys: {list(target_conn.get('additional_config', {}).keys()) if target_conn.get('additional_config') else 'None'}")
        else:
            print(f"  ⚠️  Target connection not found")
    except Exception as e:
        print(f"  ⚠️  Error getting target connection: {e}")
    
    # Get sink config
    print(f"\n" + "=" * 70)
    print("SINK CONNECTOR CONFIGURATION")
    print("=" * 70)
    sink_config = pipeline.get('sink_config', {})
    if sink_config:
        print(f"\nKey Configuration:")
        print(f"  Key Converter: {sink_config.get('key.converter', 'N/A')}")
        print(f"  Value Converter: {sink_config.get('value.converter', 'N/A')}")
        print(f"  Schema Enable: {sink_config.get('value.converter.schemas.enable', 'N/A')}")
        print(f"  Transforms: {sink_config.get('transforms', 'N/A')}")
        if sink_config.get('transforms'):
            transform_type = sink_config.get(f"transforms.{sink_config.get('transforms')}.type", 'N/A')
            print(f"  Transform Type: {transform_type}")
        
        print(f"\nSnowflake Configuration:")
        print(f"  URL: {sink_config.get('snowflake.url.name', 'N/A')}")
        print(f"  Database: {sink_config.get('snowflake.database.name', 'N/A')}")
        print(f"  Schema: {sink_config.get('snowflake.schema.name', 'N/A')}")
        print(f"  User: {sink_config.get('snowflake.user.name', 'N/A')}")
        print(f"  Auth: {'Private Key' if sink_config.get('snowflake.private.key') else 'Password' if sink_config.get('snowflake.password') else 'N/A'}")
        
        print(f"\nTopic Configuration:")
        print(f"  Topics: {sink_config.get('topics', 'N/A')}")
        print(f"  Topic Regex: {sink_config.get('topics.regex', 'N/A')}")
    else:
        print(f"\n  ⚠️  No sink config found")
    
    # Get Debezium config
    print(f"\n" + "=" * 70)
    print("DEBEZIUM SOURCE CONNECTOR CONFIGURATION")
    print("=" * 70)
    debezium_config = pipeline.get('debezium_config', {})
    if debezium_config:
        print(f"\nKey Configuration:")
        print(f"  Connector Class: {debezium_config.get('connector.class', 'N/A')}")
        print(f"  Database Hostname: {debezium_config.get('database.hostname', 'N/A')}")
        print(f"  Database Port: {debezium_config.get('database.port', 'N/A')}")
        print(f"  Database Name: {debezium_config.get('database.dbname', debezium_config.get('database.database', 'N/A'))}")
        print(f"  Table Include List: {debezium_config.get('table.include.list', 'N/A')}")
        print(f"  Snapshot Mode: {debezium_config.get('snapshot.mode', 'N/A')}")
        print(f"  Topic Prefix: {debezium_config.get('topic.prefix', 'N/A')}")
    else:
        print(f"\n  ⚠️  No Debezium config found")
    
    print("\n" + "=" * 70)
    print("✅ Configuration Check Complete")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

