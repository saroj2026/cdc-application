"""Get full error trace from failed connector task."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ingestion.kafka_connect_client import KafkaConnectClient

CONNECTOR_NAME = "sink-as400-s3_p-s3-dbo"
KAFKA_CONNECT_URL = os.getenv("KAFKA_CONNECT_URL", "http://72.61.233.209:8083")

print("=" * 70)
print(f"Getting Full Error Details: {CONNECTOR_NAME}")
print("=" * 70)

kafka_client = KafkaConnectClient(base_url=KAFKA_CONNECT_URL)

try:
    status = kafka_client.get_connector_status(CONNECTOR_NAME)
    
    print(f"\nConnector State: {status.get('connector', {}).get('state', 'UNKNOWN')}\n")
    
    tasks = status.get('tasks', [])
    for i, task in enumerate(tasks):
        task_state = task.get('state', 'UNKNOWN')
        print(f"Task {i}: {task_state}\n")
        
        if task_state == 'FAILED':
            trace = task.get('trace', 'No trace available')
            print("=" * 70)
            print("FULL ERROR TRACE:")
            print("=" * 70)
            print(trace)
            print("=" * 70)
            
            # Check for specific error types
            if 'AWS Access Key Id you provided does not exist' in trace:
                print("\n❌ ERROR: AWS Access Key ID is invalid")
                print("   The credentials may still be incorrect or not saved properly")
            elif 'AccessDenied' in trace or '403' in trace:
                print("\n❌ ERROR: AWS Access Denied")
                print("   Check IAM permissions for the AWS user")
            elif 'NoSuchBucket' in trace:
                print("\n❌ ERROR: S3 Bucket not found")
                print("   Verify bucket name and region")
            elif 'Connection' in trace and 'timeout' in trace.lower():
                print("\n❌ ERROR: Connection timeout")
                print("   Check network connectivity to S3")
    
    # Also verify the config was actually updated
    print(f"\n{'='*70}")
    print("Verifying Configuration:")
    print(f"{'='*70}\n")
    config = kafka_client.get_connector_config(CONNECTOR_NAME)
    print(f"aws.access.key.id: {config.get('aws.access.key.id', 'NOT SET')}")
    print(f"aws.secret.access.key: {'SET' if config.get('aws.secret.access.key') else 'NOT SET'}")
    
    if config.get('aws.access.key.id') == 'AKIATLTXNANW2JU6WWAH':
        print("\n✅ Configuration shows new access key ID")
    else:
        print(f"\n⚠️  Configuration shows different access key: {config.get('aws.access.key.id')}")
        print("   The update may not have been applied correctly")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()



