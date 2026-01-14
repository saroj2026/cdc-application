#!/usr/bin/env python3
"""Restart AS400 Pipeline Script"""
import requests
import time
import sys

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
    """Restart AS400 pipeline."""
    print("\n" + "="*60)
    print("🔄 RESTARTING AS400 PIPELINE")
    print("="*60 + "\n")
    
    # Find pipeline
    print_status(f"Looking for pipeline: {PIPELINE_NAME}", "INFO")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/pipelines")
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
        pipeline_name = pipeline.get("name")
        current_status = pipeline.get("status")
        
        print_status(f"Found pipeline: {pipeline_name} (ID: {pipeline_id})", "SUCCESS")
        print_status(f"Current status: {current_status}", "INFO")
        
    except requests.exceptions.ConnectionError:
        print_status("Cannot connect to backend. Is it running on http://localhost:8000?", "ERROR")
        return 1
    except Exception as e:
        print_status(f"Failed to get pipeline: {e}", "ERROR")
        return 1
    
    # Stop pipeline if running
    if current_status in ['RUNNING', 'STARTING', 'ACTIVE']:
        print_status("\nStep 1: Stopping pipeline...", "INFO")
        try:
            response = requests.post(f"{API_BASE_URL}/api/v1/pipelines/{pipeline_id}/stop")
            if response.status_code == 200:
                result = response.json()
                print_status("Pipeline stopped successfully", "SUCCESS")
                if result.get("message"):
                    print(f"   Message: {result['message']}")
            elif response.status_code == 404:
                print_status("Pipeline not found", "WARNING")
            else:
                print_status(f"Stop returned status {response.status_code}: {response.text}", "WARNING")
        except Exception as e:
            print_status(f"Stop failed: {e}", "WARNING")
        
        # Wait for stop to complete
        print_status("Waiting 5 seconds for pipeline to stop...", "INFO")
        time.sleep(5)
    else:
        print_status(f"Pipeline is already {current_status}, skipping stop", "INFO")
    
    # Start pipeline
    print_status("\nStep 2: Starting pipeline...", "INFO")
    try:
        response = requests.post(f"{API_BASE_URL}/api/v1/pipelines/{pipeline_id}/start")
        if response.status_code == 200:
            result = response.json()
            print_status("Pipeline start requested successfully", "SUCCESS")
            if result.get("message"):
                print(f"   Message: {result['message']}")
            
            # Check for full load info
            if result.get("full_load"):
                fl = result['full_load']
                print(f"   Full Load: success={fl.get('success')}, tables={fl.get('tables_transferred', 0)}")
            
            # Wait a bit and check status
            print_status("Waiting 5 seconds for pipeline to start...", "INFO")
            time.sleep(5)
            
            # Get updated status
            status_response = requests.get(f"{API_BASE_URL}/api/v1/pipelines/{pipeline_id}/status")
            if status_response.status_code == 200:
                status_data = status_response.json()
                print_status("\nPipeline Status:", "INFO")
                print(f"   Status: {status_data.get('status')}")
                print(f"   CDC Status: {status_data.get('cdc_status')}")
                print(f"   Debezium Connector: {status_data.get('debezium_connector', {}).get('state', 'N/A')}")
                print(f"   Sink Connector: {status_data.get('sink_connector', {}).get('state', 'N/A')}")
                
                if status_data.get('status') in ['RUNNING', 'STARTING']:
                    print_status("Pipeline is starting/running!", "SUCCESS")
                else:
                    print_status("Pipeline status may need attention", "WARNING")
        else:
            print_status(f"Failed to start: {response.status_code}", "ERROR")
            print(f"   Response: {response.text}")
            return 1
            
    except Exception as e:
        print_status(f"Start failed: {e}", "ERROR")
        return 1
    
    print("\n" + "="*60)
    print_status("Pipeline restart complete!", "SUCCESS")
    print("="*60 + "\n")
    
    print("Next steps:")
    print("1. Check pipeline status in frontend: http://localhost:3000/pipelines")
    print("2. Monitor logs for any errors")
    print("3. Verify connectors are running:")
    print("   curl http://72.61.233.209:8083/connectors")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())


