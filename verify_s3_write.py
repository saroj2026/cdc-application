"""Verify S3 sink connector configuration and check if data is being written to S3."""
import sys
import os
import json
import boto3
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from ingestion.kafka_connect_client import KafkaConnectClient

S3_CONFIG = {
    "bucket": "mycdcbucket26",
    "aws_access_key_id": "AKIATLTXNANW2EV7QGV2",
    "aws_secret_access_key": "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",
    "region_name": "us-east-1"
}

CONNECTOR_NAME = "sink-as400-s3_p-s3-dbo"

print("=" * 70)
print("Verifying S3 Sink Connector Configuration and Data Flow")
print("=" * 70)

# Check connector configuration
kafka_connect_url = os.getenv("KAFKA_CONNECT_URL", "http://72.61.233.209:8083")
kafka_client = KafkaConnectClient(kafka_connect_url)

print(f"\n1. Checking Connector Configuration...\n")

try:
    config = kafka_client.get_connector_config(CONNECTOR_NAME)
    
    print(f"   Connector: {CONNECTOR_NAME}")
    print(f"   flush.size: {config.get('flush.size', 'NOT SET')}")
    print(f"   s3.bucket.name: {config.get('s3.bucket.name', 'NOT SET')}")
    print(f"   s3.prefix: {config.get('s3.prefix', 'NOT SET')}")
    print(f"   topics: {config.get('topics', 'NOT SET')}")
    print(f"   format.class: {config.get('format.class', 'NOT SET')}")
    
    if config.get('flush.size') == '1':
        print(f"\n   ✅ flush.size is set to 1 - data will write immediately!")
    else:
        print(f"\n   ⚠️  flush.size is {config.get('flush.size')} - may need to be 1 for immediate writes")
    
except Exception as e:
    print(f"   ⚠️  Cannot connect to Kafka Connect (timeout): {e}")
    print("   Assuming you've updated flush.size to 1 via Kafka UI")
    print("   Continuing with S3 check to verify data is being written...")

# Check connector status
print(f"\n2. Checking Connector Status...\n")

try:
    status = kafka_client.get_connector_status(CONNECTOR_NAME)
    connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
    print(f"   Connector State: {connector_state}")
    
    tasks = status.get('tasks', [])
    for i, task in enumerate(tasks):
        task_state = task.get('state', 'UNKNOWN')
        task_id = task.get('id', i)
        print(f"   Task {task_id} State: {task_state}")
        
        if task_state == 'FAILED':
            error = task.get('trace', 'No error details')
            print(f"      ⚠️  Error: {error[:200]}...")
        elif task_state == 'RUNNING':
            print(f"      ✅ Task is running - processing messages")
    
    if connector_state != 'RUNNING':
        print(f"\n   ⚠️  Connector is not RUNNING - data may not be flowing")
    
except Exception as e:
    print(f"   ⚠️  Cannot check connector status (timeout): {e}")
    print("   Continuing with S3 check...")

# Check S3 for recent files
print(f"\n3. Checking S3 Bucket for Recent Data...\n")

s3_client = boto3.client(
    's3',
    aws_access_key_id=S3_CONFIG['aws_access_key_id'],
    aws_secret_access_key=S3_CONFIG['aws_secret_access_key'],
    region_name=S3_CONFIG['region_name']
)

try:
    # Check MYTABLE files (most recent first)
    print(f"   Checking MYTABLE/ prefix...")
    response = s3_client.list_objects_v2(
        Bucket=S3_CONFIG['bucket'], 
        Prefix="MYTABLE/"
    )
    
    if 'Contents' in response:
        files = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)
        print(f"   ✅ Found {len(files)} MYTABLE file(s)")
        
        # Show 5 most recent files
        print(f"\n   Most Recent Files:")
        for i, obj in enumerate(files[:5], 1):
            age = datetime.now(obj['LastModified'].tzinfo) - obj['LastModified']
            print(f"   {i}. {obj['Key']}")
            print(f"      Modified: {obj['LastModified']} ({age.total_seconds():.0f} seconds ago)")
            print(f"      Size: {obj['Size']} bytes")
        
        # Check for files modified in last 5 minutes
        recent_cutoff = datetime.now() - timedelta(minutes=5)
        recent_files = [f for f in files if f['LastModified'].replace(tzinfo=None) > recent_cutoff]
        
        if recent_files:
            print(f"\n   ✅ Found {len(recent_files)} file(s) modified in last 5 minutes!")
            print(f"   Data is actively being written to S3!")
        else:
            print(f"\n   ⚠️  No files modified in last 5 minutes")
            print(f"   Data may not be flowing, or flush.size is still too high")
    else:
        print(f"   ⚠️  No MYTABLE files found in S3")
    
    # Also check dbo/ prefix (based on s3.prefix)
    print(f"\n   Checking dbo/ prefix...")
    response = s3_client.list_objects_v2(
        Bucket=S3_CONFIG['bucket'], 
        Prefix="dbo/"
    )
    
    if 'Contents' in response:
        files = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)
        print(f"   ✅ Found {len(files)} file(s) in dbo/ prefix")
        
        # Show 5 most recent
        print(f"\n   Most Recent Files:")
        for i, obj in enumerate(files[:5], 1):
            age = datetime.now(obj['LastModified'].tzinfo) - obj['LastModified']
            print(f"   {i}. {obj['Key']}")
            print(f"      Modified: {obj['LastModified']} ({age.total_seconds():.0f} seconds ago)")
            print(f"      Size: {obj['Size']} bytes")
        
        # Check for recent files
        recent_cutoff = datetime.now() - timedelta(minutes=5)
        recent_files = [f for f in files if f['LastModified'].replace(tzinfo=None) > recent_cutoff]
        
        if recent_files:
            print(f"\n   ✅ Found {len(recent_files)} file(s) modified in last 5 minutes!")
    else:
        print(f"   ⚠️  No files found in dbo/ prefix")
    
    # Search for the specific record (id=333, name=KISHOR)
    print(f"\n4. Searching for Record (id=333, name=KISHOR)...\n")
    
    # Check both prefixes
    search_prefixes = ["MYTABLE/", "dbo/"]
    found_record = False
    
    for prefix in search_prefixes:
        response = s3_client.list_objects_v2(Bucket=S3_CONFIG['bucket'], Prefix=prefix)
        if 'Contents' not in response:
            continue
            
        # Get most recent files
        files = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)[:10]
        
        for file_obj in files:
            if not file_obj['Key'].endswith('.json'):
                continue
                
            try:
                obj_response = s3_client.get_object(Bucket=S3_CONFIG['bucket'], Key=file_obj['Key'])
                content = obj_response['Body'].read().decode('utf-8')
                
                # Search in content
                if '333' in content and 'KISHOR' in content.upper():
                    # Try to parse and find the exact record
                    try:
                        if content.strip().startswith('['):
                            data = json.loads(content)
                            if isinstance(data, list):
                                for record in data:
                                    if isinstance(record, dict):
                                        record_id = (record.get('id') or record.get('ID') or 
                                                   record.get('Id') or record.get('_id'))
                                        record_name = (record.get('name') or record.get('NAME') or 
                                                     record.get('Name'))
                                        
                                        if (str(record_id) == '333' and 
                                            record_name and 'KISHOR' in str(record_name).upper()):
                                            found_record = True
                                            print(f"   ✅ FOUND in: {file_obj['Key']}")
                                            print(f"      Record: {json.dumps(record, indent=6, default=str)}")
                                            break
                        else:
                            # Newline-delimited JSON
                            for line in content.strip().split('\n'):
                                if '333' in line and 'KISHOR' in line.upper():
                                    try:
                                        record = json.loads(line)
                                        record_id = (record.get('id') or record.get('ID') or 
                                                   record.get('Id'))
                                        record_name = (record.get('name') or record.get('NAME') or 
                                                     record.get('Name'))
                                        
                                        if (str(record_id) == '333' and 
                                            record_name and 'KISHOR' in str(record_name).upper()):
                                            found_record = True
                                            print(f"   ✅ FOUND in: {file_obj['Key']}")
                                            print(f"      Record: {json.dumps(record, indent=6, default=str)}")
                                            break
                                    except:
                                        pass
                    except:
                        pass
                        
                    if found_record:
                        break
            except Exception as e:
                pass
        
        if found_record:
            break
    
    if not found_record:
        print(f"   ⚠️  Record not found in recent files")
        print(f"   It may be in older files, or data hasn't been written yet")
    
except Exception as e:
    print(f"   ❌ Error checking S3: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Summary:")
print("  - Check connector configuration above")
print("  - Check connector status (should be RUNNING)")
print("  - Check S3 for recent file modifications")
print("  - Search for your specific record")
print("=" * 70)

