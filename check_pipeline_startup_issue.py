"""Script to diagnose why pipeline is stuck in STARTING status."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ingestion.database.session import SessionLocal
from ingestion.database.models_db import PipelineModel
import requests
import json

def check_pipeline_startup(pipeline_name: str):
    """Check pipeline startup status and diagnose issues.
    
    Args:
        pipeline_name: Name of the pipeline to check
    """
    db = SessionLocal()
    try:
        # Find pipeline by name
        pipeline = db.query(PipelineModel).filter(
            PipelineModel.name == pipeline_name,
            PipelineModel.deleted_at.is_(None)
        ).first()
        
        if not pipeline:
            print(f"❌ Pipeline '{pipeline_name}' not found")
            return False
        
        print(f"📋 Pipeline: {pipeline.name}")
        print(f"   ID: {pipeline.id}")
        print(f"   Status: {pipeline.status}")
        print(f"   Mode: {pipeline.mode}")
        print(f"   Full Load Status: {pipeline.full_load_status}")
        print(f"   CDC Status: {pipeline.cdc_status}")
        print(f"   Debezium Connector: {pipeline.debezium_connector_name or 'Not set'}")
        print(f"   Sink Connector: {pipeline.sink_connector_name or 'Not set'}")
        
        # Check if connectors exist via Kafka Connect API
        print(f"\n🔍 Checking Kafka Connect connectors...")
        try:
            kafka_connect_url = "http://72.61.233.209:8083"
            
            # Check if Kafka Connect is reachable
            try:
                response = requests.get(f"{kafka_connect_url}/connectors", timeout=5)
                if response.status_code == 200:
                    connectors = response.json()
                    print(f"   ✓ Kafka Connect is reachable")
                    print(f"   Active connectors: {len(connectors)}")
                    
                    # Check for Debezium connector
                    if pipeline.debezium_connector_name:
                        if pipeline.debezium_connector_name in connectors:
                            print(f"   ✓ Debezium connector '{pipeline.debezium_connector_name}' exists")
                            # Get connector status
                            try:
                                status_resp = requests.get(
                                    f"{kafka_connect_url}/connectors/{pipeline.debezium_connector_name}/status",
                                    timeout=5
                                )
                                if status_resp.status_code == 200:
                                    status = status_resp.json()
                                    connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
                                    print(f"      State: {connector_state}")
                                    if connector_state != 'RUNNING':
                                        tasks = status.get('tasks', [])
                                        for task in tasks:
                                            task_state = task.get('state', 'UNKNOWN')
                                            task_id = task.get('id', 'N/A')
                                            if task_state != 'RUNNING':
                                                print(f"      Task {task_id}: {task_state}")
                                                if 'trace' in task:
                                                    print(f"      Error: {task.get('trace', '')[:200]}")
                            except Exception as e:
                                print(f"   ⚠️  Could not get Debezium connector status: {e}")
                        else:
                            print(f"   ⚠️  Debezium connector '{pipeline.debezium_connector_name}' not found in Kafka Connect")
                    else:
                        print(f"   ⚠️  Debezium connector name not set in pipeline")
                    
                    # Check for Sink connector
                    if pipeline.sink_connector_name:
                        if pipeline.sink_connector_name in connectors:
                            print(f"   ✓ Sink connector '{pipeline.sink_connector_name}' exists")
                            # Get connector status
                            try:
                                status_resp = requests.get(
                                    f"{kafka_connect_url}/connectors/{pipeline.sink_connector_name}/status",
                                    timeout=5
                                )
                                if status_resp.status_code == 200:
                                    status = status_resp.json()
                                    connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
                                    print(f"      State: {connector_state}")
                                    if connector_state != 'RUNNING':
                                        tasks = status.get('tasks', [])
                                        for task in tasks:
                                            task_state = task.get('state', 'UNKNOWN')
                                            task_id = task.get('id', 'N/A')
                                            if task_state != 'RUNNING':
                                                print(f"      Task {task_id}: {task_state}")
                                                if 'trace' in task:
                                                    print(f"      Error: {task.get('trace', '')[:200]}")
                            except Exception as e:
                                print(f"   ⚠️  Could not get Sink connector status: {e}")
                        else:
                            print(f"   ⚠️  Sink connector '{pipeline.sink_connector_name}' not found in Kafka Connect")
                    else:
                        print(f"   ⚠️  Sink connector name not set in pipeline")
                else:
                    print(f"   ⚠️  Kafka Connect returned status {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Cannot reach Kafka Connect at {kafka_connect_url}: {e}")
        except Exception as e:
            print(f"   ⚠️  Error checking Kafka Connect: {e}")
        
        # Check backend API status
        print(f"\n🔍 Checking backend API...")
        try:
            api_url = "http://localhost:8000"
            response = requests.get(f"{api_url}/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                print(f"   ✓ Backend API is reachable")
                print(f"   Database: {health.get('database', {}).get('status', 'unknown')}")
                print(f"   Kafka Connect: {health.get('kafka_connect', {}).get('status', 'unknown')}")
            else:
                print(f"   ⚠️  Backend API returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Cannot reach backend API: {e}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if pipeline.status == "STARTING":
            if not pipeline.debezium_connector_name and not pipeline.sink_connector_name:
                print(f"   1. Pipeline is in STARTING but connectors are not created yet")
                print(f"      - This might be normal if the pipeline was just started")
                print(f"      - Wait a few moments and check again")
                print(f"      - Or try restarting the pipeline via API/UI")
            elif pipeline.debezium_connector_name or pipeline.sink_connector_name:
                print(f"   1. Connectors exist but pipeline status is still STARTING")
                print(f"      - Check connector status in Kafka Connect")
                print(f"      - There might be an error preventing connectors from starting")
                print(f"      - Check backend logs for errors")
        
        print(f"   2. To restart the pipeline:")
        print(f"      - Stop it first (if possible)")
        print(f"      - Then start it again via API: POST /api/v1/pipelines/{pipeline.id}/start")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking pipeline: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    pipeline_name = "ps_sn_p"
    
    print(f"🔍 Diagnosing startup issue for pipeline '{pipeline_name}'...\n")
    check_pipeline_startup(pipeline_name)


