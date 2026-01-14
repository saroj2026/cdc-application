#!/usr/bin/env python3
"""Find Oracle and Snowflake connections from pipeline."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ingestion.database.session import get_db
from ingestion.database.models_db import ConnectionModel, PipelineModel

db = next(get_db())

try:
    # Get pipeline
    pipeline = db.query(PipelineModel).filter_by(name="oracle_sf_p").first()
    if not pipeline:
        print("❌ Pipeline 'oracle_sf_p' not found")
        exit(1)
    
    print("Pipeline:", pipeline.name)
    print("Source Connection ID:", pipeline.source_connection_id)
    print("Target Connection ID:", pipeline.target_connection_id)
    
    # Get source connection
    source_conn = db.query(ConnectionModel).filter_by(id=pipeline.source_connection_id).first()
    if source_conn:
        print(f"\nSource Connection:")
        print(f"  Name: {source_conn.name}")
        print(f"  Type: {source_conn.database_type}")
        print(f"  Host: {source_conn.host}")
        print(f"  User: {source_conn.username}")
    
    # Get target connection
    target_conn = db.query(ConnectionModel).filter_by(id=pipeline.target_connection_id).first()
    if target_conn:
        print(f"\nTarget Connection:")
        print(f"  Name: {target_conn.name}")
        print(f"  Type: {target_conn.database_type}")
        print(f"  Host: {target_conn.host}")
        print(f"  User: {target_conn.username}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

