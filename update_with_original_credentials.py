"""Update connector with original AWS credentials."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ingestion.kafka_connect_client import KafkaConnectClient

CONNECTOR_NAME = "sink-as400-s3_p-s3-dbo"
KAFKA_CONNECT_URL = os.getenv("KAFKA_CONNECT_URL", "http://72.61.233.209:8083")

# Original credentials
ACCESS_KEY = "AKIATLTXNANW2EV7QGV2"
SECRET_KEY = "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"

print("=" * 70)
print(f"Updating Connector with Original Credentials")
print("=" * 70)

kafka_client = KafkaConnectClient(base_url=KAFKA_CONNECT_URL)

try:
    # Test credentials first
    print(f"\n1. Testing AWS credentials...\n")
    import boto3
    from botocore.exceptions import ClientError
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name='us-east-1'
    )
    
    try:
        response = s3_client.list_buckets()
        print(f"   ✅ Credentials are VALID!")
        print(f"   Can access AWS S3")
        
        # Check bucket access
        try:
            s3_client.list_objects_v2(Bucket='mycdcbucket26', MaxKeys=1)
            print(f"   ✅ Can access bucket 'mycdcbucket26'")
        except ClientError as e:
            print(f"   ⚠️  Cannot access bucket: {e.response['Error']['Code']}")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"   ❌ Credentials test failed: {error_code}")
        if error_code == 'InvalidAccessKeyId':
            print(f"   The Access Key ID doesn't exist")
        elif error_code == 'SignatureDoesNotMatch':
            print(f"   Secret Key doesn't match Access Key ID")
    
    # Update connector configuration
    print(f"\n2. Updating connector configuration...\n")
    current_config = kafka_client.get_connector_config(CONNECTOR_NAME)
    
    print(f"   Current aws.access.key.id: {current_config.get('aws.access.key.id', 'NOT SET')[:20]}...")
    
    current_config['aws.access.key.id'] = ACCESS_KEY
    current_config['aws.secret.access.key'] = SECRET_KEY
    
    kafka_client.update_connector(CONNECTOR_NAME, current_config)
    print(f"   ✅ Configuration updated!")
    print(f"   New aws.access.key.id: {ACCESS_KEY}")
    
    # Verify update
    print(f"\n3. Verifying update...\n")
    updated_config = kafka_client.get_connector_config(CONNECTOR_NAME)
    if updated_config.get('aws.access.key.id') == ACCESS_KEY:
        print(f"   ✅ Verified: Access Key ID updated correctly")
    else:
        print(f"   ⚠️  Access Key ID doesn't match")
    
    # Restart connector
    print(f"\n4. Restarting connector...\n")
    kafka_client.restart_connector(CONNECTOR_NAME)
    print(f"   ✅ Restart command sent!")
    
    # Wait and check status
    import time
    print(f"\n5. Waiting for connector to restart (30 seconds)...\n")
    time.sleep(30)
    
    status = kafka_client.get_connector_status(CONNECTOR_NAME)
    connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
    tasks = status.get('tasks', [])
    
    print(f"   Connector State: {connector_state}")
    for i, task in enumerate(tasks):
        task_state = task.get('state', 'UNKNOWN')
        print(f"   Task {i} State: {task_state}")
        
        if task_state == 'FAILED':
            trace = task.get('trace', '')
            if 'AWS Access Key Id you provided does not exist' in trace:
                print(f"      ❌ Still showing: Access Key ID doesn't exist")
            elif 'SignatureDoesNotMatch' in trace or 'signature' in trace.lower():
                print(f"      ❌ Still showing: Secret Key mismatch")
            else:
                print(f"      ⚠️  Error: {trace[:200]}...")
        elif task_state == 'RUNNING':
            print(f"      ✅ Task is running successfully!")
    
    print(f"\n{'='*70}")
    if connector_state == 'RUNNING' and all(task.get('state') == 'RUNNING' for task in tasks):
        print("✅ SUCCESS! Connector is running!")
        print("Data should now be flowing to S3!")
    else:
        print("⚠️  Connector still has issues - check error above")
    print(f"{'='*70}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()



