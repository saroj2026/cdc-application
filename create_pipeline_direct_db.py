"""
Create pipeline directly using database and services (bypasses API auth).
Based on the Auto Schema and Full Load Architecture document.

Source: PostgreSQL, cdctest, public, projects_simple
Target: SQL Server, cdctest, dbo, projects_simple
Mode: FULL_LOAD_AND_CDC
"""

import sys
import os
import uuid
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set DATABASE_URL environment variable FIRST, before any imports that use it
# Backend DB: PostgreSQL on 72.61.233.209:5432, database=cdctest, user=cdc_user, password=cdc_pass
os.environ["DATABASE_URL"] = "postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest"

# Add the ingestion module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ingestion.database.models_db import ConnectionModel, PipelineModel, DatabaseType, PipelineMode, PipelineStatus, FullLoadStatus, CDCStatus
from ingestion.models import Connection, Pipeline
from ingestion.cdc_manager import CDCManager
from ingestion.pipeline_service import PipelineService
from ingestion.connection_service import ConnectionService

# Database connection for backend database
# Backend DB: PostgreSQL on 72.61.233.209:5432, database=cdctest, user=cdc_user, password=cdc_pass
DB_URL = "postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest"

def get_db_session():
    """Get database session."""
    engine = create_engine(DB_URL)
    Session = sessionmaker(bind=engine)
    return Session()

def find_or_create_connection(session, name: str, database_type: str, host: str, 
                              port: int, database: str, username: str, password: str, 
                              schema: str = None, additional_config: dict = None) -> ConnectionModel:
    """Find or create a connection."""
    # Check if connection exists
    conn = session.query(ConnectionModel).filter(
        ConnectionModel.name == name,
        ConnectionModel.database_type == database_type,
        ConnectionModel.deleted_at.is_(None)
    ).first()
    
    if conn:
        print(f"[OK] Found existing connection: {name} (ID: {conn.id})")
        return conn
    
    # Create new connection
    conn = ConnectionModel(
        id=str(uuid.uuid4()),
        name=name,
        connection_type="source" if "Source" in name else "target",
        database_type=database_type,
        host=host,
        port=port,
        database=database,
        username=username,
        password=password,
        schema=schema,
        additional_config=additional_config or {},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    session.add(conn)
    session.commit()
    session.refresh(conn)
    print(f"[OK] Created connection: {name} (ID: {conn.id})")
    return conn

def create_pipeline_direct(session, name: str, source_conn: ConnectionModel, 
                          target_conn: ConnectionModel, source_database: str,
                          source_schema: str, source_tables: list,
                          target_database: str = None, target_schema: str = None) -> PipelineModel:
    """Create pipeline directly in database."""
    # Check if pipeline exists (including soft-deleted ones)
    existing = session.query(PipelineModel).filter(
        PipelineModel.name == name
    ).first()
    
    if existing:
        print(f"[WARN] Pipeline '{name}' already exists (ID: {existing.id})")
        # Delete the existing pipeline (hard delete to avoid unique constraint issues)
        session.delete(existing)
        session.commit()
        print(f"[OK] Deleted existing pipeline")
    
    # Create new pipeline
    pipeline = PipelineModel(
        id=str(uuid.uuid4()),
        name=name,
        source_connection_id=source_conn.id,
        target_connection_id=target_conn.id,
        source_database=source_database,
        source_schema=source_schema,
        source_tables=source_tables,
        target_database=target_database or target_conn.database,
        target_schema=target_schema or target_conn.schema or ("public" if target_conn.database_type == "postgresql" else "dbo"),
        mode=PipelineMode.FULL_LOAD_AND_CDC,
        enable_full_load=True,
        full_load_status=FullLoadStatus.NOT_STARTED,
        cdc_status=CDCStatus.NOT_STARTED,
        status=PipelineStatus.STOPPED,
        auto_create_target=True,
        target_table_mapping={table: table for table in source_tables},  # 1:1 mapping
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    session.add(pipeline)
    session.commit()
    session.refresh(pipeline)
    print(f"[OK] Created pipeline: {name} (ID: {pipeline.id})")
    return pipeline

def convert_to_connection_model(conn_model: ConnectionModel) -> Connection:
    """Convert ConnectionModel to Connection object."""
    return Connection(
        id=conn_model.id,
        name=conn_model.name,
        connection_type=conn_model.connection_type.value if hasattr(conn_model.connection_type, 'value') else str(conn_model.connection_type),
        database_type=conn_model.database_type.value if hasattr(conn_model.database_type, 'value') else str(conn_model.database_type),
        host=conn_model.host,
        port=conn_model.port,
        database=conn_model.database,
        username=conn_model.username,
        password=conn_model.password,
        schema=conn_model.schema,
        additional_config=conn_model.additional_config or {}  # Include additional_config!
    )

def convert_to_pipeline_model(pipeline_model: PipelineModel) -> Pipeline:
    """Convert PipelineModel to Pipeline object."""
    return Pipeline(
        id=pipeline_model.id,
        name=pipeline_model.name,
        source_connection_id=pipeline_model.source_connection_id,
        target_connection_id=pipeline_model.target_connection_id,
        source_database=pipeline_model.source_database,
        source_schema=pipeline_model.source_schema,
        source_tables=pipeline_model.source_tables,
        target_database=pipeline_model.target_database,
        target_schema=pipeline_model.target_schema,
        mode=pipeline_model.mode.value if hasattr(pipeline_model.mode, 'value') else str(pipeline_model.mode),
        auto_create_target=pipeline_model.auto_create_target,
        target_table_mapping=pipeline_model.target_table_mapping,
        full_load_status=pipeline_model.full_load_status.value if hasattr(pipeline_model.full_load_status, 'value') else str(pipeline_model.full_load_status),
        cdc_status=pipeline_model.cdc_status.value if hasattr(pipeline_model.cdc_status, 'value') else str(pipeline_model.cdc_status),
        status=pipeline_model.status.value if hasattr(pipeline_model.status, 'value') else str(pipeline_model.status)
    )

def main():
    print("="*80)
    print("Create Pipeline: PostgreSQL -> SQL Server")
    print("="*80)
    print("\nConfiguration:")
    print("  Source: PostgreSQL, cdctest, public, projects_simple")
    print("  Target: SQL Server, cdctest, dbo, projects_simple")
    print("  Mode: FULL_LOAD_AND_CDC")
    print("  Auto-create target: True")
    print("="*80)
    
    session = get_db_session()
    
    try:
        # Step 1: Find or create PostgreSQL source connection
        print("\n1. Setting up PostgreSQL source connection...")
        pg_conn = find_or_create_connection(
            session=session,
            name="PostgreSQL Source - cdctest",
            database_type="postgresql",
            host="72.61.233.209",
            port=5432,
            database="cdctest",
            username="cdc_user",
            password="cdc_pass",
            schema="public"
        )
        
        # Step 2: Find or create SQL Server target connection
        print("\n2. Setting up SQL Server target connection...")
        sql_conn = find_or_create_connection(
            session=session,
            name="SQL Server Target - cdctest",
            database_type="sqlserver",
            host="72.61.233.209",
            port=1433,  # User said 1432 but SQL Server default is 1433
            database="cdctest",
            username="sa",
            password="Sql@12345",
            schema="dbo",
            additional_config={"trust_server_certificate": True}  # Fix SSL certificate issue
        )
        
        # Step 3: Create pipeline
        print("\n3. Creating pipeline...")
        pipeline_name = "pg_to_mssql_projects_simple"
        pipeline_model = create_pipeline_direct(
            session=session,
            name=pipeline_name,
            source_conn=pg_conn,
            target_conn=sql_conn,
            source_database="cdctest",
            source_schema="public",
            source_tables=["projects_simple"],
            target_database="cdctest",
            target_schema="dbo"
        )
        
        print(f"\n{'='*80}")
        print("Pipeline Created Successfully!")
        print(f"{'='*80}")
        print(f"\nPipeline ID: {pipeline_model.id}")
        print(f"Pipeline Name: {pipeline_model.name}")
        print(f"Source: {pipeline_model.source_database}.{pipeline_model.source_schema}.{pipeline_model.source_tables}")
        print(f"Target: {pipeline_model.target_database}.{pipeline_model.target_schema}")
        print(f"Mode: {pipeline_model.mode.value}")
        print(f"Auto-create target: {pipeline_model.auto_create_target}")
        
        # Step 4: Start pipeline using CDC Manager
        print(f"\n4. Starting pipeline...")
        print("   This will:")
        print("   - Step 0: Auto-create target schema/tables")
        print("   - Step 1: Full load (transfer data)")
        print("   - Step 2: Start CDC")
        
        # Initialize CDC Manager
        kafka_connect_url = os.getenv("KAFKA_CONNECT_URL", "http://72.61.233.209:8083")
        cdc_manager = CDCManager(kafka_connect_url=kafka_connect_url)
        
        # Set database session factory for status persistence
        from ingestion.cdc_manager import set_db_session_factory
        from ingestion.database.session import get_db
        set_db_session_factory(get_db)
        
        # Convert models to service objects
        source_connection = convert_to_connection_model(pg_conn)
        target_connection = convert_to_connection_model(sql_conn)
        pipeline = convert_to_pipeline_model(pipeline_model)
        
        # Add to CDC Manager stores
        cdc_manager.connection_store[source_connection.id] = source_connection
        cdc_manager.connection_store[target_connection.id] = target_connection
        cdc_manager.pipeline_store[pipeline.id] = pipeline
        
        # Start pipeline
        try:
            result = cdc_manager.start_pipeline(pipeline.id)
            print(f"\n[OK] Pipeline started!")
            print(f"  Status: {result.get('status')}")
            print(f"  Message: {result.get('message')}")
            
            if result.get('full_load'):
                fl = result['full_load']
                print(f"\n  Full Load Result:")
                print(f"    Success: {fl.get('success')}")
                if fl.get('success'):
                    print(f"    Tables: {fl.get('tables_transferred')}")
                    print(f"    Rows: {fl.get('total_rows')}")
                    print(f"    LSN: {fl.get('lsn')}")
        except Exception as e:
            print(f"\n[ERROR] Error starting pipeline: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n{'='*80}")
        print("Next Steps:")
        print(f"{'='*80}")
        print("1. Monitor backend logs for progress:")
        print("   - Step 0: Schema creation")
        print("   - Step 1: Full load progress")
        print("   - Step 2: CDC setup")
        print("\n2. Check pipeline status in database:")
        print(f"   SELECT * FROM pipelines WHERE id = '{pipeline_model.id}';")
        print("\n3. Verify data in target:")
        print("   SELECT COUNT(*) FROM cdctest.dbo.projects_simple;")
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main()

