"""Start CDC pipeline with Docker PostgreSQL as source and SQL Server as target."""

import logging
import sys
import uuid
from ingestion.cdc_manager import CDCManager
from ingestion.models import Connection, Pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

print("=" * 60)
print("Starting CDC Pipeline - VM PostgreSQL to SQL Server")
print("=" * 60)

# VM PostgreSQL connection details
# Both Python (host) and Debezium (Docker) will connect to VM server
VM_PG_HOST = "72.61.241.193"  # VM server IP
VM_PG_PORT = 5432
VM_PG_DATABASE = "openmetadata_db"  # Database name
VM_PG_USER = "cdc_user"  # CDC user with REPLICATION privilege
VM_PG_PASSWORD = "cdc_password"

# SQL Server connection (target - remote)
SQL_SERVER_HOST = "72.61.233.209"
SQL_SERVER_PORT = 1433
SQL_SERVER_DATABASE = "cdctest"
SQL_SERVER_USER = "SA"
SQL_SERVER_PASSWORD = "Sql@12345"

print(f"\n1. Creating pipeline...")
print(f"   Source: VM PostgreSQL ({VM_PG_HOST}:{VM_PG_PORT}/{VM_PG_DATABASE})")
print(f"   Target: SQL Server ({SQL_SERVER_HOST}:{SQL_SERVER_PORT}/{SQL_SERVER_DATABASE})")
print(f"   User: {VM_PG_USER}")
print(f"   Table: cdc_test")

try:
    # Initialize CDC Manager
    cdc_manager = CDCManager(kafka_connect_url="http://localhost:8083")
    
    # Create source connection (VM PostgreSQL)
    # Both Python (host) and Debezium (Docker) will connect to VM server IP
    source_connection = Connection(
        id=str(uuid.uuid4()),
        name="VM PostgreSQL SOURCE",
        connection_type="source",
        database_type="postgresql",
        host=VM_PG_HOST,  # VM server IP/hostname
        port=VM_PG_PORT,
        database=VM_PG_DATABASE,
        username=VM_PG_USER,
        password=VM_PG_PASSWORD,
        schema="public",
        additional_config={
            "publication_name": "cdc_publication",  # Use existing publication
            "publication_autocreate": "disabled"  # Use existing publication as-is
        }
    )
    
    # Create target connection (SQL Server)
    target_connection = Connection(
        id=str(uuid.uuid4()),
        name="SQL Server TARGET",
        connection_type="target",
        database_type="sqlserver",
        host=SQL_SERVER_HOST,
        port=SQL_SERVER_PORT,
        database=SQL_SERVER_DATABASE,
        username=SQL_SERVER_USER,
        password=SQL_SERVER_PASSWORD,
        schema="dbo",
        additional_config={
            "encrypt": False,
            "trust_server_certificate": True
        }
    )
    
    # Table name
    print(f"\n2. Table Configuration...")
    table_name = "cdc_test"  # Table to replicate
    print(f"   Table: {table_name}")
    
    # Create pipeline
    pipeline = Pipeline(
        id=str(uuid.uuid4()),
        name="P_DOCKER_POSTGRES_TO_SQLSERVER",
        source_connection_id=source_connection.id,
        target_connection_id=target_connection.id,
        source_database=VM_PG_DATABASE,
        source_schema="public",
        source_tables=[table_name],
        target_database=SQL_SERVER_DATABASE,
        target_schema="dbo",
        enable_full_load=True  # Enable full load to create schema and copy existing data, then CDC will capture new changes
    )
    
    # Create pipeline (this will also create connections)
    created_pipeline = cdc_manager.create_pipeline(
        pipeline=pipeline,
        source_connection=source_connection,
        target_connection=target_connection
    )
    
    print(f"   ✓ Pipeline created: {created_pipeline.name}")
    
    print(f"\n3. Connection details...")
    print(f"   Python (host): Will connect to {VM_PG_HOST}:{VM_PG_PORT}")
    print(f"   Debezium (Docker): Will connect to {VM_PG_HOST}:{VM_PG_PORT}")
    print(f"   Note: Ensure VM server is accessible from Docker container")
    
    print(f"\n4. Starting CDC connectors...")
    print(f"   Creating Debezium source connector...")
    print(f"   Creating Kafka Sink connector...")
    
    # Start the pipeline
    result = cdc_manager.start_pipeline(created_pipeline.id)
    
    if result.get("success"):
        print(f"\n   ✓ CDC Pipeline started successfully!")
        print(f"   Status: {result.get('status', 'UNKNOWN')}")
        print(f"\n   Debezium Connector:")
        print(f"     - Name: {result.get('debezium_connector_name', 'N/A')}")
        print(f"     - Status: {result.get('debezium_status', 'N/A')}")
        print(f"\n   Sink Connector:")
        print(f"     - Name: {result.get('sink_connector_name', 'N/A')}")
        print(f"     - Status: {result.get('sink_status', 'N/A')}")
        print(f"\n   Kafka Topics:")
        for topic in result.get('topics', []):
            print(f"     - {topic}")
        
        print("\n" + "=" * 60)
        print("✓ CDC Pipeline is now running!")
        print("=" * 60)
        print("\nReal-time replication is active:")
        print(f"- Changes to {VM_PG_DATABASE}.public.{table_name} will be captured")
        print(f"- Changes will be replicated to {SQL_SERVER_DATABASE}.dbo.{table_name}")
    else:
        print(f"\n   ✗ Failed to start pipeline: {result.get('error', 'Unknown error')}")
        sys.exit(1)
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

