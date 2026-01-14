"""Script to check pipeline CDC status and verify CDC is working."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ingestion.database.session import SessionLocal
from ingestion.database.models_db import PipelineModel, ConnectionModel
import json

def check_pipeline_cdc_status(pipeline_name: str):
    """Check pipeline CDC status and details.
    
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
        print(f"   Mode: {pipeline.mode}")
        print(f"   Status: {pipeline.status}")
        print(f"\n📊 Full Load Status:")
        print(f"   Status: {pipeline.full_load_status}")
        print(f"   LSN: {pipeline.full_load_lsn or 'Not set'}")
        
        print(f"\n🔄 CDC Status:")
        print(f"   Status: {pipeline.cdc_status}")
        print(f"   Debezium Connector: {pipeline.debezium_connector_name or 'Not set'}")
        print(f"   Sink Connector: {pipeline.sink_connector_name or 'Not set'}")
        print(f"   Kafka Topics: {', '.join(pipeline.kafka_topics) if pipeline.kafka_topics else 'None'}")
        
        print(f"\n📝 Configuration:")
        print(f"   Source: {pipeline.source_database}.{pipeline.source_schema}")
        print(f"   Source Tables: {', '.join(pipeline.source_tables) if pipeline.source_tables else 'None'}")
        print(f"   Target: {pipeline.target_database or 'N/A'}.{pipeline.target_schema or 'N/A'}")
        
        # Get connection details
        source_conn = db.query(ConnectionModel).filter_by(id=pipeline.source_connection_id).first()
        target_conn = db.query(ConnectionModel).filter_by(id=pipeline.target_connection_id).first()
        
        if source_conn:
            print(f"\n🔌 Source Connection:")
            print(f"   Name: {source_conn.name}")
            print(f"   Type: {source_conn.database_type}")
            print(f"   Database: {source_conn.database}")
        
        if target_conn:
            print(f"\n🎯 Target Connection:")
            print(f"   Name: {target_conn.name}")
            print(f"   Type: {target_conn.database_type}")
            print(f"   Database: {target_conn.database}")
        
        # Check if CDC is active
        print(f"\n✅ CDC Verification:")
        if pipeline.cdc_status in ["RUNNING", "STARTING"]:
            print(f"   ✓ CDC is {'running' if pipeline.cdc_status == 'RUNNING' else 'starting'}")
        else:
            print(f"   ⚠️  CDC status is: {pipeline.cdc_status}")
        
        if pipeline.debezium_connector_name:
            print(f"   ✓ Debezium connector configured: {pipeline.debezium_connector_name}")
        else:
            print(f"   ⚠️  Debezium connector not configured")
        
        if pipeline.sink_connector_name:
            print(f"   ✓ Sink connector configured: {pipeline.sink_connector_name}")
        else:
            print(f"   ⚠️  Sink connector not configured")
        
        if pipeline.kafka_topics:
            print(f"   ✓ Kafka topics configured: {len(pipeline.kafka_topics)} topic(s)")
        else:
            print(f"   ⚠️  No Kafka topics configured")
        
        # Show Debezium config if available
        if pipeline.debezium_config:
            print(f"\n⚙️  Debezium Config (excerpt):")
            config_preview = {k: v for k, v in list(pipeline.debezium_config.items())[:5]}
            print(f"   {json.dumps(config_preview, indent=2)}")
        
        # Show Sink config if available
        if pipeline.sink_config:
            print(f"\n⚙️  Sink Config (excerpt):")
            config_preview = {k: v for k, v in list(pipeline.sink_config.items())[:5]}
            print(f"   {json.dumps(config_preview, indent=2)}")
        
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
    
    print(f"🔍 Checking CDC status for pipeline '{pipeline_name}'...\n")
    check_pipeline_cdc_status(pipeline_name)
    
    print(f"\n💡 To verify CDC is working:")
    print(f"   1. Make a change in the source database (INSERT/UPDATE/DELETE)")
    print(f"   2. Check if the change appears in the target database")
    print(f"   3. Check Kafka topics for messages")
    print(f"   4. Monitor the pipeline status in the UI")


