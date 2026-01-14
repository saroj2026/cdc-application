#!/bin/bash

# Script to SSH and check AS400 connector installation
# Note: IP address corrected to 72.61.233.209 (not 72.60.233.209)

SERVER="72.61.233.209"
USER="root"
PASSWORD="segmbp@1100"

echo "================================================================================
🔐 SSH CONNECTION AND AS400 CONNECTOR CHECK
================================================================================
"

echo "Connecting to $USER@$SERVER..."
echo "Password: $PASSWORD"
echo ""
echo "Note: If IP is 72.60.233.209, update SERVER variable in script"
echo ""

# Check if sshpass is available (for automated password entry)
if command -v sshpass &> /dev/null; then
    echo "Using sshpass for automated connection..."
    echo ""
    
    # Run commands on remote server
    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER << 'REMOTE_SCRIPT'
        echo "Connected! Checking AS400 connector installation..."
        echo ""
        
        # Find container
        CONTAINER=$(docker ps | grep -i connect | awk '{print $1}' | head -1)
        if [ -z "$CONTAINER" ]; then
            echo "❌ Kafka Connect container not found!"
            exit 1
        fi
        
        echo "Container: $CONTAINER"
        echo ""
        
        # Check connector directory
        echo "1. Checking connector directory..."
        if docker exec $CONTAINER test -d "/kafka/connect/debezium-connector-ibmi" 2>/dev/null; then
            echo "   ✅ Directory exists"
            JAR_COUNT=$(docker exec $CONTAINER ls -1 /kafka/connect/debezium-connector-ibmi/*.jar 2>/dev/null | wc -l)
            echo "   JAR files: $JAR_COUNT"
        else
            echo "   ❌ Directory NOT found"
        fi
        echo ""
        
        # Check if plugin is loaded
        echo "2. Checking if plugin is loaded..."
        AS400_FOUND=$(curl -s http://localhost:8083/connector-plugins 2>/dev/null | grep -i "As400RpcConnector\|db2as400" | wc -l)
        if [ "$AS400_FOUND" -gt 0 ]; then
            echo "   ✅ Plugin is loaded"
        else
            echo "   ❌ Plugin NOT loaded"
        fi
        echo ""
        
        # Check for errors
        echo "3. Checking for errors in logs..."
        ERRORS=$(docker logs $CONTAINER 2>&1 | tail -100 | grep -iE "error|exception|fatal" | grep -v "WARNING" | head -10)
        if [ -n "$ERRORS" ]; then
            echo "   Found errors:"
            echo "$ERRORS"
        else
            echo "   ✅ No errors found"
        fi
        echo ""
        
        echo "================================================================================
SUMMARY
================================================================================
"
        if docker exec $CONTAINER test -d "/kafka/connect/debezium-connector-ibmi" 2>/dev/null; then
            JAR_COUNT=$(docker exec $CONTAINER ls -1 /kafka/connect/debezium-connector-ibmi/*.jar 2>/dev/null | wc -l)
            if [ "$JAR_COUNT" -gt 0 ]; then
                echo "✅ Connector directory exists with $JAR_COUNT JAR file(s)"
            else
                echo "❌ Connector directory exists but NO JAR files"
            fi
        else
            echo "❌ Connector directory does NOT exist"
        fi
        
        AS400_FOUND=$(curl -s http://localhost:8083/connector-plugins 2>/dev/null | grep -i "As400RpcConnector\|db2as400" | wc -l)
        if [ "$AS400_FOUND" -gt 0 ]; then
            echo "✅ Plugin is loaded in Kafka Connect"
        else
            echo "❌ Plugin is NOT loaded (may need restart)"
        fi
        echo ""
REMOTE_SCRIPT

else
    echo "sshpass not found. Please run manually:"
    echo ""
    echo "ssh $USER@$SERVER"
    echo "# Password: $PASSWORD"
    echo ""
    echo "Then run these commands:"
    echo "  CONTAINER=\$(docker ps | grep -i connect | awk '{print \$1}' | head -1)"
    echo "  docker exec \$CONTAINER ls -la /kafka/connect/debezium-connector-ibmi"
    echo "  curl -s http://localhost:8083/connector-plugins | grep -i As400RpcConnector"
    echo ""
fi

echo ""
echo "================================================================================
"


