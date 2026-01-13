"""Diagnose S3 sink connector task failure."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ingestion.kafka_connect_client import KafkaConnectClient

CONNECTOR_NAME = "sink-as400-s3_p-s3-dbo"
KAFKA_CONNECT_URL = os.getenv("KAFKA_CONNECT_URL", "http://72.61.233.209:8083")

print("=" * 70)
print(f"Diagnosing Sink Connector Failure: {CONNECTOR_NAME}")
print("=" * 70)

kafka_client = KafkaConnectClient(base_url=KAFKA_CONNECT_URL)

try:
    # Get connector status
    print(f"\n1. Checking Connector Status...\n")
    status = kafka_client.get_connector_status(CONNECTOR_NAME)
    
    connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
    connector_worker_id = status.get('connector', {}).get('worker_id', 'UNKNOWN')
    
    print(f"   Connector State: {connector_state}")
    print(f"   Worker ID: {connector_worker_id}")
    
    # Check tasks
    tasks = status.get('tasks', [])
    print(f"\n   Tasks: {len(tasks)}")
    
    for i, task in enumerate(tasks):
        task_id = task.get('id', i)
        task_state = task.get('state', 'UNKNOWN')
        task_worker_id = task.get('worker_id', 'UNKNOWN')
        
        print(f"\n   Task {task_id}:")
        print(f"      State: {task_state}")
        print(f"      Worker ID: {task_worker_id}")
        
        if task_state == 'FAILED':
            trace = task.get('trace', 'No trace available')
            print(f"\n      ❌ TASK FAILED!")
            print(f"      Error Trace:")
            print(f"      {'-' * 60}")
            # Print first 2000 characters of trace
            print(f"      {trace[:2000]}")
            if len(trace) > 2000:
                print(f"      ... (truncated, {len(trace)} total characters)")
            print(f"      {'-' * 60}")
    
    # Get connector configuration
    print(f"\n2. Checking Connector Configuration...\n")
    config = kafka_client.get_connector_config(CONNECTOR_NAME)
    
    print(f"   Key Configuration Values:")
    print(f"      connector.class: {config.get('connector.class', 'NOT SET')}")
    print(f"      topics: {config.get('topics', 'NOT SET')}")
    print(f"      s3.bucket.name: {config.get('s3.bucket.name', 'NOT SET')}")
    print(f"      s3.region: {config.get('s3.region', 'NOT SET')}")
    print(f"      s3.prefix: {config.get('s3.prefix', 'NOT SET')}")
    print(f"      flush.size: {config.get('flush.size', 'NOT SET')}")
    print(f"      aws.access.key.id: {config.get('aws.access.key.id', 'NOT SET')[:10]}... (hidden)")
    print(f"      aws.secret.access.key: {'SET' if config.get('aws.secret.access.key') else 'NOT SET'} (hidden)")
    print(f"      format.class: {config.get('format.class', 'NOT SET')}")
    print(f"      storage.class: {config.get('storage.class', 'NOT SET')}")
    
    # Common issues to check
    print(f"\n3. Common Issues Check...\n")
    
    issues = []
    
    # Check if topics exist
    topics = config.get('topics', '')
    if not topics:
        issues.append("❌ No topics configured")
    else:
        print(f"   ✅ Topics configured: {topics}")
    
    # Check AWS credentials
    if not config.get('aws.access.key.id'):
        issues.append("❌ AWS access key ID not set")
    else:
        print(f"   ✅ AWS access key ID is set")
    
    if not config.get('aws.secret.access.key'):
        issues.append("❌ AWS secret access key not set")
    else:
        print(f"   ✅ AWS secret access key is set")
    
    # Check bucket name
    bucket = config.get('s3.bucket.name', '')
    if not bucket:
        issues.append("❌ S3 bucket name not set")
    else:
        print(f"   ✅ S3 bucket name: {bucket}")
    
    # Check region
    region = config.get('s3.region', '')
    if not region:
        issues.append("❌ S3 region not set")
    else:
        print(f"   ✅ S3 region: {region}")
    
    if issues:
        print(f"\n   Issues Found:")
        for issue in issues:
            print(f"      {issue}")
    
    print(f"\n4. Recommendations...\n")
    
    if any(task.get('state') == 'FAILED' for task in tasks):
        print("   Since task is FAILED, try:")
        print("   1. Check the error trace above for specific error message")
        print("   2. Common causes:")
        print("      - Invalid AWS credentials")
        print("      - S3 bucket doesn't exist or wrong region")
        print("      - Network/firewall blocking S3 access")
        print("      - Kafka topic doesn't exist or has no messages")
        print("      - Invalid connector configuration")
        print("   3. Fix the issue and restart the connector")
        print("   4. Check Kafka Connect logs for more details")
    
except Exception as e:
    print(f"\n❌ Error diagnosing connector: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*70}")
print("Next Steps:")
print("  1. Review the error trace above")
print("  2. Fix any configuration issues")
print("  3. Restart the connector in Kafka UI")
print("  4. Monitor connector status")
print(f"{'='*70}")

