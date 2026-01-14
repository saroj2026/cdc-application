"""Restart Kafka Connect connector to apply new configuration."""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(__file__))

from ingestion.kafka_connect_client import KafkaConnectClient

CONNECTOR_NAME = "sink-as400-s3_p-s3-dbo"
KAFKA_CONNECT_URL = os.getenv("KAFKA_CONNECT_URL", "http://72.61.233.209:8083")

print("=" * 70)
print(f"Restarting Connector: {CONNECTOR_NAME}")
print("=" * 70)

kafka_client = KafkaConnectClient(base_url=KAFKA_CONNECT_URL)

try:
    # Restart connector
    print(f"\n1. Restarting connector...\n")
    kafka_client.restart_connector(CONNECTOR_NAME)
    print(f"   ✅ Restart command sent!")
    
    # Wait a bit for restart to initiate
    print(f"\n2. Waiting for connector to restart...\n")
    time.sleep(5)
    
    # Check status
    print(f"3. Checking connector status...\n")
    max_wait = 60  # Wait up to 60 seconds
    wait_interval = 5
    waited = 0
    
    while waited < max_wait:
        status = kafka_client.get_connector_status(CONNECTOR_NAME)
        connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
        tasks = status.get('tasks', [])
        
        print(f"   Status check ({waited}s): Connector={connector_state}, ", end="")
        if tasks:
            task_states = [task.get('state', 'UNKNOWN') for task in tasks]
            print(f"Tasks={task_states}")
            
            # Check if all tasks are running
            if connector_state == 'RUNNING' and all(state == 'RUNNING' for state in task_states):
                print(f"\n   ✅ Connector is RUNNING successfully!")
                print(f"   All tasks are running - data should be flowing to S3!")
                break
            elif any(state == 'FAILED' for state in task_states):
                # Check if it's still the old error or a new one
                failed_task = next((t for t in tasks if t.get('state') == 'FAILED'), None)
                if failed_task:
                    trace = failed_task.get('trace', '')
                    if 'AWS Access Key Id you provided does not exist' in trace:
                        print(f"\n   ⚠️  Still showing old error - may need more time or manual restart")
                    else:
                        print(f"\n   ⚠️  New error detected:")
                        print(f"      {trace[:300]}...")
        else:
            print(f"No tasks")
        
        if waited < max_wait - wait_interval:
            time.sleep(wait_interval)
            waited += wait_interval
        else:
            break
    
    # Final status check
    print(f"\n4. Final Status:\n")
    status = kafka_client.get_connector_status(CONNECTOR_NAME)
    connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
    print(f"   Connector State: {connector_state}")
    
    tasks = status.get('tasks', [])
    for i, task in enumerate(tasks):
        task_state = task.get('state', 'UNKNOWN')
        print(f"   Task {i} State: {task_state}")
        
        if task_state == 'FAILED':
            trace = task.get('trace', '')
            if 'AWS Access Key Id' in trace:
                print(f"      ⚠️  AWS credentials error - verify credentials are correct")
            else:
                print(f"      ⚠️  Error: {trace[:200]}...")
        elif task_state == 'RUNNING':
            print(f"      ✅ Task is running!")
    
    print(f"\n{'='*70}")
    if connector_state == 'RUNNING' and all(task.get('state') == 'RUNNING' for task in tasks):
        print("✅ SUCCESS! Connector is running and data should be flowing to S3!")
    else:
        print("⚠️  Connector may need manual restart in Kafka UI:")
        print(f"   http://72.61.233.209:8080/ui/clusters/local/connectors/{CONNECTOR_NAME}")
    print(f"{'='*70}")
    
except Exception as e:
    print(f"\n❌ Error restarting connector: {e}")
    import traceback
    traceback.print_exc()
    print(f"\nPlease restart manually in Kafka UI:")
    print(f"   http://72.61.233.209:8080/ui/clusters/local/connectors/{CONNECTOR_NAME}")
    sys.exit(1)



