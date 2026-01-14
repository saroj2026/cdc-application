"""Automatically enable CDC for S3 pipelines by changing mode from FULL_LOAD_ONLY to FULL_LOAD_AND_CDC."""

import sys
import os

# Add the ingestion directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ingestion'))

try:
    from ingestion.database import SessionLocal
    from ingestion.database.models_db import PipelineModel, ConnectionModel
    from sqlalchemy import text
    
    print("=" * 70)
    print("Enable CDC for S3 Pipelines (Auto)")
    print("=" * 70)
    
    session = SessionLocal()
    
    try:
        # Find all pipelines with S3 targets that are in FULL_LOAD_ONLY mode
        pipelines = session.query(PipelineModel).filter(
            PipelineModel.deleted_at.is_(None)
        ).all()
        
        s3_pipelines = []
        for pipeline in pipelines:
            # Get target connection
            target_conn = session.query(ConnectionModel).filter_by(
                id=pipeline.target_connection_id
            ).first()
            
            if target_conn:
                target_db_type = str(target_conn.database_type).lower()
                if hasattr(target_conn.database_type, 'value'):
                    target_db_type = str(target_conn.database_type.value).lower()
                
                # Normalize
                if target_db_type in ['aws_s3', 's3']:
                    target_db_type = 's3'
                
                if target_db_type == 's3':
                    pipeline_mode = str(pipeline.mode).lower()
                    if hasattr(pipeline.mode, 'value'):
                        pipeline_mode = str(pipeline.mode.value).lower()
                    
                    if pipeline_mode == 'full_load_only':
                        s3_pipelines.append((pipeline, target_conn))
        
        if not s3_pipelines:
            print("\n✅ No S3 pipelines found with FULL_LOAD_ONLY mode.")
            print("   All S3 pipelines already have CDC enabled or are not in FULL_LOAD_ONLY mode.")
        else:
            print(f"\nFound {len(s3_pipelines)} S3 pipeline(s) with FULL_LOAD_ONLY mode:\n")
            
            for pipeline, target_conn in s3_pipelines:
                print(f"  - {pipeline.name} (ID: {pipeline.id})")
                print(f"    Current mode: FULL_LOAD_ONLY")
                print(f"    Target: {target_conn.name} (S3)")
                print(f"    Status: {pipeline.status}")
                print()
            
            print("\n" + "-" * 70)
            print(f"\n🔄 Automatically enabling CDC for {len(s3_pipelines)} pipeline(s)...\n")
            
            updated_count = 0
            for pipeline, target_conn in s3_pipelines:
                try:
                    # Update mode to FULL_LOAD_AND_CDC using raw SQL to bypass enum validation
                    session.execute(text("""
                        UPDATE pipelines 
                        SET mode = :new_mode,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = :pipeline_id
                    """), {
                        "new_mode": "full_load_and_cdc",
                        "pipeline_id": pipeline.id
                    })
                    updated_count += 1
                    print(f"  ✅ Updated {pipeline.name} to FULL_LOAD_AND_CDC mode")
                except Exception as e:
                    print(f"  ❌ Failed to update {pipeline.name}: {e}")
                    session.rollback()
            
            if updated_count > 0:
                session.commit()
                print(f"\n✅ Successfully updated {updated_count} pipeline(s).")
                print("\n⚠️  IMPORTANT: You need to restart the pipeline for the changes to take effect.")
                print("   Steps:")
                print("   1. Stop the pipeline (if it's running)")
                print("   2. Start/Trigger the pipeline again")
                print("   3. The pipeline will now enable CDC after full load completes.")
                print("   4. CDC events will be written to S3 as JSON files.")
            else:
                print("\n⚠️  No pipelines were updated.")
        
        # Show all S3 pipelines and their current modes
        print("\n" + "-" * 70)
        print("All S3 Pipelines Summary:\n")
        
        all_s3_pipelines = []
        for pipeline in pipelines:
            target_conn = session.query(ConnectionModel).filter_by(
                id=pipeline.target_connection_id
            ).first()
            
            if target_conn:
                target_db_type = str(target_conn.database_type).lower()
                if hasattr(target_conn.database_type, 'value'):
                    target_db_type = str(target_conn.database_type.value).lower()
                
                if target_db_type in ['aws_s3', 's3']:
                    pipeline_mode = str(pipeline.mode).lower()
                    if hasattr(pipeline.mode, 'value'):
                        pipeline_mode = str(pipeline.mode.value).lower()
                    
                    all_s3_pipelines.append((pipeline, target_conn, pipeline_mode))
        
        if all_s3_pipelines:
            for pipeline, target_conn, mode in all_s3_pipelines:
                cdc_status = "✅ CDC Enabled" if mode in ['full_load_and_cdc', 'cdc_only'] else "❌ CDC Disabled"
                print(f"  {pipeline.name}: {mode.upper()} - {cdc_status}")
        else:
            print("  No S3 pipelines found.")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()
    
    print("\n" + "=" * 70)
    print("Complete")
    print("=" * 70)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()


