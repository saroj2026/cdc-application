"""Update S3 Sink Connector flush.size to 1 for immediate data writes."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ingestion.kafka_connect_client import KafkaConnectClient

# Sink connector name
SINK_CONNECTOR_NAME = "sink-as400-s3_p-s3-dbo"

print("=" * 70)
print("Updating S3 Sink Connector Flush Size")
print("=" * 70)

kafka_connect_url = os.getenv("KAFKA_CONNECT_URL", "http://72.61.233.209:8083")
kafka_client = KafkaConnectClient(kafka_connect_url)

try:
    # Get current connector configuration
    print(f"\n1. Getting current configuration for: {SINK_CONNECTOR_NAME}\n")
    current_config = kafka_client.get_connector_config(SINK_CONNECTOR_NAME)
    
    print("   Current flush.size:", current_config.get('flush.size', 'NOT SET'))
    
    # Update flush.size to 1
    print(f"\n2. Updating flush.size to 1 for immediate writes...\n")
    current_config['flush.size'] = '1'
    
    # Update the connector
    kafka_client.update_connector(SINK_CONNECTOR_NAME, current_config)
    
    print("   ✅ Connector configuration updated!")
    print("   New flush.size: 1")
    print("\n   The connector will now write to S3 immediately after each record.")
    print("   This means your record (id=333, name=KISHOR) should appear in S3 soon.")
    
    # Verify the update
    print(f"\n3. Verifying update...\n")
    updated_config = kafka_client.get_connector_config(SINK_CONNECTOR_NAME)
    print("   Verified flush.size:", updated_config.get('flush.size', 'NOT SET'))
    
    # Check connector status
    print(f"\n4. Checking connector status...\n")
    status = kafka_client.get_connector_status(SINK_CONNECTOR_NAME)
    connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
    print(f"   Connector State: {connector_state}")
    
    tasks = status.get('tasks', [])
    for i, task in enumerate(tasks):
        task_state = task.get('state', 'UNKNOWN')
        print(f"   Task {i} State: {task_state}")
        if task_state == 'FAILED':
            error = task.get('trace', 'No error details')
            print(f"      Error: {error[:200]}...")
    
    print("\n" + "=" * 70)
    print("✅ Update Complete!")
    print("=" * 70)
    print("\nNext Steps:")
    print("  1. Wait a few seconds for the connector to process pending records")
    print("  2. Check S3 bucket for the new record")
    print("  3. If data still doesn't appear, check connector logs for errors")
    
except Exception as e:
    print(f"\n❌ Error updating connector: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)



