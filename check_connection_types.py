"""Check connection database types to diagnose boto3 error."""

import sys
import os

# Add the ingestion directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ingestion'))

try:
    from ingestion.database import SessionLocal
    from ingestion.database.models_db import ConnectionModel
    
    print("=" * 70)
    print("Checking Connection Database Types")
    print("=" * 70)
    
    session = SessionLocal()
    
    try:
        connections = session.query(ConnectionModel).all()
        
        print(f"\nFound {len(connections)} connection(s):\n")
        
        for conn in connections:
            db_type = conn.database_type
            if hasattr(db_type, 'value'):
                db_type = db_type.value
            db_type_str = str(db_type).lower()
            
            print(f"Connection: {conn.name} (ID: {conn.id})")
            print(f"  Database Type: {db_type_str}")
            print(f"  Host: {conn.host}")
            print(f"  Database: {conn.database}")
            print(f"  Connection Type: {conn.connection_type}")
            
            if db_type_str == "s3":
                print(f"  ⚠️  WARNING: This connection is set to S3 type!")
                print(f"     If this is actually SQL Server or PostgreSQL, the database_type is incorrect.")
            
            print()
        
        # Check for pipelines with potential issues
        from ingestion.database.models_db import PipelineModel
        pipelines = session.query(PipelineModel).all()
        
        print(f"\nChecking {len(pipelines)} pipeline(s) for connection type issues:\n")
        
        for pipeline in pipelines:
            source_conn = session.query(ConnectionModel).filter_by(id=pipeline.source_connection_id).first()
            target_conn = session.query(ConnectionModel).filter_by(id=pipeline.target_connection_id).first()
            
            if source_conn and target_conn:
                source_type = str(source_conn.database_type).lower()
                if hasattr(source_conn.database_type, 'value'):
                    source_type = str(source_conn.database_type.value).lower()
                
                target_type = str(target_conn.database_type).lower()
                if hasattr(target_conn.database_type, 'value'):
                    target_type = str(target_conn.database_type.value).lower()
                
                print(f"Pipeline: {pipeline.name} (ID: {pipeline.id})")
                print(f"  Source: {source_conn.name} ({source_type})")
                print(f"  Target: {target_conn.name} ({target_type})")
                
                if target_type == "s3":
                    print(f"  ⚠️  WARNING: Target connection is S3 type!")
                    print(f"     This pipeline will fail when trying to create target schema.")
                    print(f"     Fix: Update the target connection's database_type to the correct type.")
                print()
        
    finally:
        session.close()
    
    print("=" * 70)
    print("Diagnosis Complete")
    print("=" * 70)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()


