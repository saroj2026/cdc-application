#!/usr/bin/env python3
"""Check if data is flowing to S3 sink for AS400-S3_P pipeline"""
import requests
import sys
import json
from datetime import datetime, timedelta

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
    """Check S3 sink data flow."""
    print("\n" + "="*70)
    print("🔍 CHECKING S3 SINK DATA FLOW FOR AS400-S3_P PIPELINE")
    print("="*70 + "\n")
    
    # Find pipeline
    print_status("Finding pipeline...", "INFO")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/pipelines", timeout=10)
        response.raise_for_status()
        pipelines = response.json()
        
        pipeline = next((p for p in pipelines if p.get("name") == PIPELINE_NAME or p.get("id") == PIPELINE_NAME), None)
        
        if not pipeline:
            print_status(f"Pipeline '{PIPELINE_NAME}' not found", "ERROR")
            return 1
        
        pipeline_id = pipeline.get("id")
        print_status(f"Found pipeline: {pipeline.get('name')} (ID: {pipeline_id})", "SUCCESS")
        
    except Exception as e:
        print_status(f"Failed to get pipeline: {e}", "ERROR")
        return 1
    
    # Get pipeline status
    print_status("\nChecking pipeline status...", "INFO")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/pipelines/{pipeline_id}/status", timeout=10)
        response.raise_for_status()
        status = response.json()
        
        print("\n" + "-"*70)
        print("PIPELINE STATUS")
        print("-"*70)
        print(f"  Status: {status.get('status', 'N/A')}")
        print(f"  CDC Status: {status.get('cdc_status', 'N/A')}")
        
        # Sink connector status
        sink = status.get('sink_connector', {})
        if sink:
            print(f"\n  Sink Connector:")
            print(f"    Name: {sink.get('name', 'N/A')}")
            print(f"    State: {sink.get('state', 'N/A')}")
            
            # Tasks
            tasks = sink.get('tasks', [])
            if tasks:
                print(f"    Tasks: {len(tasks)}")
                for i, task in enumerate(tasks, 1):
                    task_state = task.get('state', 'N/A')
                    print(f"      Task {i}: {task_state} (ID: {task.get('id', 'N/A')})")
                    
                    if task_state == 'FAILED':
                        if task.get('trace'):
                            print(f"        Error: {task.get('trace', '')[:300]}")
                    elif task_state == 'RUNNING':
                        print_status(f"        Task {i} is RUNNING", "SUCCESS")
        else:
            print_status("\n  Sink Connector: NOT FOUND", "ERROR")
        
    except Exception as e:
        print_status(f"Failed to get status: {e}", "ERROR")
        return 1
    
    # Check Kafka Connect sink connector directly
    print_status("\nChecking Kafka Connect sink connector...", "INFO")
    try:
        response = requests.get(f"{KAFKA_CONNECT_URL}/connectors", timeout=10)
        response.raise_for_status()
        connectors = response.json()
        
        # Find S3 sink connector
        sink_connectors = [c for c in connectors if 's3' in c.lower() or 'sink' in c.lower()]
        as400_sink = [c for c in sink_connectors if PIPELINE_NAME.lower() in c.lower() or 'as400' in c.lower()]
        
        if as400_sink:
            sink_conn_name = as400_sink[0]
            print_status(f"Found sink connector: {sink_conn_name}", "SUCCESS")
            
            # Get connector status
            try:
                conn_response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{sink_conn_name}/status", timeout=10)
                if conn_response.status_code == 200:
                    conn_status = conn_response.json()
                    print(f"\n  Connector State: {conn_status.get('connector', {}).get('state', 'N/A')}")
                    
                    tasks = conn_status.get('tasks', [])
                    print(f"  Tasks: {len(tasks)}")
                    for task in tasks:
                        task_state = task.get('state', 'N/A')
                        print(f"    Task {task.get('id', 'N/A')}: {task_state}")
                        
                        if task_state == 'FAILED':
                            if task.get('trace'):
                                print(f"      Error: {task.get('trace', '')[:300]}")
                        elif task_state == 'RUNNING':
                            print_status(f"      Task {task.get('id')} is RUNNING", "SUCCESS")
            
            except Exception as e:
                print_status(f"Error getting connector status: {e}", "WARNING")
            
            # Get connector config to find S3 bucket
            try:
                config_response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{sink_conn_name}/config", timeout=10)
                if config_response.status_code == 200:
                    config = config_response.json()
                    bucket = config.get('s3.bucket.name', 'N/A')
                    prefix = config.get('topics.dir', config.get('s3.prefix', 'N/A'))
                    flush_size = config.get('flush.size', 'N/A')
                    
                    print(f"\n  S3 Configuration:")
                    print(f"    Bucket: {bucket}")
                    print(f"    Prefix: {prefix}")
                    print(f"    Flush Size: {flush_size}")
                    print(f"\n  To check S3 bucket manually:")
                    print(f"    aws s3 ls s3://{bucket}/{prefix}/ --recursive | tail -20")
            except Exception as e:
                print_status(f"Error getting connector config: {e}", "WARNING")
        else:
            print_status("S3 sink connector not found", "ERROR")
            print(f"  All connectors: {', '.join(connectors[:10])}")
            
    except requests.exceptions.ConnectionError:
        print_status("Cannot connect to Kafka Connect", "WARNING")
        print(f"  URL: {KAFKA_CONNECT_URL}")
    except Exception as e:
        print_status(f"Error checking connectors: {e}", "WARNING")
    
    # Check replication events
    print_status("\nChecking replication events...", "INFO")
    try:
        # Get events from last hour
        response = requests.get(f"{API_BASE_URL}/api/v1/monitoring/replication-events", 
                              params={"pipeline_id": pipeline_id, "limit": 50}, timeout=10)
        if response.status_code == 200:
            events = response.json()
            if isinstance(events, list):
                # Filter for recent events (last hour)
                now = datetime.now()
                recent_events = []
                for event in events:
                    event_time = event.get('created_at') or event.get('timestamp')
                    if event_time:
                        try:
                            # Parse timestamp
                            if isinstance(event_time, str):
                                # Try different formats
                                for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f']:
                                    try:
                                        event_dt = datetime.strptime(event_time.split('.')[0], fmt)
                                        break
                                    except:
                                        continue
                                else:
                                    continue
                            else:
                                continue
                            
                            # Check if within last hour
                            if (now - event_dt).total_seconds() < 3600:
                                recent_events.append(event)
                        except:
                            pass
                
                print(f"\n  Total events: {len(events)}")
                print(f"  Recent events (last hour): {len(recent_events)}")
                
                if recent_events:
                    print_status("Data is flowing!", "SUCCESS")
                    print(f"\n  Latest events:")
                    for event in recent_events[:5]:
                        print(f"    - {event.get('event_type', 'N/A')} | {event.get('table_name', 'N/A')} | {event.get('status', 'N/A')} | {event.get('created_at', event.get('timestamp', 'N/A'))}")
                else:
                    print_status("No recent events found (last hour)", "WARNING")
                    if events:
                        print(f"  Latest event: {events[0].get('created_at', events[0].get('timestamp', 'N/A'))}")
            else:
                print(f"  Response: {events}")
        else:
            print(f"  Status: {response.status_code}")
    except Exception as e:
        print_status(f"Error getting events: {e}", "WARNING")
    
    # Check pipeline metrics
    print_status("\nChecking pipeline metrics...", "INFO")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/monitoring/pipelines/{pipeline_id}/metrics", timeout=10)
        if response.status_code == 200:
            metrics = response.json()
            if isinstance(metrics, dict):
                print(f"\n  Metrics:")
                print(f"    Events Captured: {metrics.get('events_captured', 'N/A')}")
                print(f"    Events Applied: {metrics.get('events_applied', 'N/A')}")
                print(f"    Events Failed: {metrics.get('events_failed', 'N/A')}")
                print(f"    Rows Transferred: {metrics.get('rows_transferred', 'N/A')}")
    except Exception as e:
        print_status(f"Error getting metrics: {e}", "WARNING")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    # Check sink connector
    if sink and sink.get('state') == 'RUNNING':
        print_status("Sink connector is RUNNING", "SUCCESS")
    elif sink:
        print_status(f"Sink connector: {sink.get('state')}", "WARNING")
    else:
        print_status("Sink connector: NOT FOUND", "ERROR")
    
    # Check if data is flowing
    print("\nTo verify data in S3:")
    print("1. Check S3 bucket using AWS CLI:")
    print("   aws s3 ls s3://<bucket-name>/<prefix>/ --recursive | tail -20")
    print("2. Check connector logs for flush messages")
    print("3. Monitor replication events for new data")
    print("4. Check S3 bucket size/object count")
    
    print("\n" + "="*70)
    print("Next steps:")
    print("1. If sink connector is RUNNING, data should be flowing")
    print("2. Check S3 bucket for new files")
    print("3. Monitor replication events for confirmation")
    print("4. Check connector logs if no data appears")
    print("="*70 + "\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())


