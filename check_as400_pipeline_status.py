#!/usr/bin/env python3
"""Check status and logs for AS400-S3_P pipeline."""

import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000/api/v1"
KAFKA_CONNECT = "http://72.61.233.209:8083"

def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_status(message, status="INFO"):
    symbols = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARNING": "⚠️"
    }
    print(f"{symbols.get(status, 'ℹ️')} {message}")

def check_pipeline_status():
    """Check pipeline status from backend API."""
    print_section("PIPELINE STATUS")
    
    try:
        # Get all pipelines
        response = requests.get(f"{API_BASE}/pipelines")
        if response.status_code != 200:
            print_status(f"Failed to get pipelines: {response.status_code}", "ERROR")
            return None
        
        pipelines = response.json()
        as400_pipeline = None
        
        for pipeline in pipelines:
            if pipeline.get('name') == 'AS400-S3_P' or 'AS400' in pipeline.get('name', '').upper():
                as400_pipeline = pipeline
                break
        
        if not as400_pipeline:
            print_status("AS400-S3_P pipeline not found", "WARNING")
            return None
        
        pipeline_id = as400_pipeline.get('id')
        print_status(f"Found pipeline: {as400_pipeline.get('name')} (ID: {pipeline_id})", "SUCCESS")
        
        # Get detailed status
        status_response = requests.get(f"{API_BASE}/pipelines/{pipeline_id}/status")
        if status_response.status_code == 200:
            status = status_response.json()
            print("\n📊 Pipeline Status Details:")
            print(f"   Status: {status.get('status', 'N/A')}")
            print(f"   Full Load Status: {status.get('full_load_status', 'N/A')}")
            print(f"   CDC Status: {status.get('cdc_status', 'N/A')}")
            print(f"   Last Updated: {status.get('updated_at', 'N/A')}")
            
            if status.get('full_load_error'):
                print(f"   Full Load Error: {status.get('full_load_error')}")
            if status.get('cdc_error'):
                print(f"   CDC Error: {status.get('cdc_error')}")
        
        return pipeline_id
        
    except Exception as e:
        print_status(f"Error checking pipeline status: {e}", "ERROR")
        return None

def check_kafka_connect_connectors(pipeline_id):
    """Check Kafka Connect connector status."""
    print_section("KAFKA CONNECT CONNECTORS")
    
    try:
        # Get all connectors
        response = requests.get(f"{KAFKA_CONNECT}/connectors")
        if response.status_code != 200:
            print_status(f"Failed to connect to Kafka Connect: {response.status_code}", "ERROR")
            return
        
        connectors = response.json()
        print_status(f"Found {len(connectors)} connector(s)", "INFO")
        
        # Check for AS400-related connectors
        as400_connectors = [c for c in connectors if 'as400' in c.lower() or 'ibmi' in c.lower() or pipeline_id in c]
        
        if not as400_connectors:
            print_status("No AS400 connectors found", "WARNING")
        else:
            for conn_name in as400_connectors:
                print(f"\n📡 Connector: {conn_name}")
                
                # Get connector status
                status_resp = requests.get(f"{KAFKA_CONNECT}/connectors/{conn_name}/status")
                if status_resp.status_code == 200:
                    status = status_resp.json()
                    print(f"   State: {status.get('connector', {}).get('state', 'N/A')}")
                    print(f"   Worker ID: {status.get('connector', {}).get('worker_id', 'N/A')}")
                    
                    # Check tasks
                    tasks = status.get('tasks', [])
                    print(f"   Tasks: {len(tasks)}")
                    for i, task in enumerate(tasks):
                        task_state = task.get('state', 'N/A')
                        task_id = task.get('id', i)
                        print(f"      Task {task_id}: {task_state}")
                        if task.get('trace'):
                            print(f"         Error: {task.get('trace')[:200]}")
                
                # Get connector config
                config_resp = requests.get(f"{KAFKA_CONNECT}/connectors/{conn_name}/config")
                if config_resp.status_code == 200:
                    config = config_resp.json()
                    print(f"   Connector Class: {config.get('connector.class', 'N/A')}")
                    print(f"   Database: {config.get('database.dbname', 'N/A')}")
                    print(f"   Tables: {config.get('table.include.list', 'N/A')}")
        
        # Check for S3 sink connector
        s3_connectors = [c for c in connectors if 's3' in c.lower() or 'sink' in c.lower()]
        if s3_connectors:
            print(f"\n📦 S3 Sink Connectors:")
            for conn_name in s3_connectors:
                status_resp = requests.get(f"{KAFKA_CONNECT}/connectors/{conn_name}/status")
                if status_resp.status_code == 200:
                    status = status_resp.json()
                    print(f"   {conn_name}: {status.get('connector', {}).get('state', 'N/A')}")
        
    except Exception as e:
        print_status(f"Error checking Kafka Connect: {e}", "ERROR")

def check_replication_events(pipeline_id):
    """Check recent replication events."""
    print_section("RECENT REPLICATION EVENTS")
    
    try:
        response = requests.get(f"{API_BASE}/monitoring/replication-events?pipeline_id={pipeline_id}&limit=10")
        if response.status_code == 200:
            events = response.json()
            if events:
                print_status(f"Found {len(events)} recent events", "INFO")
                for event in events[:5]:  # Show last 5
                    event_type = event.get('event_type', 'N/A')
                    status = event.get('status', 'N/A')
                    timestamp = event.get('created_at', event.get('timestamp', 'N/A'))
                    print(f"   [{timestamp}] {event_type}: {status}")
            else:
                print_status("No replication events found", "WARNING")
        else:
            print_status(f"Failed to get events: {response.status_code}", "WARNING")
    except Exception as e:
        print_status(f"Error checking events: {e}", "ERROR")

def check_pipeline_metrics(pipeline_id):
    """Check pipeline metrics."""
    print_section("PIPELINE METRICS")
    
    try:
        response = requests.get(f"{API_BASE}/monitoring/pipelines/{pipeline_id}/metrics?limit=5")
        if response.status_code == 200:
            data = response.json()
            metrics = data if isinstance(data, list) else data.get('metrics', [])
            if metrics:
                print_status(f"Found {len(metrics)} metric(s)", "INFO")
                latest = metrics[0] if metrics else {}
                print(f"   Throughput: {latest.get('throughput_events_per_sec', 0)} events/sec")
                print(f"   Lag: {latest.get('lag_bytes', 0)} bytes")
                print(f"   Error Count: {latest.get('error_count', 0)}")
            else:
                print_status("No metrics available", "WARNING")
        else:
            print_status(f"Failed to get metrics: {response.status_code}", "WARNING")
    except Exception as e:
        print_status(f"Error checking metrics: {e}", "ERROR")

def main():
    print("\n" + "=" * 80)
    print("  AS400-S3_P PIPELINE STATUS CHECK")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Check pipeline status
    pipeline_id = check_pipeline_status()
    
    if pipeline_id:
        # Check Kafka Connect connectors
        check_kafka_connect_connectors(pipeline_id)
        
        # Check replication events
        check_replication_events(pipeline_id)
        
        # Check metrics
        check_pipeline_metrics(pipeline_id)
    else:
        print_status("Cannot proceed without pipeline ID", "ERROR")
    
    print("\n" + "=" * 80)
    print("  STATUS CHECK COMPLETE")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()

