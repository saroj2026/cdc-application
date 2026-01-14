#!/bin/bash

# Simple Backend Start Script
cd "$(dirname "$0")"

echo "🚀 Starting Backend..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please create it first: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Set environment variables
export KAFKA_CONNECT_URL=http://72.61.233.209:8083
export KAFKA_BOOTSTRAP_SERVERS=72.61.233.209:9092
export DATABASE_URL=postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest
export API_HOST=0.0.0.0
export API_PORT=8000

echo "Environment:"
echo "  KAFKA_CONNECT_URL=$KAFKA_CONNECT_URL"
echo "  DATABASE_URL=$DATABASE_URL"
echo ""

# Use uvicorn directly
echo "Starting with uvicorn..."
"$PWD/venv/bin/python" -m uvicorn ingestion.api:app --host 0.0.0.0 --port 8000

