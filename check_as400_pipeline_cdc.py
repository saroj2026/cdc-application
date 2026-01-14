#!/usr/bin/env python3
"""Check CDC status for AS400-S3_P pipeline"""
import requests
import sys
import json
from datetime import datetime

API_BASE_URL = "http://localhost:8000"
KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
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
    """Check AS400 pipeline CDC status."""
    print("\n" + "="*70)
    print("🔍 CHECKING CDC STATUS FOR AS400-S3_P PIPELINE")
    print("="*70 + "\n")
    
    # Check backend connectivity
    print_status("Connecting to backend API...", "INFO")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/health", timeout=5)
        if response.status_code == 200:
            print_status("Backend is accessible", "SUCCESS")
        else:
            print_status(f"Backend returned status {response.status_code}", "WARNING")
    except requests.exceptions.ConnectionError:
        print_status("Cannot connect to backend. Is it running on http://localhost:8000?", "ERROR")
        return 1
    except Exception as e:
        print_status(f"Error connecting to backend: {e}", "ERROR")
        return 1
    
    # Find pipeline
    print_status(f"\nLooking for pipeline: {PIPELINE_NAME}", "INFO")
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
        print_status(f"Found pipeline: {pipeline.get('name')} (ID: {pipeline_id})", "SUCCESS")
        
    except Exception as e:
        print_status(f"Failed to get pipeline: {e}", "ERROR")
        return 1
    
    # Get pipeline status
    print_status("\nFetching pipeline status...", "INFO")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/pipelines/{pipeline_id}/status", timeout=10)
        response.raise_for_status()
        status = response.json()
        
        print("\n" + "-"*70)
        print("PIPELINE STATUS")
        print("-"*70)
        print(f"  Status: {status.get('status', 'N/A')}")
        print(f"  CDC Status: {status.get('cdc_status', 'N/A')}")
        print(f"  Full Load Status: {status.get('full_load_status', 'N/A')}")
        
        # Debezium connector status
        debezium = status.get('debezium_connector', {})
        if debezium:
            print(f"\n  Debezium Connector:")
            print(f"    Name: {debezium.get('name', 'N/A')}")
            print(f"    State: {debezium.get('state', 'N/A')}")
            print(f"    Worker ID: {debezium.get('worker_id', 'N/A')}")
            
            # Tasks
            tasks = debezium.get('tasks', [])
            if tasks:
                print(f"    Tasks: {len(tasks)}")
                for i, task in enumerate(tasks, 1):
                    print(f"      Task {i}: {task.get('state', 'N/A')} (ID: {task.get('id', 'N/A')})")
        else:
            print(f"\n  Debezium Connector: Not found")
        
        # Sink connector status
        sink = status.get('sink_connector', {})
        if sink:
            print(f"\n  Sink Connector:")
            print(f"    Name: {sink.get('name', 'N/A')}")
            print(f"    State: {sink.get('state', 'N/A')}")
            print(f"    Worker ID: {sink.get('worker_id', 'N/A')}")
            
            # Tasks
            tasks = sink.get('tasks', [])
            if tasks:
                print(f"    Tasks: {len(tasks)}")
                for i, task in enumerate(tasks, 1):
                    print(f"      Task {i}: {task.get('state', 'N/A')} (ID: {task.get('id', 'N/A')})")
                    if task.get('trace'):
                        print(f"        Error: {task.get('trace', '')[:200]}")
        else:
            print(f"\n  Sink Connector: Not found")
        
    except Exception as e:
        print_status(f"Failed to get status: {e}", "ERROR")
        return 1
    
    # Get pipeline details
    print_status("\nFetching pipeline details...", "INFO")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/pipelines/{pipeline_id}", timeout=10)
        response.raise_for_status()
        details = response.json()
        
        print("\n" + "-"*70)
        print("PIPELINE DETAILS")
        print("-"*70)
        print(f"  Source Connection: {details.get('source_connection', {}).get('name', 'N/A')}")
        print(f"  Target Connection: {details.get('target_connection', {}).get('name', 'N/A')}")
        print(f"  Mode: {details.get('mode', 'N/A')}")
        print(f"  Source Tables: {', '.join(details.get('source_tables', []))}")
        print(f"  Target Tables: {', '.join(details.get('target_tables', []))}")
        
    except Exception as e:
        print_status(f"Failed to get details: {e}", "WARNING")
    
    # Check Kafka Connect connectors directly
    print_status("\nChecking Kafka Connect connectors directly...", "INFO")
    try:
        response = requests.get(f"{KAFKA_CONNECT_URL}/connectors", timeout=10)
        response.raise_for_status()
        connectors = response.json()
        
        # Find AS400-related connectors
        as400_connectors = [c for c in connectors if 'as400' in c.lower() or PIPELINE_NAME.lower() in c.lower()]
        
        if as400_connectors:
            print(f"\n  Found {len(as400_connectors)} AS400-related connector(s):")
            for conn_name in as400_connectors:
                print(f"    - {conn_name}")
                
                # Get connector status
                try:
                    conn_response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{conn_name}/status", timeout=10)
                    if conn_response.status_code == 200:
                        conn_status = conn_response.json()
                        print(f"      State: {conn_status.get('connector', {}).get('state', 'N/A')}")
                        tasks = conn_status.get('tasks', [])
                        for task in tasks:
                            print(f"      Task {task.get('id', 'N/A')}: {task.get('state', 'N/A')}")
                            if task.get('trace'):
                                print(f"        Error: {task.get('trace', '')[:200]}")
                except Exception as e:
                    print(f"      Error getting status: {e}")
        else:
            print(f"\n  No AS400-related connectors found")
            print(f"  All connectors: {', '.join(connectors[:10])}")
            
    except requests.exceptions.ConnectionError:
        print_status("Cannot connect to Kafka Connect", "WARNING")
        print(f"  URL: {KAFKA_CONNECT_URL}")
    except Exception as e:
        print_status(f"Error checking connectors: {e}", "WARNING")
    
    # Get replication events/metrics
    print_status("\nChecking replication events...", "INFO")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/monitoring/replication-events", 
                              params={"pipeline_id": pipeline_id, "limit": 10}, timeout=10)
        if response.status_code == 200:
            events = response.json()
            if isinstance(events, list):
                print(f"\n  Found {len(events)} recent event(s)")
                if events:
                    print(f"  Latest event:")
                    latest = events[0]
                    print(f"    Type: {latest.get('event_type', 'N/A')}")
                    print(f"    Table: {latest.get('table_name', 'N/A')}")
                    print(f"    Status: {latest.get('status', 'N/A')}")
                    print(f"    Timestamp: {latest.get('created_at', latest.get('timestamp', 'N/A'))}")
            else:
                print(f"  Response: {events}")
        else:
            print(f"  Status: {response.status_code}")
    except Exception as e:
        print_status(f"Error getting events: {e}", "WARNING")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    if status.get('status') == 'RUNNING':
        print_status("Pipeline is RUNNING", "SUCCESS")
    elif status.get('status') == 'STARTING':
        print_status("Pipeline is STARTING", "INFO")
    else:
        print_status(f"Pipeline status: {status.get('status')}", "WARNING")
    
    if status.get('cdc_status') == 'RUNNING':
        print_status("CDC is RUNNING", "SUCCESS")
    elif status.get('cdc_status') == 'STARTING':
        print_status("CDC is STARTING", "INFO")
    else:
        print_status(f"CDC status: {status.get('cdc_status')}", "WARNING")
    
    # Check connectors
    if debezium and debezium.get('state') == 'RUNNING':
        print_status("Debezium connector is RUNNING", "SUCCESS")
    elif debezium:
        print_status(f"Debezium connector: {debezium.get('state')}", "WARNING")
    else:
        print_status("Debezium connector: NOT FOUND", "ERROR")
    
    if sink and sink.get('state') == 'RUNNING':
        print_status("Sink connector is RUNNING", "SUCCESS")
    elif sink:
        print_status(f"Sink connector: {sink.get('state')}", "WARNING")
    else:
        print_status("Sink connector: NOT FOUND", "ERROR")
    
    print("\n" + "="*70)
    print("Next steps:")
    print("1. If CDC is not running, check connector logs")
    print("2. Verify AS400 connector plugin is installed")
    print("3. Check pipeline configuration")
    print("4. Monitor replication events for data flow")
    print("="*70 + "\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())


