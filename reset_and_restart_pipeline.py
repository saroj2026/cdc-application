"""Script to reset pipeline status and restart it."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ingestion.database.session import SessionLocal
from ingestion.database.models_db import PipelineModel, PipelineStatus, CDCStatus
from datetime import datetime

def reset_and_restart_pipeline(pipeline_name: str):
    """Reset pipeline status to STOPPED and prepare for restart.
    
    Args:
        pipeline_name: Name of the pipeline to reset
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
        
        print(f"📋 Found pipeline: {pipeline.name}")
        print(f"   Current status: {pipeline.status}")
        print(f"   Current CDC status: {pipeline.cdc_status}")
        
        # Reset status to STOPPED
        old_status = pipeline.status
        pipeline.status = PipelineStatus.STOPPED
        pipeline.cdc_status = CDCStatus.STOPPED
        pipeline.updated_at = datetime.utcnow()
        
        db.commit()
        
        print(f"✅ Successfully reset pipeline status:")
        print(f"   Old status: {old_status}")
        print(f"   New status: {pipeline.status.value}")
        print(f"   CDC status: {pipeline.cdc_status.value}")
        print(f"\n💡 Next steps:")
        print(f"   1. Start the pipeline via UI or API")
        print(f"   2. Or use: POST /api/v1/pipelines/{pipeline.id}/start")
        print(f"   3. The pipeline will create connectors and start CDC")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error resetting pipeline: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    pipeline_name = "ps_sn_p"
    
    print(f"🔄 Resetting pipeline '{pipeline_name}' status...\n")
    success = reset_and_restart_pipeline(pipeline_name)
    
    if success:
        print(f"\n✅ Pipeline reset successfully!")
        print(f"   You can now start the pipeline again.")
    else:
        print(f"\n❌ Failed to reset pipeline.")
        sys.exit(1)


