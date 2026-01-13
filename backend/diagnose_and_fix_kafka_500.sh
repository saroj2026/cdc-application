#!/bin/bash
# Diagnose and fix Kafka Connect 500 errors for AS400

echo "=================================================================================="
echo "🔍 DIAGNOSING KAFKA CONNECT 500 ERROR"
echo "=================================================================================="
echo ""

VPS_HOST="72.61.233.209"
VPS_USER="root"
CONTAINER_NAME="kafka-connect-cdc"

echo "This script will help you fix the Kafka Connect 500 error."
echo "The error indicates the AS400 connector plugin is missing or not loaded."
echo ""
echo "You need to run these commands on the VPS server: $VPS_HOST"
echo ""

cat << 'INSTRUCTIONS'
================================================================================
STEP-BY-STEP FIX (Run on VPS Server)
================================================================================

1. SSH to the VPS server:
   ssh root@72.61.233.209
   # Password: segmbp@1100

2. Check if connector exists in container:
   docker exec kafka-connect-cdc find /usr/share/java/plugins -type d -name "*ibmi*" -o -name "*db2as400*"

3. If not found, check host path:
   find /opt/cdc3/connect-plugins -type d -name "*ibmi*" -o -name "*db2as400*"

4. If found on host, copy to container:
   CONNECTOR=$(find /opt/cdc3/connect-plugins -type d -name "*ibmi*" | head -1)
   docker cp "$CONNECTOR" kafka-connect-cdc:/usr/share/java/plugins/$(basename $CONNECTOR)

5. Restart Kafka Connect:
   docker restart kafka-connect-cdc
   sleep 30

6. Verify connector is loaded:
   curl -s http://localhost:8083/connector-plugins | grep -i "As400RpcConnector"

================================================================================
QUICK FIX SCRIPT (Copy to VPS and run)
================================================================================

Copy this entire block and paste it on the VPS server:

cat > /tmp/fix_as400_connector.sh << 'SCRIPT'
#!/bin/bash
CONTAINER_NAME="kafka-connect-cdc"
echo "Checking for AS400 connector..."
CONNECTOR=$(docker exec $CONTAINER_NAME find /usr/share/java/plugins -type d \( -name "*ibmi*" -o -name "*db2as400*" \) 2>/dev/null | head -1)

if [ -z "$CONNECTOR" ]; then
    echo "Connector not found in container. Checking host..."
    HOST_CONNECTOR=$(find /opt/cdc3/connect-plugins -type d \( -name "*ibmi*" -o -name "*db2as400*" \) 2>/dev/null | head -1)
    
    if [ -n "$HOST_CONNECTOR" ]; then
        echo "Found on host: $HOST_CONNECTOR"
        echo "Copying to container..."
        docker cp "$HOST_CONNECTOR" "$CONTAINER_NAME:/usr/share/java/plugins/$(basename $HOST_CONNECTOR)"
        echo "✅ Copied"
    else
        echo "❌ Connector not found on host either!"
        echo "Please download debezium-connector-ibmi first"
        exit 1
    fi
else
    echo "✅ Connector found: $CONNECTOR"
fi

echo ""
echo "Restarting Kafka Connect..."
docker restart $CONTAINER_NAME
echo "Waiting 30 seconds..."
sleep 30

echo ""
echo "Verifying connector is loaded..."
curl -s http://localhost:8083/connector-plugins | grep -i "As400RpcConnector" && echo "✅ SUCCESS!" || echo "⚠️  May need more time"
SCRIPT

chmod +x /tmp/fix_as400_connector.sh
/tmp/fix_as400_connector.sh

================================================================================
INSTRUCTIONS

echo ""
echo "After fixing on the VPS, try starting the pipeline again:"
echo "  python3 start_as400_pipeline.py"
echo ""

