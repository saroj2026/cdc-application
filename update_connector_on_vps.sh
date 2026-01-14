#!/bin/bash
# Script to run directly on VPS to update connector configuration

CONNECTOR_NAME="sink-as400-s3_p-s3-dbo"
KAFKA_CONNECT_URL="http://localhost:8083"

# AWS Credentials
ACCESS_KEY="AKIATLTXNANW2EV7QGV2"
SECRET_KEY="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"

echo "======================================================================"
echo "Updating Kafka Connect Connector Configuration"
echo "======================================================================"

# Step 1: Get current configuration
echo ""
echo "1. Getting current connector configuration..."
CURRENT_CONFIG=$(docker exec kafka-connect-cdc curl -s $KAFKA_CONNECT_URL/connectors/$CONNECTOR_NAME/config)

if [ $? -ne 0 ] || [ -z "$CURRENT_CONFIG" ]; then
    echo "❌ Failed to get current configuration"
    exit 1
fi

echo "   ✅ Retrieved configuration"

# Step 2: Update credentials using Python (available in container)
echo ""
echo "2. Updating AWS credentials..."
UPDATED_CONFIG=$(echo "$CURRENT_CONFIG" | docker exec -i kafka-connect-cdc python3 -c "
import sys, json
config = json.load(sys.stdin)
config['aws.access.key.id'] = '$ACCESS_KEY'
config['aws.secret.access.key'] = '$SECRET_KEY'
print(json.dumps(config))
")

if [ -z "$UPDATED_CONFIG" ]; then
    echo "   ❌ Failed to update configuration"
    exit 1
fi

echo "   ✅ Updated credentials in configuration"

# Step 3: Update connector via REST API
echo ""
echo "3. Updating connector configuration via REST API..."
RESPONSE=$(echo "$UPDATED_CONFIG" | docker exec -i kafka-connect-cdc curl -s -X PUT \
    -H 'Content-Type: application/json' \
    -d @- \
    $KAFKA_CONNECT_URL/connectors/$CONNECTOR_NAME/config)

if [ $? -eq 0 ]; then
    echo "   ✅ Configuration updated successfully!"
else
    echo "   ❌ Failed to update configuration"
    exit 1
fi

# Step 4: Restart connector
echo ""
echo "4. Restarting connector..."
docker exec kafka-connect-cdc curl -s -X POST $KAFKA_CONNECT_URL/connectors/$CONNECTOR_NAME/restart > /dev/null

if [ $? -eq 0 ]; then
    echo "   ✅ Restart command sent!"
else
    echo "   ⚠️  Restart command may have failed"
fi

# Step 5: Wait and check status
echo ""
echo "5. Waiting 30 seconds and checking status..."
sleep 30

STATUS=$(docker exec kafka-connect-cdc curl -s $KAFKA_CONNECT_URL/connectors/$CONNECTOR_NAME/status)

echo ""
echo "Connector Status:"
echo "$STATUS" | docker exec -i kafka-connect-cdc python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f\"   Connector State: {data.get('connector', {}).get('state', 'UNKNOWN')}\")
    for i, task in enumerate(data.get('tasks', [])):
        state = task.get('state', 'UNKNOWN')
        print(f\"   Task {i} State: {state}\")
        if state == 'FAILED':
            trace = task.get('trace', '')[:300]
            print(f\"      Error: {trace}...\")
        elif state == 'RUNNING':
            print(f\"      ✅ Task is running!\")
except Exception as e:
    print(f\"   Error parsing status: {e}\")
    print(sys.stdin.read())
"

echo ""
echo "======================================================================"
echo "Update Complete!"
echo "======================================================================"



