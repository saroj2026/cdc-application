"""Check AS400-S3_P pipeline status and sample data."""
import sys
import os
import json
import boto3

sys.path.insert(0, os.path.dirname(__file__))

from ingestion.database import SessionLocal
from ingestion.database.models_db import PipelineModel
from ingestion.kafka_connect_client import KafkaConnectClient

S3_CONFIG = {
    "bucket": "mycdcbucket26",
    "aws_access_key_id": "AKIATLTXNANW2EV7QGV2",
    "aws_secret_access_key": "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",
    "region_name": "us-east-1"
}

print("=" * 70)
print("AS400-S3_P Pipeline Status Check")
print("=" * 70)

# Get pipeline
db = SessionLocal()
pipeline = db.query(PipelineModel).filter(PipelineModel.name == 'AS400-S3_P').first()

if not pipeline:
    print("❌ Pipeline not found!")
    sys.exit(1)

print(f"\nPipeline: {pipeline.name}")
print(f"Status: {pipeline.status.value}")
print(f"CDC Status: {pipeline.cdc_status.value}")
print(f"Debezium Connector: {pipeline.debezium_connector_name}")
print(f"Sink Connector: {pipeline.sink_connector_name}")
print(f"Kafka Topics: {pipeline.kafka_topics}")

# Check connector status
kafka_connect_url = os.getenv("KAFKA_CONNECT_URL", "http://72.61.233.209:8083")
kafka_client = KafkaConnectClient(kafka_connect_url)

print(f"\n2. Checking Connector Status...\n")

if pipeline.debezium_connector_name:
    try:
        debezium_status = kafka_client.get_connector_status(pipeline.debezium_connector_name)
        print(f"   Debezium Connector ({pipeline.debezium_connector_name}):")
        print(f"      State: {debezium_status.get('connector', {}).get('state', 'UNKNOWN')}")
        tasks = debezium_status.get('tasks', [])
        for i, task in enumerate(tasks):
            print(f"      Task {i}: {task.get('state', 'UNKNOWN')}")
    except Exception as e:
        print(f"   ⚠️  Error checking Debezium: {e}")

if pipeline.sink_connector_name:
    try:
        sink_status = kafka_client.get_connector_status(pipeline.sink_connector_name)
        print(f"\n   Sink Connector ({pipeline.sink_connector_name}):")
        print(f"      State: {sink_status.get('connector', {}).get('state', 'UNKNOWN')}")
        tasks = sink_status.get('tasks', [])
        for i, task in enumerate(tasks):
            print(f"      Task {i}: {task.get('state', 'UNKNOWN')}")
    except Exception as e:
        print(f"   ⚠️  Error checking Sink: {e}")

# Sample MYTABLE files to see data format
print(f"\n3. Sampling MYTABLE files to check data format...\n")

s3_client = boto3.client(
    's3',
    aws_access_key_id=S3_CONFIG['aws_access_key_id'],
    aws_secret_access_key=S3_CONFIG['aws_secret_access_key'],
    region_name=S3_CONFIG['region_name']
)

response = s3_client.list_objects_v2(Bucket=S3_CONFIG['bucket'], Prefix="MYTABLE/")
mytable_files = []

if 'Contents' in response:
    mytable_files = sorted([obj['Key'] for obj in response['Contents'] 
                          if obj['Key'].endswith('.json')], 
                          key=lambda x: response['Contents'][[o['Key'] for o in response['Contents']].index(x)]['LastModified'],
                          reverse=True)[:3]  # Get 3 most recent
    
    print(f"   Checking {len(mytable_files)} most recent file(s)...\n")
    
    for file_key in mytable_files:
        try:
            obj_response = s3_client.get_object(Bucket=S3_CONFIG['bucket'], Key=file_key)
            content = obj_response['Body'].read().decode('utf-8')
            
            print(f"   📄 File: {file_key}")
            
            # Try to parse
            try:
                if content.strip().startswith('['):
                    data = json.loads(content)
                    if isinstance(data, list) and data:
                        print(f"      Format: JSON Array")
                        print(f"      Records: {len(data)}")
                        print(f"      Sample record keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'N/A'}")
                        if isinstance(data[0], dict):
                            print(f"      Sample record: {json.dumps(data[0], indent=8, default=str)[:300]}...")
                else:
                    # Newline-delimited
                    lines = [l for l in content.strip().split('\n') if l.strip()]
                    if lines:
                        first_record = json.loads(lines[0])
                        print(f"      Format: Newline-delimited JSON")
                        print(f"      Records: {len(lines)}")
                        print(f"      Sample record keys: {list(first_record.keys()) if isinstance(first_record, dict) else 'N/A'}")
                        if isinstance(first_record, dict):
                            print(f"      Sample record: {json.dumps(first_record, indent=8, default=str)[:300]}...")
            except Exception as e:
                print(f"      ⚠️  Parse error: {e}")
                print(f"      Content preview: {content[:200]}...")
            
            print()
            
        except Exception as e:
            print(f"   ⚠️  Error reading {file_key}: {e}\n")

print("=" * 70)
print("Summary:")
print("  - Check connector states above")
print("  - Review sample data format to understand field names")
print("  - If connectors are RUNNING, data should be flowing")
print("=" * 70)

db.close()
