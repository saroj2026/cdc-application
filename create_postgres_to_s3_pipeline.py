"""Create pipeline from PostgreSQL (source) to S3 (target) with full load only."""

import requests
import json
import time

API_URL = "http://localhost:8000/api/v1"

def wait_for_server(max_attempts=10):
    """Wait for server to be ready."""
    for i in range(max_attempts):
        try:
            response = requests.get(f"{API_URL}/connections", timeout=2)
            if response.status_code in [200, 401, 403]:
                return True
        except:
            pass
        time.sleep(1)
    return False

def get_connections():
    """Get all connections and find PostgreSQL source and S3 target."""
    try:
        response = requests.get(f"{API_URL}/connections", timeout=5)
        if response.status_code == 200:
            connections = response.json()
            
            # Find PostgreSQL connections (source)
            postgres_connections = [
                c for c in connections 
                if c.get('database_type') == 'postgresql' and c.get('is_active', True)
            ]
            
            # Find S3 connection (target)
            s3_connections = [
                c for c in connections 
                if c.get('database_type') == 's3' and c.get('is_active', True)
            ]
            
            return postgres_connections, s3_connections
    except Exception as e:
        print(f"Error fetching connections: {e}")
    return [], []

def discover_tables(connection_id, database=None, schema=None):
    """Discover tables in PostgreSQL connection."""
    try:
        params = {}
        if database:
            params['database'] = database
        if schema:
            params['schema'] = schema
            
        response = requests.get(
            f"{API_URL}/connections/{connection_id}/tables",
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('tables', [])
    except Exception as e:
        print(f"Error discovering tables: {e}")
    return []

def create_pipeline(source_conn, target_conn, tables):
    """Create pipeline from PostgreSQL to S3."""
    print("\n3. Creating pipeline...")
    print(f"   Source: {source_conn.get('name')} (PostgreSQL)")
    print(f"   Target: {target_conn.get('name')} (S3)")
    print(f"   Tables: {', '.join(tables) if tables else 'All tables'}")
    print(f"   Mode: Full Load Only\n")
    
    # Get source database and schema
    source_database = source_conn.get('database', 'postgres')
    source_schema = source_conn.get('schema') or 'public'
    
    # For S3 target, we'll use the bucket name as database and prefix as schema
    target_database = target_conn.get('database')  # Bucket name
    target_schema = target_conn.get('schema') or ''  # S3 prefix
    
    pipeline_data = {
        "name": f"PostgreSQL_to_S3_{source_conn.get('database', 'db')}",
        "source_connection_id": source_conn.get('id'),
        "target_connection_id": target_conn.get('id'),
        "source_database": source_database,
        "source_schema": source_schema,
        "source_tables": tables if tables else [],  # Empty list means all tables
        "target_database": target_database,
        "target_schema": target_schema,
        "target_tables": None,
        "mode": "full_load_only",  # Full load only, no CDC
        "enable_full_load": True,
        "auto_create_target": True,
        "target_table_mapping": None  # Will be auto-generated
    }
    
    try:
        # Pipeline endpoint is /api/pipelines (not /api/v1/pipelines)
        pipeline_url = f"http://localhost:8000/api/pipelines"
        response = requests.post(
            pipeline_url,
            json=pipeline_data,
            timeout=30
        )
        
        if response.status_code == 201:
            pipeline = response.json()
            print("✅ Pipeline created successfully!")
            print(f"   Pipeline ID: {pipeline.get('id')}")
            print(f"   Name: {pipeline.get('name')}")
            print(f"   Mode: {pipeline.get('mode')}")
            print(f"   Status: {pipeline.get('status')}")
            return pipeline
        else:
            print(f"❌ Failed to create pipeline: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("=" * 60)
    print("Create PostgreSQL to S3 Pipeline (Full Load Only)")
    print("=" * 60)
    
    # Wait for server
    print("\nWaiting for API server...")
    if not wait_for_server():
        print("❌ API server is not responding")
        return
    print("✅ API server is ready\n")
    
    # Get connections
    print("1. Fetching connections...")
    postgres_conns, s3_conns = get_connections()
    
    if not postgres_conns:
        print("❌ No PostgreSQL connections found")
        print("   Please create a PostgreSQL connection first")
        return
    
    if not s3_conns:
        print("❌ No S3 connections found")
        print("   Please create an S3 connection first")
        return
    
    # Select first PostgreSQL connection as source
    source_conn = postgres_conns[0]
    print(f"   ✅ Source: {source_conn.get('name')} (ID: {source_conn.get('id')})")
    print(f"      Database: {source_conn.get('database')}")
    print(f"      Schema: {source_conn.get('schema') or 'public'}")
    
    # Select S3 connection as target
    target_conn = s3_conns[0]
    print(f"   ✅ Target: {target_conn.get('name')} (ID: {target_conn.get('id')})")
    print(f"      Bucket: {target_conn.get('database')}")
    print(f"      Region: {target_conn.get('additional_config', {}).get('region_name', 'N/A')}")
    
    # Discover tables
    print("\n2. Discovering tables in source database...")
    source_db = source_conn.get('database')
    source_schema = source_conn.get('schema') or 'public'
    
    tables_data = discover_tables(source_conn.get('id'), database=source_db, schema=source_schema)
    
    # Extract table names from response (could be list of strings or list of dicts)
    if tables_data:
        if isinstance(tables_data[0], dict):
            tables = [t.get('name') or t.get('table_name') for t in tables_data if t.get('name') or t.get('table_name')]
        else:
            tables = [str(t) for t in tables_data]
    else:
        tables = []
    
    if tables:
        print(f"   ✅ Found {len(tables)} tables")
        print(f"   Tables: {', '.join(tables[:10])}{'...' if len(tables) > 10 else ''}")
        
        # Use first 5 tables or all if less than 5
        selected_tables = tables[:5] if len(tables) > 5 else tables
        print(f"\n   Using first {len(selected_tables)} tables for pipeline")
    else:
        print("   ⚠️  No tables found or could not discover tables")
        print("   Creating pipeline without specific tables (will use all tables)")
        selected_tables = []
    
    # Create pipeline
    pipeline = create_pipeline(source_conn, target_conn, selected_tables)
    
    if pipeline:
        print("\n" + "=" * 60)
        print("✅ Pipeline Created Successfully!")
        print("=" * 60)
        print(f"\nPipeline Details:")
        print(f"  ID: {pipeline.get('id')}")
        print(f"  Name: {pipeline.get('name')}")
        print(f"  Source: {source_conn.get('name')}")
        print(f"  Target: {target_conn.get('name')}")
        print(f"  Mode: {pipeline.get('mode')}")
        print(f"  Status: {pipeline.get('status')}")
        print(f"  Tables: {len(selected_tables) if selected_tables else 'All'}")
        
        print(f"\nTo start the pipeline:")
        print(f"  POST {API_URL}/pipelines/{pipeline.get('id')}/start")
        print(f"\nTo view pipeline:")
        print(f"  GET {API_URL}/pipelines/{pipeline.get('id')}")

if __name__ == "__main__":
    main()

