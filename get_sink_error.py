"""Get detailed error information for failed sink connector."""
import requests
import json

CONNECTOR_NAME = "sink-as400-s3_p-s3-dbo"
KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

print("=" * 70)
print(f"Getting Error Details for: {CONNECTOR_NAME}")
print("=" * 70)

try:
    # Get connector status
    print(f"\n1. Connector Status:\n")
    status_response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status", timeout=10)
    status = status_response.json()
    
    connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
    print(f"   Connector State: {connector_state}")
    
    tasks = status.get('tasks', [])
    print(f"   Tasks: {len(tasks)}\n")
    
    for i, task in enumerate(tasks):
        task_id = task.get('id', i)
        task_state = task.get('state', 'UNKNOWN')
        print(f"   Task {task_id}: {task_state}")
        
        if task_state == 'FAILED':
            trace = task.get('trace', 'No trace available')
            print(f"\n   ❌ ERROR TRACE:")
            print(f"   {'='*70}")
            print(f"   {trace}")
            print(f"   {'='*70}")
    
    # Get connector configuration
    print(f"\n2. Connector Configuration:\n")
    config_response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config", timeout=10)
    config = config_response.json()
    
    print(f"   Key Settings:")
    print(f"      topics: {config.get('topics', 'NOT SET')}")
    print(f"      s3.bucket.name: {config.get('s3.bucket.name', 'NOT SET')}")
    print(f"      s3.region: {config.get('s3.region', 'NOT SET')}")
    print(f"      s3.prefix: {config.get('s3.prefix', 'NOT SET')}")
    print(f"      flush.size: {config.get('flush.size', 'NOT SET')}")
    print(f"      format.class: {config.get('format.class', 'NOT SET')}")
    print(f"      storage.class: {config.get('storage.class', 'NOT SET')}")
    print(f"      aws.access.key.id: {config.get('aws.access.key.id', 'NOT SET')[:15]}...")
    print(f"      aws.secret.access.key: {'SET' if config.get('aws.secret.access.key') else 'NOT SET'}")
    
    # Common fixes
    print(f"\n3. Common Issues & Solutions:\n")
    print(f"   Based on the error trace above, common issues are:\n")
    print(f"   a) AWS Credentials:")
    print(f"      - Invalid access key ID or secret key")
    print(f"      - Solution: Verify AWS credentials in connector config\n")
    print(f"   b) S3 Bucket Access:")
    print(f"      - Bucket doesn't exist or wrong region")
    print(f"      - IAM permissions insufficient")
    print(f"      - Solution: Verify bucket name and IAM permissions\n")
    print(f"   c) Network/Firewall:")
    print(f"      - Kafka Connect can't reach S3")
    print(f"      - Solution: Check network connectivity to S3\n")
    print(f"   d) Topic Issues:")
    print(f"      - Topic doesn't exist or has no messages")
    print(f"      - Solution: Verify topic exists and has data\n")
    
except requests.exceptions.Timeout:
    print(f"\n❌ Connection timeout to Kafka Connect")
    print(f"   Please check the error in Kafka UI directly:")
    print(f"   http://72.61.233.209:8080/ui/clusters/local/connectors/{CONNECTOR_NAME}")
except requests.exceptions.RequestException as e:
    print(f"\n❌ Error: {e}")
    print(f"   Please check the error in Kafka UI directly:")
    print(f"   http://72.61.233.209:8080/ui/clusters/local/connectors/{CONNECTOR_NAME}")
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*70}")
print("Next Steps:")
print("  1. Review the error trace above")
print("  2. Click on the connector in Kafka UI to see full error details")
print("  3. Fix the configuration issue")
print("  4. Restart the connector")
print(f"{'='*70}")



