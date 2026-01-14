#!/usr/bin/env python3
"""Start AS400-S3_P pipeline"""
import requests
import sys
import time

API_BASE_URL = "http://localhost:8000"
PIPELINE_NAME = "AS400-S3_P"

def print_status(message: str, status: str = "INFO"):
    """Print colored status message."""
    colors = {
        "SUCCESS": "\033[92m",  # Green
        "ERROR": "\033[91m",     # Red
        "WARNING": "\033[93m",   # Yellow
        "INFO": "\033[94m",      # Blue
        "RESET": "\033[0m"
    }
    symbol = {
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARNING": "⚠️",
        "INFO": "ℹ️"
    }
    print(f"{colors.get(status, '')}{symbol.get(status, '')} {message}{colors['RESET']}")

def main():
    """Start AS400 pipeline."""
    print("\n" + "="*70)
    print("🚀 STARTING AS400-S3_P PIPELINE")
    print("="*70 + "\n")
    
    # Check backend connectivity
    print_status("Checking backend connectivity...", "INFO")
    try:
        # Try multiple health endpoints
        health_endpoints = [
            f"{API_BASE_URL}/api/v1/health",
            f"{API_BASE_URL}/health",
            f"{API_BASE_URL}/docs",  # FastAPI docs endpoint
            f"{API_BASE_URL}/"  # Root endpoint
        ]
        
        connected = False
        for endpoint in health_endpoints:
            try:
                response = requests.get(endpoint, timeout=5)
                if response.status_code in [200, 404]:  # 404 is OK, means server is responding
                    print_status(f"Backend is accessible at {endpoint}", "SUCCESS")
                    connected = True
                    break
            except:
                continue
        
        if not connected:
            print_status("Cannot connect to backend. Is it running on http://localhost:8000?", "ERROR")
            print_status("Trying to continue anyway...", "WARNING")
    except Exception as e:
        print_status(f"Error connecting to backend: {e}", "WARNING")
        print_status("Trying to continue anyway...", "WARNING")
    
    # Find pipeline
    print_status(f"Looking for pipeline: {PIPELINE_NAME}", "INFO")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/pipelines", timeout=10)
        response.raise_for_status()
        pipelines = response.json()
        
        pipeline = next((p for p in pipelines if p.get("name") == PIPELINE_NAME or p.get("id") == PIPELINE_NAME), None)
        
        if not pipeline:
            print_status(f"Pipeline '{PIPELINE_NAME}' not found", "ERROR")
            print("\nAvailable pipelines:")
            for p in pipelines:
                print(f"  - {p.get('name')} (ID: {p.get('id')})")
            return 1
        
        pipeline_id = pipeline.get("id")
        current_status = pipeline.get("status")
        
        print_status(f"Found pipeline: {pipeline.get('name')} (ID: {pipeline_id})", "SUCCESS")
        print_status(f"Current status: {current_status}", "INFO")
        
    except Exception as e:
        print_status(f"Failed to get pipeline: {e}", "ERROR")
        return 1
    
    # Stop pipeline if running
    if current_status in ['RUNNING', 'STARTING', 'ACTIVE']:
        print_status("\nPipeline is already running. Stopping first...", "INFO")
        try:
            response = requests.post(f"{API_BASE_URL}/api/v1/pipelines/{pipeline_id}/stop", timeout=30)
            if response.status_code == 200:
                print_status("Pipeline stopped successfully", "SUCCESS")
                print_status("Waiting 5 seconds before restart...", "INFO")
                time.sleep(5)
            else:
                print_status(f"Stop returned status {response.status_code}", "WARNING")
        except Exception as e:
            print_status(f"Error stopping pipeline: {e}", "WARNING")
    
    # Start pipeline
    print_status("\nStarting pipeline...", "INFO")
    try:
        response = requests.post(f"{API_BASE_URL}/api/v1/pipelines/{pipeline_id}/start", timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print_status("Pipeline start requested successfully", "SUCCESS")
            
            if result.get("message"):
                print(f"  Message: {result['message']}")
            
            # Check for full load info
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
            status_response = requests.get(f"{API_BASE_URL}/api/v1/pipelines/{pipeline_id}/status", timeout=10)
            if status_response.status_code == 200:
                status_data = status_response.json()
                
                print("\n" + "-"*70)
                print("PIPELINE STATUS")
                print("-"*70)
                print(f"  Status: {status_data.get('status')}")
                print(f"  CDC Status: {status_data.get('cdc_status')}")
                print(f"  Full Load Status: {status_data.get('full_load_status')}")
                
                # Debezium connector
                debezium = status_data.get('debezium_connector', {})
                if debezium:
                    print(f"\n  Debezium Connector:")
                    print(f"    State: {debezium.get('state', 'N/A')}")
                    tasks = debezium.get('tasks', [])
                    for task in tasks:
                        print(f"    Task {task.get('id', 'N/A')}: {task.get('state', 'N/A')}")
                
                # Sink connector
                sink = status_data.get('sink_connector', {})
                if sink:
                    print(f"\n  Sink Connector:")
                    print(f"    State: {sink.get('state', 'N/A')}")
                    tasks = sink.get('tasks', [])
                    for task in tasks:
                        print(f"    Task {task.get('id', 'N/A')}: {task.get('state', 'N/A')}")
                
                # Summary
                print("\n" + "="*70)
                if status_data.get('status') in ['RUNNING', 'STARTING']:
                    print_status("Pipeline is starting/running!", "SUCCESS")
                else:
                    print_status(f"Pipeline status: {status_data.get('status')}", "WARNING")
                
                if status_data.get('cdc_status') in ['RUNNING', 'STARTING']:
                    print_status("CDC is starting/running!", "SUCCESS")
                else:
                    print_status(f"CDC status: {status_data.get('cdc_status')}", "WARNING")
                
        else:
            print_status(f"Failed to start pipeline: {response.status_code}", "ERROR")
            print(f"  Response: {response.text}")
            return 1
            
    except requests.exceptions.Timeout:
        print_status("Request timed out. Pipeline may still be starting...", "WARNING")
        print("  Check status manually: curl http://localhost:8000/api/v1/pipelines/{pipeline_id}/status")
    except Exception as e:
        print_status(f"Error starting pipeline: {e}", "ERROR")
        return 1
    
    print("\n" + "="*70)
    print("Next steps:")
    print("1. Monitor pipeline status in frontend: http://localhost:3000/pipelines")
    print("2. Check CDC status: python check_as400_pipeline_cdc.py")
    print("3. Check S3 data flow: python check_s3_sink_data.py")
    print("="*70 + "\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())


