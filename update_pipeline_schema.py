"""Update pipeline to use a schema without special characters."""
import sys
from ingestion.database.session import get_db
from ingestion.database.models_db import PipelineModel

PIPELINE_ID = "3b06bbae-2bbc-4526-ad6f-4e5d12c14f04"
NEW_SCHEMA = "cdc_user"  # Changed from c##cdc_user to cdc_user

print(f"=== UPDATING PIPELINE SCHEMA ===")
print(f"Pipeline ID: {PIPELINE_ID}")
print(f"Old Schema: c##cdc_user")
print(f"New Schema: {NEW_SCHEMA}")

db = next(get_db())
try:
    pipeline = db.query(PipelineModel).filter_by(id=PIPELINE_ID).first()
    
    if not pipeline:
        print(f"ERROR: Pipeline not found!")
        sys.exit(1)
    
    old_schema = pipeline.source_schema
    pipeline.source_schema = NEW_SCHEMA
    
    db.commit()
    
    print(f"✓ Updated pipeline source_schema from '{old_schema}' to '{NEW_SCHEMA}'")
    print(f"\nNOTE: You'll need to:")
    print(f"  1. Create the schema/user '{NEW_SCHEMA}' in Oracle (if it doesn't exist)")
    print(f"  2. Create the 'test' table in that schema")
    print(f"  3. Grant necessary permissions")
    print(f"  4. Restart the pipeline")
    
except Exception as e:
    db.rollback()
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    db.close()

