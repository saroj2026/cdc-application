#!/bin/bash

# Script to check Kafka Connect logs for sink connector errors
# Run this script on the Kafka Connect server (72.61.233.209)

echo "=================================================================================="
echo "🔍 CHECKING KAFKA CONNECT LOGS FOR SINK CONNECTOR ERRORS"
echo "=================================================================================="
echo ""

# Find Kafka Connect container
echo "1. Finding Kafka Connect container..."
CONNECT_CONTAINER=$(docker ps | grep -i connect | awk '{print $1}')

if [ -z "$CONNECT_CONTAINER" ]; then
    echo "   ❌ Kafka Connect container not found"
    echo "   Trying alternative methods..."
    
    # Try finding by name
    CONNECT_CONTAINER=$(docker ps -a | grep -i connect | awk '{print $1}')
    if [ -z "$CONNECT_CONTAINER" ]; then
        echo "   ❌ Still not found. Checking all containers..."
        docker ps
        exit 1
    fi
fi

echo "   ✅ Found container: $CONNECT_CONTAINER"
echo ""

# Check logs for sink connector errors
echo "2. Checking logs for sink-pg_sql_p-mssql-dbo errors..."
echo "   (Last 200 lines filtered for errors)"
echo ""
docker logs "$CONNECT_CONTAINER" 2>&1 | grep -i "sink-pg_sql_p\|error\|exception\|transform\|ExtractField\|SQLException\|JDBC" | tail -200

echo ""
echo "=================================================================================="
echo "3. Checking for recent errors (last 50 lines of full log)..."
echo "=================================================================================="
docker logs "$CONNECT_CONTAINER" 2>&1 | tail -50

echo ""
echo "=================================================================================="
echo "4. Checking connector status via REST API..."
echo "=================================================================================="
curl -s http://localhost:8083/connectors/sink-pg_sql_p-mssql-dbo/status | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8083/connectors/sink-pg_sql_p-mssql-dbo/status

echo ""
echo "=================================================================================="
echo "✅ Log check complete!"
echo "=================================================================================="
echo ""
echo "Look for errors related to:"
echo "  - ExtractField transform failures"
echo "  - SQL Server connection errors"
echo "  - Table name format issues"
echo "  - Message format mismatches"
echo "  - JDBC errors"


