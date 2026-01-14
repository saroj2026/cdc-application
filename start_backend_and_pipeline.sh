#!/bin/bash
# Start backend and then start AS400-S3_P pipeline

cd "$(dirname "$0")"

echo "=================================================================================="
echo "🚀 STARTING BACKEND AND AS400-S3_P PIPELINE"
echo "=================================================================================="
echo ""

# Check if backend is already running
echo "Step 1: Checking if backend is running..."
if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "✅ Backend is already running"
    BACKEND_RUNNING=true
else
    echo "⚠️  Backend is not running"
    BACKEND_RUNNING=false
fi
echo ""

# Start backend if not running
if [ "$BACKEND_RUNNING" = false ]; then
    echo "Step 2: Starting backend..."
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
    
    echo "Starting backend in background..."
    nohup "$PWD/venv/bin/python" -m uvicorn ingestion.api:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
    BACKEND_PID=$!
    
    echo "Backend started with PID: $BACKEND_PID"
    echo "Waiting 10 seconds for backend to start..."
    sleep 10
    
    # Check if backend started successfully
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo "✅ Backend is now running"
    else
        echo "⚠️  Backend may still be starting. Check logs: tail -f backend.log"
        echo "Waiting 10 more seconds..."
        sleep 10
    fi
    echo ""
else
    echo "Step 2: Backend already running, skipping..."
    echo ""
fi

# Start pipeline
echo "Step 3: Starting AS400-S3_P pipeline..."
echo ""

python3 << 'PYEOF'
import requests
import sys
import time

API_BASE = "http://localhost:8000/api/v1"
PIPELINE_NAME = "AS400-S3_P"

def print_status(message, status="INFO"):
    colors = {"SUCCESS": "\033[92m", "ERROR": "\033[91m", "WARNING": "\033[93m", "INFO": "\033[94m", "RESET": "\033[0m"}
    symbols = {"SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️", "INFO": "ℹ️"}
    print(f"{colors.get(status, '')}{symbols.get(status, '')} {message}{colors['RESET']}")

try:
    # Get pipelines
    print_status(f"Looking for pipeline: {PIPELINE_NAME}", "INFO")
    response = requests.get(f"{API_BASE}/pipelines", timeout=10)
    response.raise_for_status()
    pipelines = response.json()
    
    pipeline = next((p for p in pipelines if p.get("name") == PIPELINE_NAME), None)
    
    if not pipeline:
        print_status(f"Pipeline '{PIPELINE_NAME}' not found", "ERROR")
        print("\nAvailable pipelines:")
        for p in pipelines:
            print(f"  - {p.get('name')} (ID: {p.get('id')})")
        sys.exit(1)
    
    pipeline_id = pipeline.get("id")
    current_status = pipeline.get("status")
    
    print_status(f"Found pipeline: {pipeline.get('name')} (ID: {pipeline_id})", "SUCCESS")
    print_status(f"Current status: {current_status}", "INFO")
    
    # Stop if running
    if current_status in ['RUNNING', 'STARTING', 'ACTIVE']:
        print_status("\nPipeline is already running. Stopping first...", "INFO")
        try:
            response = requests.post(f"{API_BASE}/pipelines/{pipeline_id}/stop", timeout=30)
            if response.status_code == 200:
                print_status("Pipeline stopped successfully", "SUCCESS")
                print_status("Waiting 5 seconds before restart...", "INFO")
                time.sleep(5)
        except Exception as e:
            print_status(f"Error stopping pipeline: {e}", "WARNING")
    
    # Start pipeline
    print_status("\nStarting pipeline...", "INFO")
    response = requests.post(f"{API_BASE}/pipelines/{pipeline_id}/start", timeout=60)
    
    if response.status_code == 200:
        result = response.json()
        print_status("Pipeline start requested successfully", "SUCCESS")
        
        if result.get("message"):
            print(f"  Message: {result['message']}")
        
        if result.get("full_load"):
            fl = result['full_load']
            print(f"\n  Full Load:")
            print(f"    Success: {fl.get('success', 'N/A')}")
            print(f"    Tables: {fl.get('tables_transferred', 0)}")
            print(f"    Rows: {fl.get('total_rows', 0)}")
        
        # Wait and check status
        print_status("\nWaiting 10 seconds for pipeline to start...", "INFO")
        time.sleep(10)
        
        # Get updated status
        print_status("Checking pipeline status...", "INFO")
        status_response = requests.get(f"{API_BASE}/pipelines/{pipeline_id}/status", timeout=10)
        if status_response.status_code == 200:
            status_data = status_response.json()
            
            print("\n" + "-"*70)
            print("PIPELINE STATUS")
            print("-"*70)
            print(f"  Status: {status_data.get('status')}")
            print(f"  CDC Status: {status_data.get('cdc_status')}")
            print(f"  Full Load Status: {status_data.get('full_load_status')}")
            
            if status_data.get('status') in ['RUNNING', 'STARTING']:
                print_status("\nPipeline is starting/running!", "SUCCESS")
            else:
                print_status(f"\nPipeline status: {status_data.get('status')}", "WARNING")
    else:
        print_status(f"Failed to start pipeline: {response.status_code}", "ERROR")
        print(f"  Response: {response.text}")
        sys.exit(1)
        
except requests.exceptions.ConnectionError:
    print_status("Cannot connect to backend. Is it running on http://localhost:8000?", "ERROR")
    print_status("Start backend first: ./start_backend_simple.sh", "INFO")
    sys.exit(1)
except Exception as e:
    print_status(f"Error: {e}", "ERROR")
    sys.exit(1)

print("\n" + "="*70)
print("Next steps:")
print("1. Monitor pipeline status: python3 check_as400_pipeline_cdc.py")
print("2. Check S3 data flow: python3 check_s3_sink_data.py")
print("3. View in frontend: http://localhost:3000/pipelines")
print("="*70 + "\n")
PYEOF

echo ""
echo "=================================================================================="
echo "✅ DONE"
echo "=================================================================================="
echo ""
echo "Backend is running. To stop it:"
echo "  pkill -f 'uvicorn ingestion.api'"
echo "  Or check backend.log for the PID"
echo ""

