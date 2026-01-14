#!/bin/bash

# Restart Backend Script
cd "$(dirname "$0")"

echo "🔄 Restarting Backend Application..."
echo ""

# Kill existing backend processes
echo "1. Stopping existing backend processes..."
pkill -f "python.*api.py" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "ingestion.api" 2>/dev/null || true

# Wait for processes to stop
sleep 2

# Check if processes are still running
if pgrep -f "python.*api.py" > /dev/null || pgrep -f "uvicorn" > /dev/null; then
    echo "   ⚠️  Some processes still running, forcing kill..."
    pkill -9 -f "python.*api.py" 2>/dev/null || true
    pkill -9 -f "uvicorn" 2>/dev/null || true
    sleep 1
fi

echo "   ✅ Backend processes stopped"
echo ""

# Activate virtual environment
echo "2. Activating virtual environment..."
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "   ✅ Virtual environment activated"
else
    echo "   ❌ Virtual environment not found!"
    echo "   Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Set environment variables
export KAFKA_CONNECT_URL=http://72.61.233.209:8083
export KAFKA_BOOTSTRAP_SERVERS=72.61.233.209:9092
export DATABASE_URL=postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest
export API_HOST=0.0.0.0
export API_PORT=8000

echo ""
echo "3. Starting Backend API..."
echo "   URL: http://localhost:8000"
echo "   Kafka Connect: $KAFKA_CONNECT_URL"
echo "   Press Ctrl+C to stop"
echo ""

# Start backend
"$PWD/venv/bin/python" -m ingestion.api


