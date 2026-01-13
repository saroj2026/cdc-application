#!/bin/bash
# Script to create fix_as400_500_quick.sh directly on VPS via SSH

VPS_HOST="72.61.233.209"
VPS_USER="root"
VPS_PASSWORD="segmbp@1100"

echo "Creating fix_as400_500_quick.sh on VPS server..."

# Create the script content
SCRIPT_CONTENT='#!/bin/bash
# Quick fix for Kafka Connect 500 errors - run on VPS server

echo "🔧 Quick Fix for Kafka Connect 500 Errors"
echo ""

CONTAINER_NAME="kafka-connect-cdc"

# Check if AS400 connector exists
echo "Checking for AS400 connector..."
CONNECTOR=$(docker exec $CONTAINER_NAME find /usr/share/java/plugins -type d \( -name "*ibmi*" -o -name "*db2as400*" \) 2>/dev/null | head -1)

if [ -z "$CONNECTOR" ]; then
    echo "❌ AS400 connector not found!"
    echo ""
    echo "Checking host path..."
    HOST_CONNECTOR=$(find /opt/cdc3/connect-plugins -type d \( -name "*ibmi*" -o -name "*db2as400*" \) 2>/dev/null | head -1)
    
    if [ -n "$HOST_CONNECTOR" ]; then
        echo "✅ Found connector on host: $HOST_CONNECTOR"
        echo "Copying to container..."
        CONNECTOR_NAME=$(basename "$HOST_CONNECTOR")
        docker cp "$HOST_CONNECTOR" "$CONTAINER_NAME:/usr/share/java/plugins/$CONNECTOR_NAME"
        echo "✅ Copied"
    else
        echo "❌ Connector not found on host either!"
        echo "Please download debezium-connector-ibmi first"
        exit 1
    fi
else
    echo "✅ AS400 connector found: $CONNECTOR"
fi

echo ""
echo "Restarting Kafka Connect..."
docker restart $CONTAINER_NAME

echo ""
echo "Waiting 30 seconds for restart..."
sleep 30

echo ""
echo "Checking if connector is loaded..."
curl -s http://localhost:8083/connector-plugins | grep -i "As400RpcConnector\|db2as400" && echo "✅ Connector loaded!" || echo "⚠️  Connector may need more time to load"

echo ""
echo "✅ Done! Try starting the pipeline again."
'

# Use SSH to create the script on VPS
sshpass -p "$VPS_PASSWORD" ssh "$VPS_USER@$VPS_HOST" "cat > /tmp/fix_as400_500_quick.sh << 'SCRIPTEOF'
$SCRIPT_CONTENT
SCRIPTEOF
chmod +x /tmp/fix_as400_500_quick.sh
echo 'Script created at /tmp/fix_as400_500_quick.sh'
"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Script created successfully on VPS!"
    echo ""
    echo "To run it, SSH to the VPS and execute:"
    echo "  ssh $VPS_USER@$VPS_HOST"
    echo "  /tmp/fix_as400_500_quick.sh"
else
    echo ""
    echo "❌ Failed to create script. Try manually:"
    echo "  1. SSH to VPS: ssh $VPS_USER@$VPS_HOST"
    echo "  2. Copy the script content manually"
fi

