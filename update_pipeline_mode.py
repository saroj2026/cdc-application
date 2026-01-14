"""Script to update pipeline mode to full_load_and_cdc."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ingestion.database.session import SessionLocal
from ingestion.database.models_db import PipelineModel, PipelineMode
from datetime import datetime

def update_pipeline_mode(pipeline_name: str, new_mode: str = "full_load_and_cdc"):
    """Update pipeline mode.
    
    Args:
        pipeline_name: Name of the pipeline to update
        new_mode: New mode value (default: "full_load_and_cdc")
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
        print(f"   Current mode: {pipeline.mode}")
        print(f"   Current status: {pipeline.status}")
        print(f"   Full load status: {pipeline.full_load_status}")
        print(f"   CDC status: {pipeline.cdc_status}")
        
        # Validate mode
        valid_modes = [mode.value for mode in PipelineMode]
        if new_mode not in valid_modes:
            print(f"❌ Invalid mode: {new_mode}")
            print(f"   Valid modes: {valid_modes}")
            return False
        
        # Update mode
        old_mode = pipeline.mode
        pipeline.mode = PipelineMode(new_mode)
        pipeline.updated_at = datetime.utcnow()
        
        db.commit()
        
        print(f"✅ Successfully updated pipeline mode:")
        print(f"   Old mode: {old_mode}")
        print(f"   New mode: {pipeline.mode.value}")
        print(f"   Updated at: {pipeline.updated_at}")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating pipeline: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    pipeline_name = "ps_sn_p"
    new_mode = "full_load_and_cdc"
    
    print(f"🔄 Updating pipeline '{pipeline_name}' to mode '{new_mode}'...")
    success = update_pipeline_mode(pipeline_name, new_mode)
    
    if success:
        print(f"\n✅ Pipeline mode updated successfully!")
        print(f"   You can now start the pipeline to enable full load and CDC.")
    else:
        print(f"\n❌ Failed to update pipeline mode.")
        sys.exit(1)


