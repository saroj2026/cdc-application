import requests
import json
from ingestion.database.session import get_db
from ingestion.database.models_db import PipelineModel, ConnectionModel

PIPELINE_ID = "3b06bbae-2bbc-4526-ad6f-4e5d12c14f04"

print("=== CURRENT PIPELINE CONFIG ===")
db = next(get_db())
pipeline = db.query(PipelineModel).filter_by(id=PIPELINE_ID).first()

if pipeline:
    print(f"Pipeline Name: {pipeline.name}")
    print(f"Source Schema: {pipeline.source_schema}")
    print(f"Source Database: {pipeline.source_database}")
    print(f"Source Tables: {pipeline.source_tables}")
    
    # Get source connection
    source_conn = db.query(ConnectionModel).filter_by(id=pipeline.source_connection_id).first()
    if source_conn:
        print(f"\nSource Connection:")
        print(f"  Name: {source_conn.name}")
        print(f"  Host: {source_conn.host}")
        print(f"  Database: {source_conn.database}")
        print(f"  Username: {source_conn.username}")
        print(f"  Schema (if any): {getattr(source_conn, 'schema', 'N/A')}")

db.close()

