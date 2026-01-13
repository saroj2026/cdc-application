"""Check status of sink-as400-s3_p-s3-dbo connector."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ingestion.kafka_connect_client import KafkaConnectClient

CONNECTOR_NAME = "sink-as400-s3_p-s3-dbo"
KAFKA_CONNECT_URL = os.getenv("KAFKA_CONNECT_URL", "http://72.61.233.209:8083")

print("=" * 70)
print(f"Connector Status: {CONNECTOR_NAME}")
print("=" * 70)

kafka_client = KafkaConnectClient(base_url=KAFKA_CONNECT_URL)

try:
    # Get connector status
    print(f"\n1. Connector Status:\n")
    status = kafka_client.get_connector_status(CONNECTOR_NAME)
    
    connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
    connector_worker = status.get('connector', {}).get('worker_id', 'UNKNOWN')
    
    print(f"   State: {connector_state}")
    print(f"   Worker: {connector_worker}")
    
    # Check tasks
    tasks = status.get('tasks', [])
    print(f"\n2. Tasks ({len(tasks)}):\n")
    
    for i, task in enumerate(tasks):
        task_id = task.get('id', i)
        task_state = task.get('state', 'UNKNOWN')
        task_worker = task.get('worker_id', 'UNKNOWN')
        
        print(f"   Task {task_id}:")
        print(f"      State: {task_state}")
        print(f"      Worker: {task_worker}")
        
        if task_state == 'FAILED':
            trace = task.get('trace', '')
            print(f"      ❌ FAILED")
            print(f"      Error: {trace[:400]}...")
        elif task_state == 'RUNNING':
            print(f"      ✅ RUNNING")
    
    # Get configuration
    print(f"\n3. Configuration:\n")
    config = kafka_client.get_connector_config(CONNECTOR_NAME)
    
    print(f"   connector.class: {config.get('connector.class', 'NOT SET')}")
    print(f"   topics: {config.get('topics', 'NOT SET')}")
    print(f"   s3.bucket.name: {config.get('s3.bucket.name', 'NOT SET')}")
    print(f"   s3.region: {config.get('s3.region', 'NOT SET')}")
    print(f"   s3.prefix: {config.get('s3.prefix', 'NOT SET')}")
    print(f"   flush.size: {config.get('flush.size', 'NOT SET')}")
    print(f"   aws.access.key.id: {config.get('aws.access.key.id', 'NOT SET')[:20]}...")
    print(f"   aws.secret.access.key: {'SET' if config.get('aws.secret.access.key') else 'NOT SET'}")
    
    print(f"\n{'='*70}")
    if connector_state == 'RUNNING' and all(task.get('state') == 'RUNNING' for task in tasks):
        print("✅ Connector is RUNNING successfully!")
        print("Data should be flowing to S3 now.")
    elif connector_state == 'RUNNING' and any(task.get('state') == 'FAILED' for task in tasks):
        print("⚠️  Connector is RUNNING but task is FAILED")
        print("Check the error above for details.")
    else:
        print(f"⚠️  Connector state: {connector_state}")
        print("Connector may need to be restarted or has configuration issues.")
    print(f"{'='*70}")
    
except Exception as e:
    print(f"\n❌ Error checking connector: {e}")
    import traceback
    traceback.print_exc()
