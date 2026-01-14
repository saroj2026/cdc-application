#!/bin/bash

# Start Backend (FastAPI)
cd "$(dirname "$0")"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Set environment variables
export KAFKA_CONNECT_URL=http://72.61.233.209:8083
export KAFKA_BOOTSTRAP_SERVERS=72.61.233.209:9092
# PostgreSQL database on remote VPS Docker container
export DATABASE_URL=postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest
export API_HOST=0.0.0.0
export API_PORT=8000

echo "Starting Backend API on http://localhost:8000"
echo "Kafka Connect URL: $KAFKA_CONNECT_URL"
echo "Press Ctrl+C to stop"

# Use venv Python directly to ensure we're using the right environment
"$PWD/venv/bin/python" -m ingestion.api

