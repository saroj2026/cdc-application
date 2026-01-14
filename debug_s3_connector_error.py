"""Debug S3 connector creation error by capturing the exact error message."""

import requests
import json
import sys

API_BASE = "http://localhost:8000/api/v1"
KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
PIPELINE_NAME = "PostgreSQL_to_S3_cdctest"

print("=" * 70)
print("Debugging S3 Connector Creation Error")
print("=" * 70)

try:
    # Get pipeline
    print("\n1. Getting pipeline details...")
    response = requests.get(f"{API_BASE}/pipelines", timeout=10)
    pipelines = response.json()
    
    pipeline = None
    for p in pipelines:
        if p.get('name') == PIPELINE_NAME:
            pipeline = p
            break
    
    if not pipeline:
        print(f"Pipeline '{PIPELINE_NAME}' not found")
        sys.exit(1)
    
    print(f"   Pipeline ID: {pipeline['id']}")
    
    # Get connections
    source_conn = requests.get(f"{API_BASE}/connections/{pipeline['source_connection_id']}", timeout=10).json()
    target_conn = requests.get(f"{API_BASE}/connections/{pipeline['target_connection_id']}", timeout=10).json()
    
    print(f"   Source: {source_conn.get('name')} ({source_conn.get('database_type')})")
    print(f"   Target: {target_conn.get('name')} ({target_conn.get('database_type')})")
    
    # Build expected connector name
    pipeline_name_lower = pipeline['name'].lower().replace(' ', '_')
    target_schema = pipeline.get('target_schema') or target_conn.get('schema') or 'public'
    sink_connector_name = f"sink-{pipeline_name_lower}-s3-{target_schema.lower()}"
    
    print(f"\n2. Expected Sink Connector Name: {sink_connector_name}")
    
    # Check if connector exists
    try:
        existing = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{sink_connector_name}", timeout=10)
        if existing.status_code == 200:
            print(f"   ⚠️  Connector already exists!")
            print(f"   Config: {json.dumps(existing.json(), indent=2)}")
    except:
        print(f"   ✅ Connector doesn't exist (will create)")
    
    # Build topics list
    source_tables = pipeline.get('source_tables', [])
    source_schema = pipeline.get('source_schema', 'public')
    topics = [f"{pipeline['name']}.{source_schema}.{table}" for table in source_tables]
    
    print(f"\n3. Topics to use: {topics}")
    
    if not topics:
        print("   ❌ ERROR: No topics found!")
        sys.exit(1)
    
    # Build S3 sink config (same as what the backend generates)
    s3_config = {
        "connector.class": "io.confluent.connect.s3.S3SinkConnector",
        "tasks.max": "1",
        "topics": ",".join(topics),
        "s3.region": target_conn.get('additional_config', {}).get('region_name', 'us-east-1'),
        "s3.bucket.name": target_conn.get('database', ''),
        "s3.part.size": "5242880",
        "flush.size": "3000",
        "storage.class": "io.confluent.connect.s3.storage.S3Storage",
        "format.class": "io.confluent.connect.s3.format.json.JsonFormat",
        "partitioner.class": "io.confluent.connect.storage.partitioner.DefaultPartitioner",
        "schema.compatibility": "NONE",
        "aws.access.key.id": target_conn.get('username', ''),
        "aws.secret.access.key": target_conn.get('password', ''),
    }
    
    if pipeline.get('target_schema'):
        s3_config["s3.prefix"] = pipeline.get('target_schema', '')
    
    print(f"\n4. S3 Sink Config:")
    safe_config = s3_config.copy()
    safe_config['aws.secret.access.key'] = '***HIDDEN***'
    print(json.dumps(safe_config, indent=2))
    
    # Validate config
    print(f"\n5. Validating config...")
    validate_response = requests.put(
        f"{KAFKA_CONNECT_URL}/connector-plugins/io.confluent.connect.s3.S3SinkConnector/config/validate",
        json=s3_config,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    if validate_response.status_code == 200:
        validation = validate_response.json()
        errors = [c for c in validation.get('configs', []) if c.get('value', {}).get('errors')]
        if errors:
            print(f"   ❌ Validation Errors:")
            for err in errors:
                print(f"      {err.get('value', {}).get('name')}: {err.get('value', {}).get('errors')}")
        else:
            print(f"   ✅ Config is valid")
    else:
        print(f"   ⚠️  Validation failed: {validate_response.status_code}")
        print(f"   {validate_response.text}")
    
    # Try to create connector
    print(f"\n6. Attempting to create connector...")
    
    # Delete if exists
    try:
        requests.delete(f"{KAFKA_CONNECT_URL}/connectors/{sink_connector_name}", timeout=10)
        print(f"   Deleted existing connector (if any)")
    except:
        pass
    
    create_data = {
        "name": sink_connector_name,
        "config": s3_config
    }
    
    print(f"   Request: {json.dumps({'name': sink_connector_name, 'config': safe_config}, indent=2)}")
    
    create_response = requests.post(
        f"{KAFKA_CONNECT_URL}/connectors",
        json=create_data,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    print(f"\n   Status Code: {create_response.status_code}")
    
    if create_response.status_code in [200, 201]:
        print(f"   ✅ Connector created successfully!")
        print(f"   Response: {json.dumps(create_response.json(), indent=2)}")
    else:
        print(f"   ❌ Failed to create connector")
        print(f"\n   Error Response:")
        try:
            error_json = create_response.json()
            print(json.dumps(error_json, indent=2))
            
            if 'message' in error_json:
                print(f"\n   Error Message: {error_json['message']}")
            if 'error_code' in error_json:
                print(f"   Error Code: {error_json['error_code']}")
        except:
            print(f"   {create_response.text}")
    
    print("\n" + "=" * 70)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()


