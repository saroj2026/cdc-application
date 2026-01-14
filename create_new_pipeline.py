"""
Create a new pipeline:
- Source: PostgreSQL, cdctest database, public schema, projects_simple table
- Target: SQL Server, cdctest database, dbo schema, projects_simple table
- Mode: FULL_LOAD_AND_CDC
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8000"

def get_connections() -> list:
    """Get all connections."""
    response = requests.get(f"{BASE_URL}/api/connections")
    if response.status_code != 200:
        print(f"Error getting connections: {response.status_code}")
        return []
    return response.json()

def find_connection(name: str, database_type: str) -> Optional[Dict[str, Any]]:
    """Find a connection by name and database type."""
    connections = get_connections()
    for conn in connections:
        if conn.get("name") == name and conn.get("database_type") == database_type:
            return conn
    return None

def create_connection(name: str, database_type: str, host: str, port: int, 
                     database: str, username: str, password: str, schema: Optional[str] = None) -> Dict[str, Any]:
    """Create a new connection."""
    data = {
        "name": name,
        "database_type": database_type,
        "host": host,
        "port": port,
        "database": database,
        "username": username,
        "password": password,
        "schema": schema
    }
    
    response = requests.post(f"{BASE_URL}/api/connections", json=data)
    if response.status_code == 201:
        return response.json()
    else:
        print(f"Error creating connection: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def create_pipeline(name: str, source_connection_id: str, target_connection_id: str,
                   source_database: str, source_schema: str, source_tables: list,
                   target_database: Optional[str] = None, target_schema: Optional[str] = None,
                   mode: str = "full_load_and_cdc", auto_create_target: bool = True) -> Dict[str, Any]:
    """Create a new pipeline."""
    data = {
        "name": name,
        "source_connection_id": source_connection_id,
        "target_connection_id": target_connection_id,
        "source_database": source_database,
        "source_schema": source_schema,
        "source_tables": source_tables,
        "target_database": target_database,
        "target_schema": target_schema,
        "mode": mode,
        "auto_create_target": auto_create_target
    }
    
    response = requests.post(f"{BASE_URL}/api/pipelines", json=data)
    if response.status_code == 201:
        return response.json()
    else:
        print(f"Error creating pipeline: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def start_pipeline(pipeline_id: str) -> Dict[str, Any]:
    """Start a pipeline."""
    response = requests.post(f"{BASE_URL}/api/pipelines/{pipeline_id}/start")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error starting pipeline: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def main():
    print("="*80)
    print("Create New Pipeline: PostgreSQL -> SQL Server")
    print("="*80)
    print("\nConfiguration:")
    print("  Source: PostgreSQL, cdctest, public, projects_simple")
    print("  Target: SQL Server, cdctest, dbo, projects_simple")
    print("  Mode: FULL_LOAD_AND_CDC")
    print("="*80)
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("✗ Backend is not responding correctly")
            return
        print("✓ Backend is running\n")
    except Exception as e:
        print(f"✗ Backend is not running: {e}")
        print("Please start the backend first:")
        print("  python -m uvicorn ingestion.api:app --host 0.0.0.0 --port 8000")
        return
    
    # Find or create PostgreSQL source connection
    print("1. Checking PostgreSQL source connection...")
    pg_conn = find_connection("PostgreSQL Source - cdctest", "postgresql")
    
    if not pg_conn:
        print("   PostgreSQL connection not found. Creating...")
        # Default PostgreSQL credentials (adjust if needed)
        pg_conn = create_connection(
            name="PostgreSQL Source - cdctest",
            database_type="postgresql",
            host="localhost",
            port=5432,
            database="cdctest",
            username="postgres",
            password="postgres",
            schema="public"
        )
        if not pg_conn:
            print("✗ Failed to create PostgreSQL connection")
            return
        print(f"   ✓ Created PostgreSQL connection: {pg_conn.get('id')}")
    else:
        print(f"   ✓ Found PostgreSQL connection: {pg_conn.get('id')}")
    
    # Find or create SQL Server target connection
    print("\n2. Checking SQL Server target connection...")
    sql_conn = find_connection("SQL Server Target - cdctest", "sqlserver")
    
    if not sql_conn:
        print("   SQL Server connection not found. Creating...")
        # SQL Server credentials (from previous context)
        sql_conn = create_connection(
            name="SQL Server Target - cdctest",
            database_type="sqlserver",
            host="localhost",
            port=1433,
            database="cdctest",
            username="sa",
            password="Sql@12345",
            schema="dbo"
        )
        if not sql_conn:
            print("✗ Failed to create SQL Server connection")
            return
        print(f"   ✓ Created SQL Server connection: {sql_conn.get('id')}")
    else:
        print(f"   ✓ Found SQL Server connection: {sql_conn.get('id')}")
    
    # Create pipeline
    print("\n3. Creating pipeline...")
    pipeline_name = "pg_to_mssql_projects_simple"
    
    # Check if pipeline already exists
    pipelines_response = requests.get(f"{BASE_URL}/api/pipelines")
    if pipelines_response.status_code == 200:
        existing_pipelines = pipelines_response.json()
        for p in existing_pipelines:
            if p.get("name") == pipeline_name:
                print(f"   ⚠ Pipeline '{pipeline_name}' already exists (ID: {p.get('id')})")
                response = input("   Do you want to delete and recreate it? (y/n): ").strip().lower()
                if response == 'y':
                    # Delete existing pipeline
                    delete_response = requests.delete(f"{BASE_URL}/api/pipelines/{p.get('id')}")
                    if delete_response.status_code == 200:
                        print(f"   ✓ Deleted existing pipeline")
                    else:
                        print(f"   ⚠ Could not delete: {delete_response.status_code}")
                else:
                    print("   Using existing pipeline")
                    pipeline_id = p.get('id')
                    break
        else:
            # Create new pipeline
            pipeline = create_pipeline(
                name=pipeline_name,
                source_connection_id=pg_conn.get('id'),
                target_connection_id=sql_conn.get('id'),
                source_database="cdctest",
                source_schema="public",
                source_tables=["projects_simple"],
                target_database="cdctest",
                target_schema="dbo",
                mode="full_load_and_cdc",
                auto_create_target=True
            )
            
            if not pipeline:
                print("✗ Failed to create pipeline")
                return
            pipeline_id = pipeline.get('id')
            print(f"   ✓ Created pipeline: {pipeline_id}")
    else:
        print(f"✗ Failed to check existing pipelines: {pipelines_response.status_code}")
        return
    
    # Start pipeline
    print("\n4. Starting pipeline...")
    start_result = start_pipeline(pipeline_id)
    
    if start_result:
        print("   ✓ Pipeline start requested")
        print(f"   Status: {start_result.get('status')}")
        print(f"   Message: {start_result.get('message')}")
        
        if start_result.get('full_load'):
            fl = start_result['full_load']
            print(f"\n   Full Load Result:")
            print(f"     Success: {fl.get('success')}")
            if fl.get('success'):
                print(f"     Tables: {fl.get('tables_transferred')}")
                print(f"     Rows: {fl.get('total_rows')}")
                print(f"     LSN: {fl.get('lsn')}")
        
        print(f"\n{'='*80}")
        print("Pipeline started successfully!")
        print(f"{'='*80}")
        print(f"\nPipeline ID: {pipeline_id}")
        print(f"Pipeline Name: {pipeline_name}")
        print(f"\nMonitor the backend logs to see:")
        print("  - Step 0: Schema creation")
        print("  - Step 1: Full load progress")
        print("  - Step 2: CDC setup (if enabled)")
        print(f"\nCheck pipeline status:")
        print(f"  GET {BASE_URL}/api/pipelines/{pipeline_id}")
    else:
        print("✗ Failed to start pipeline")
        return

if __name__ == "__main__":
    main()

