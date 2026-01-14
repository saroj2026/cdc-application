#!/bin/bash
# Check Kafka Connect status and AS400 connector availability

VPS_HOST="72.61.233.209"

echo "=================================================================================="
echo "🔍 CHECKING KAFKA CONNECT STATUS"
echo "=================================================================================="
echo ""

echo "Checking Kafka Connect at http://$VPS_HOST:8083..."
echo ""

# Check if Kafka Connect is accessible
if curl -s --max-time 5 "http://$VPS_HOST:8083/" > /dev/null 2>&1; then
    echo "✅ Kafka Connect is accessible"
else
    echo "❌ Kafka Connect is NOT accessible"
    echo "   Check if the service is running on the VPS"
    exit 1
fi

echo ""

# Check connector plugins
echo "Checking available connector plugins..."
PLUGINS=$(curl -s --max-time 5 "http://$VPS_HOST:8083/connector-plugins" 2>/dev/null)

if [ $? -eq 0 ] && [ -n "$PLUGINS" ]; then
    echo "✅ Connector plugins endpoint is accessible"
    
    # Check for AS400 connector
    if echo "$PLUGINS" | grep -qi "As400RpcConnector\|db2as400"; then
        echo "✅ AS400 connector plugin is AVAILABLE"
        echo ""
        echo "AS400 connector details:"
        echo "$PLUGINS" | python3 -m json.tool 2>/dev/null | grep -A 10 -i "As400RpcConnector\|db2as400" || \
        echo "$PLUGINS" | grep -i "As400RpcConnector\|db2as400" -A 5
    else
        echo "❌ AS400 connector plugin is NOT available"
        echo ""
        echo "Available Debezium connectors:"
        echo "$PLUGINS" | python3 -m json.tool 2>/dev/null | grep -E '"class"' | grep -i "debezium" | head -10 || \
        echo "$PLUGINS" | grep -i "debezium" | head -10
        echo ""
        echo "⚠️  You need to install the AS400 connector plugin on the VPS server"
        echo "   See: FIX_AS400_500_ERROR.md"
    fi
else
    echo "❌ Cannot access connector plugins endpoint"
    echo "   Kafka Connect may be returning 500 errors"
    echo ""
    echo "⚠️  You need to fix Kafka Connect on the VPS server"
    echo "   See: FIX_AS400_500_ERROR.md"
fi

echo ""
echo "=================================================================================="
echo "Next steps:"
echo "1. If AS400 connector is missing, fix it on VPS: FIX_AS400_500_ERROR.md"
echo "2. Then try starting the pipeline again: python3 start_as400_pipeline.py"
echo "=================================================================================="

