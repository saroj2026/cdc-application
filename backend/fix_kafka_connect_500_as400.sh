#!/bin/bash
# Fix Kafka Connect 500 errors for AS400 pipeline

echo "=================================================================================="
echo "🔧 FIXING KAFKA CONNECT 500 ERRORS FOR AS400"
echo "=================================================================================="
echo ""

VPS_HOST="72.61.233.209"
VPS_USER="root"
VPS_PASSWORD="segmbp@1100"
CONTAINER_PLUGIN_PATH="/usr/share/java/plugins"
HOST_PLUGIN_PATH="/opt/cdc3/connect-plugins"

echo "This script will:"
echo "1. Check Kafka Connect container status"
echo "2. Verify AS400 connector plugin installation"
echo "3. Copy connector if needed"
echo "4. Restart Kafka Connect"
echo "5. Verify connector is loaded"
echo ""

echo "⚠️  You need to run this on the VPS server (72.61.233.209)"
echo "   Or use SSH/plink to execute these commands remotely"
echo ""

# Function to check connector
check_connector() {
    echo "Step 1: Finding Kafka Connect container..."
    CONTAINER_NAME="kafka-connect-cdc"
    CONTAINER=$(docker ps --filter "name=$CONTAINER_NAME" --format "{{.ID}}" | head -1)
    
    if [ -z "$CONTAINER" ]; then
        echo "❌ Kafka Connect container '$CONTAINER_NAME' not found!"
        echo "   Available containers:"
        docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Status}}"
        return 1
    fi
    
    echo "✅ Found container: $CONTAINER_NAME ($CONTAINER)"
    echo ""
    
    echo "Step 2: Checking plugin directory..."
    if docker exec $CONTAINER_NAME ls -la $CONTAINER_PLUGIN_PATH 2>/dev/null; then
        echo "✅ Plugin directory exists"
    else
        echo "⚠️  Plugin directory not found, creating..."
        docker exec $CONTAINER_NAME mkdir -p $CONTAINER_PLUGIN_PATH
    fi
    echo ""
    
    echo "Step 3: Checking for AS400 connector..."
    CONNECTOR_FOUND=$(docker exec $CONTAINER_NAME find $CONTAINER_PLUGIN_PATH -type d \( -name "*ibmi*" -o -name "*db2as400*" -o -name "*as400*" \) 2>/dev/null | head -1)
    
    if [ -n "$CONNECTOR_FOUND" ]; then
        echo "✅ AS400 connector found at: $CONNECTOR_FOUND"
        docker exec $CONTAINER_NAME ls -la "$CONNECTOR_FOUND" | head -10
    else
        echo "❌ AS400 connector NOT found"
        return 2
    fi
    echo ""
    
    echo "Step 4: Checking if connector is loaded..."
    sleep 2
    PLUGINS=$(curl -s http://localhost:8083/connector-plugins 2>/dev/null | grep -i "As400RpcConnector\|db2as400" || echo "")
    
    if [ -n "$PLUGINS" ]; then
        echo "✅ AS400 connector is loaded in Kafka Connect"
        echo "$PLUGINS"
    else
        echo "⚠️  AS400 connector not loaded (may need restart)"
        return 3
    fi
    echo ""
    
    return 0
}

# Function to copy connector
copy_connector() {
    echo "Step 1: Finding connector on host..."
    CONNECTOR_PATH=$(find $HOST_PLUGIN_PATH -type d \( -name "*ibmi*" -o -name "*db2as400*" -o -name "*as400*" \) 2>/dev/null | head -1)
    
    if [ -z "$CONNECTOR_PATH" ]; then
        echo "❌ Connector not found at $HOST_PLUGIN_PATH"
        echo "   Please download debezium-connector-ibmi first"
        return 1
    fi
    
    echo "✅ Found connector: $CONNECTOR_PATH"
    echo ""
    
    echo "Step 2: Finding Kafka Connect container..."
    CONTAINER_NAME="kafka-connect-cdc"
    CONTAINER=$(docker ps --filter "name=$CONTAINER_NAME" --format "{{.ID}}" | head -1)
    
    if [ -z "$CONTAINER" ]; then
        echo "❌ Kafka Connect container '$CONTAINER_NAME' not found!"
        return 1
    fi
    
    echo "✅ Found container: $CONTAINER_NAME ($CONTAINER)"
    echo ""
    
    echo "Step 3: Copying connector to container..."
    CONNECTOR_NAME=$(basename "$CONNECTOR_PATH")
        docker cp "$CONNECTOR_PATH" "$CONTAINER_NAME:$CONTAINER_PLUGIN_PATH/$CONNECTOR_NAME"
    
    if [ $? -eq 0 ]; then
        echo "✅ Connector copied successfully"
    else
        echo "❌ Failed to copy connector"
        return 1
    fi
    echo ""
    
    echo "Step 4: Verifying copy..."
        docker exec $CONTAINER_NAME ls -la "$CONTAINER_PLUGIN_PATH/$CONNECTOR_NAME" | head -5
    echo ""
    
    return 0
}

# Function to restart Kafka Connect
restart_connect() {
    echo "Restarting Kafka Connect container..."
    CONTAINER_NAME="kafka-connect-cdc"
    CONTAINER=$(docker ps --filter "name=$CONTAINER_NAME" --format "{{.ID}}" | head -1)
    
    if [ -z "$CONTAINER" ]; then
        echo "❌ Kafka Connect container '$CONTAINER_NAME' not found!"
        return 1
    fi
    
    docker restart $CONTAINER_NAME
    echo "✅ Container restarted"
    echo ""
    
    echo "Waiting 30 seconds for Kafka Connect to start..."
    sleep 30
    echo ""
    
    echo "Checking Kafka Connect status..."
    curl -s http://localhost:8083/ | head -5 || echo "⚠️  Kafka Connect may still be starting..."
    echo ""
}

# Main execution
echo "Choose an option:"
echo "1. Check connector status"
echo "2. Copy connector from host to container"
echo "3. Restart Kafka Connect"
echo "4. Full fix (check, copy if needed, restart)"
echo ""
read -p "Enter option (1-4): " OPTION

case $OPTION in
    1)
        check_connector
        ;;
    2)
        copy_connector
        ;;
    3)
        restart_connect
        ;;
    4)
        echo "Running full fix..."
        check_connector
        STATUS=$?
        
        if [ $STATUS -eq 2 ]; then
            echo ""
            echo "Connector not found, attempting to copy..."
            copy_connector
            if [ $? -eq 0 ]; then
                echo ""
                restart_connect
                echo ""
                echo "Verifying fix..."
                check_connector
            fi
        elif [ $STATUS -eq 3 ]; then
            echo ""
            echo "Connector found but not loaded, restarting..."
            restart_connect
            echo ""
            echo "Verifying fix..."
            check_connector
        fi
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

echo ""
echo "=================================================================================="
echo "Next steps:"
echo "1. Try starting the pipeline again: ./quick_start_as400.sh"
echo "2. Check pipeline status: python3 check_as400_pipeline_cdc.py"
echo "=================================================================================="

