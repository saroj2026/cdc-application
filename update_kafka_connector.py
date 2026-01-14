"""Update Kafka Connect S3 sink connector with new AWS credentials."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ingestion.kafka_connect_client import KafkaConnectClient

CONNECTOR_NAME = "sink-as400-s3_p-s3-dbo"
KAFKA_CONNECT_URL = os.getenv("KAFKA_CONNECT_URL", "http://72.61.233.209:8083")

# New AWS credentials
NEW_ACCESS_KEY = "AKIATLTXNANW2JU6WWAH"
NEW_SECRET_KEY = "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"

print("=" * 70)
print(f"Updating Kafka Connect Connector: {CONNECTOR_NAME}")
print("=" * 70)

kafka_client = KafkaConnectClient(base_url=KAFKA_CONNECT_URL)

try:
    # Get current configuration
    print(f"\n1. Getting current connector configuration...\n")
    current_config = kafka_client.get_connector_config(CONNECTOR_NAME)
    
    print(f"   Current aws.access.key.id: {current_config.get('aws.access.key.id', 'NOT SET')[:20]}...")
    print(f"   Current aws.secret.access.key: {'SET' if current_config.get('aws.secret.access.key') else 'NOT SET'}")
    
    # Update credentials
    print(f"\n2. Updating AWS credentials...\n")
    current_config['aws.access.key.id'] = NEW_ACCESS_KEY
    current_config['aws.secret.access.key'] = NEW_SECRET_KEY
    
    # Update connector configuration
    print(f"   Updating connector configuration...")
    kafka_client.update_connector(CONNECTOR_NAME, current_config)
    
    print(f"   ✅ Connector configuration updated!")
    print(f"   New aws.access.key.id: {NEW_ACCESS_KEY}")
    print(f"   New aws.secret.access.key: {'SET' if NEW_SECRET_KEY else 'NOT SET'}")
    
    # Verify the update
    print(f"\n3. Verifying update...\n")
    updated_config = kafka_client.get_connector_config(CONNECTOR_NAME)
    
    if updated_config.get('aws.access.key.id') == NEW_ACCESS_KEY:
        print(f"   ✅ Verified: aws.access.key.id updated correctly")
    else:
        print(f"   ⚠️  Warning: aws.access.key.id doesn't match expected value")
    
    if updated_config.get('aws.secret.access.key'):
        print(f"   ✅ Verified: aws.secret.access.key is set")
    else:
        print(f"   ⚠️  Warning: aws.secret.access.key is not set")
    
    # Check connector status
    print(f"\n4. Checking connector status...\n")
    status = kafka_client.get_connector_status(CONNECTOR_NAME)
    connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
    print(f"   Connector State: {connector_state}")
    
    tasks = status.get('tasks', [])
    for i, task in enumerate(tasks):
        task_state = task.get('state', 'UNKNOWN')
        print(f"   Task {i} State: {task_state}")
        
        if task_state == 'FAILED':
            trace = task.get('trace', 'No error details')
            print(f"      ⚠️  Error: {trace[:300]}...")
        elif task_state == 'RUNNING':
            print(f"      ✅ Task is running successfully!")
    
    print(f"\n{'='*70}")
    print("Update Complete!")
    print(f"{'='*70}")
    
    if connector_state == 'RUNNING' and all(task.get('state') == 'RUNNING' for task in tasks):
        print("\n✅ Connector is RUNNING - data should be flowing to S3!")
    else:
        print("\n⚠️  Connector needs to be restarted:")
        print("   1. Go to Kafka UI: http://72.61.233.209:8080")
        print(f"   2. Find connector: {CONNECTOR_NAME}")
        print("   3. Click 'Restart' button")
        print("   4. Wait 30-60 seconds")
        print("   5. Verify status is RUNNING")
    
except Exception as e:
    print(f"\n❌ Error updating connector: {e}")
    import traceback
    traceback.print_exc()
    print(f"\nYou may need to update manually in Kafka UI:")
    print(f"   http://72.61.233.209:8080/ui/clusters/local/connectors/{CONNECTOR_NAME}")
    sys.exit(1)



