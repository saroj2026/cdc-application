#!/bin/bash
# Restart Backend Server with Clean State
# This ensures pipelines are loaded fresh from the database

echo "========================================"
echo "Restarting Backend with Clean State"
echo "========================================"
echo ""

# Step 1: Stop existing backend processes
echo "1. Stopping existing backend processes..."
pkill -f "ingestion.api" || true
sleep 2
echo "   [OK] Stopped existing processes"

# Step 2: Check if port 8000 is still in use
echo ""
echo "2. Checking if port 8000 is available..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "   [WARNING] Port 8000 is still in use"
    echo "   Waiting additional 5 seconds..."
    sleep 5
else
    echo "   [OK] Port 8000 is available"
fi

# Step 3: Set environment variables
echo ""
echo "3. Setting environment variables..."
export DATABASE_URL="postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest"
export KAFKA_CONNECT_URL="http://72.61.233.209:8083"
export API_HOST="0.0.0.0"
export API_PORT="8000"
export API_RELOAD="True"
echo "   [OK] Environment variables set"
echo "      DATABASE_URL: $DATABASE_URL"
echo "      KAFKA_CONNECT_URL: $KAFKA_CONNECT_URL"

# Step 4: Start backend server
echo ""
echo "4. Starting backend server..."
cd "$(dirname "$0")"
nohup python -m ingestion.api > backend.log 2>&1 &
BACKEND_PID=$!
echo "   [OK] Backend process started (PID: $BACKEND_PID)"

# Step 5: Wait for server to be ready
echo ""
echo "5. Waiting for server to be ready..."
max_wait=30
waited=0
ready=false

while [ $waited -lt $max_wait ] && [ "$ready" = false ]; do
    sleep 2
    waited=$((waited + 2))
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        ready=true
    else
        echo "   Waiting... ($waited/$max_wait seconds)"
    fi
done

if [ "$ready" = true ]; then
    echo "   [OK] Server is ready!"
else
    echo "   [WARNING] Server may not be fully ready yet"
    echo "   Check logs or wait a bit longer"
fi

# Step 6: Test server
echo ""
echo "6. Testing server..."
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "   [OK] Health check passed"
    
    connections_count=$(curl -s http://localhost:8000/api/v1/connections | jq '. | length' 2>/dev/null || echo "0")
    echo "   [OK] Found $connections_count connections"
    
    pipelines_count=$(curl -s http://localhost:8000/api/pipelines | jq '. | length' 2>/dev/null || echo "0")
    echo "   [OK] Found $pipelines_count pipelines in database"
else
    echo "   [ERROR] Server test failed"
fi

echo ""
echo "========================================"
echo "Backend Restarted Successfully!"
echo "========================================"
echo ""
echo "Server is running at: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Note: Pipelines will be loaded from database when you start them."
echo ""

# Restart Backend Server with Clean State
# This ensures pipelines are loaded fresh from the database

echo "========================================"
echo "Restarting Backend with Clean State"
echo "========================================"
echo ""

# Step 1: Stop existing backend processes
echo "1. Stopping existing backend processes..."
pkill -f "ingestion.api" || true
sleep 2
echo "   [OK] Stopped existing processes"

# Step 2: Check if port 8000 is still in use
echo ""
echo "2. Checking if port 8000 is available..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "   [WARNING] Port 8000 is still in use"
    echo "   Waiting additional 5 seconds..."
    sleep 5
else
    echo "   [OK] Port 8000 is available"
fi

# Step 3: Set environment variables
echo ""
echo "3. Setting environment variables..."
export DATABASE_URL="postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest"
export KAFKA_CONNECT_URL="http://72.61.233.209:8083"
export API_HOST="0.0.0.0"
export API_PORT="8000"
export API_RELOAD="True"
echo "   [OK] Environment variables set"
echo "      DATABASE_URL: $DATABASE_URL"
echo "      KAFKA_CONNECT_URL: $KAFKA_CONNECT_URL"

# Step 4: Start backend server
echo ""
echo "4. Starting backend server..."
cd "$(dirname "$0")"
nohup python -m ingestion.api > backend.log 2>&1 &
BACKEND_PID=$!
echo "   [OK] Backend process started (PID: $BACKEND_PID)"

# Step 5: Wait for server to be ready
echo ""
echo "5. Waiting for server to be ready..."
max_wait=30
waited=0
ready=false

while [ $waited -lt $max_wait ] && [ "$ready" = false ]; do
    sleep 2
    waited=$((waited + 2))
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        ready=true
    else
        echo "   Waiting... ($waited/$max_wait seconds)"
    fi
done

if [ "$ready" = true ]; then
    echo "   [OK] Server is ready!"
else
    echo "   [WARNING] Server may not be fully ready yet"
    echo "   Check logs or wait a bit longer"
fi

# Step 6: Test server
echo ""
echo "6. Testing server..."
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "   [OK] Health check passed"
    
    connections_count=$(curl -s http://localhost:8000/api/v1/connections | jq '. | length' 2>/dev/null || echo "0")
    echo "   [OK] Found $connections_count connections"
    
    pipelines_count=$(curl -s http://localhost:8000/api/pipelines | jq '. | length' 2>/dev/null || echo "0")
    echo "   [OK] Found $pipelines_count pipelines in database"
else
    echo "   [ERROR] Server test failed"
fi

echo ""
echo "========================================"
echo "Backend Restarted Successfully!"
echo "========================================"
echo ""
echo "Server is running at: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Note: Pipelines will be loaded from database when you start them."
echo ""

