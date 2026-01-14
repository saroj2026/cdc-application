#!/bin/bash
# Update Kafka Connect connector configuration via SSH

VPS_HOST="72.61.233.209"
VPS_USER="root"
VPS_PASS="segmbp@1100"
CONNECTOR_NAME="sink-as400-s3_p-s3-dbo"
KAFKA_CONNECT_URL="http://localhost:8083"

# AWS Credentials
ACCESS_KEY="AKIATLTXNANW2EV7QGV2"
SECRET_KEY="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"

echo "======================================================================"
echo "Updating Kafka Connect Connector via SSH"
echo "======================================================================"

# Step 1: Get current configuration
echo ""
echo "1. Getting current connector configuration..."
CURRENT_CONFIG=$(sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST \
  "docker exec kafka-connect-cdc curl -s $KAFKA_CONNECT_URL/connectors/$CONNECTOR_NAME/config")

if [ $? -ne 0 ]; then
    echo "❌ Failed to get current configuration"
    exit 1
fi

echo "   ✅ Retrieved current configuration"

# Step 2: Update credentials in config (using jq if available, or sed)
echo ""
echo "2. Updating AWS credentials in configuration..."

# Create updated config JSON
UPDATED_CONFIG=$(echo "$CURRENT_CONFIG" | python3 -c "
import sys, json
config = json.load(sys.stdin)
config['aws.access.key.id'] = '$ACCESS_KEY'
config['aws.secret.access.key'] = '$SECRET_KEY'
print(json.dumps(config))
" 2>/dev/null)

if [ -z "$UPDATED_CONFIG" ]; then
    echo "   ⚠️  Python not available, using sed method..."
    # Fallback: use sed to replace values
    UPDATED_CONFIG=$(echo "$CURRENT_CONFIG" | \
        sed "s/\"aws.access.key.id\":[^,}]*/\"aws.access.key.id\": \"$ACCESS_KEY\"/" | \
        sed "s/\"aws.secret.access.key\":[^,}]*/\"aws.secret.access.key\": \"$SECRET_KEY\"/")
fi

# Step 3: Update connector configuration
echo ""
echo "3. Updating connector configuration via REST API..."

RESPONSE=$(sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST \
  "docker exec kafka-connect-cdc curl -s -X PUT \
    -H 'Content-Type: application/json' \
    -d '$UPDATED_CONFIG' \
    $KAFKA_CONNECT_URL/connectors/$CONNECTOR_NAME/config")

if [ $? -eq 0 ]; then
    echo "   ✅ Configuration updated successfully!"
else
    echo "   ❌ Failed to update configuration"
    exit 1
fi

# Step 4: Restart connector
echo ""
echo "4. Restarting connector..."
sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST \
  "docker exec kafka-connect-cdc curl -s -X POST $KAFKA_CONNECT_URL/connectors/$CONNECTOR_NAME/restart" > /dev/null

if [ $? -eq 0 ]; then
    echo "   ✅ Restart command sent!"
else
    echo "   ⚠️  Restart command may have failed"
fi

# Step 5: Wait and check status
echo ""
echo "5. Waiting 30 seconds and checking status..."
sleep 30

STATUS=$(sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST \
  "docker exec kafka-connect-cdc curl -s $KAFKA_CONNECT_URL/connectors/$CONNECTOR_NAME/status")

echo ""
echo "Connector Status:"
echo "$STATUS" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f\"   Connector State: {data.get('connector', {}).get('state', 'UNKNOWN')}\")
    for i, task in enumerate(data.get('tasks', [])):
        print(f\"   Task {i} State: {task.get('state', 'UNKNOWN')}\")
        if task.get('state') == 'FAILED':
            trace = task.get('trace', '')[:200]
            print(f\"      Error: {trace}...\")
except:
    print(\"   Could not parse status\")
" 2>/dev/null || echo "$STATUS"

echo ""
echo "======================================================================"
echo "Update Complete!"
echo "======================================================================"



