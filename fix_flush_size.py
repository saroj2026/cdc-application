"""Quick fix: Update S3 sink connector flush.size to 1."""
import requests
import json

CONNECTOR_NAME = "sink-as400-s3_p-s3-dbo"
KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

print("Updating flush.size to 1...")

# Get current config
response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config")
config = response.json()

print(f"Current flush.size: {config.get('flush.size', 'NOT SET')}")

# Update flush.size
config['flush.size'] = '1'

# Update connector
update_response = requests.put(
    f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config",
    json=config,
    headers={"Content-Type": "application/json"}
)

if update_response.status_code == 200:
    print("✅ Updated! flush.size is now 1")
    print("Data will now write to S3 immediately after each record.")
else:
    print(f"❌ Error: {update_response.status_code}")
    print(update_response.text)



