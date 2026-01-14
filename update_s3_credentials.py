"""Update S3 connection credentials in database."""
import sys
sys.path.insert(0, '.')

from ingestion.database import SessionLocal
from ingestion.database.models_db import ConnectionModel, PipelineModel

# New AWS credentials
NEW_ACCESS_KEY = "AKIATLTXNANW2JU6WWAH"
NEW_SECRET_KEY = "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"

db = SessionLocal()

try:
    # Find the AS400-S3_P pipeline
    pipeline = db.query(PipelineModel).filter(PipelineModel.name == 'AS400-S3_P').first()
    
    if not pipeline:
        print("❌ Pipeline 'AS400-S3_P' not found!")
        sys.exit(1)
    
    # Get the target S3 connection
    target_conn = db.query(ConnectionModel).filter(
        ConnectionModel.id == pipeline.target_connection_id
    ).first()
    
    if not target_conn:
        print("❌ Target connection not found!")
        sys.exit(1)
    
    print("=" * 70)
    print("Updating S3 Connection Credentials")
    print("=" * 70)
    
    print(f"\nCurrent Connection:")
    print(f"  Name: {target_conn.name}")
    print(f"  Bucket: {target_conn.database}")
    print(f"  Old Access Key: {target_conn.username}")
    
    # Update credentials
    target_conn.username = NEW_ACCESS_KEY
    target_conn.password = NEW_SECRET_KEY
    
    # Update additional_config if it exists
    if target_conn.additional_config:
        target_conn.additional_config['aws_access_key_id'] = NEW_ACCESS_KEY
        target_conn.additional_config['aws_secret_access_key'] = NEW_SECRET_KEY
    else:
        target_conn.additional_config = {
            'aws_access_key_id': NEW_ACCESS_KEY,
            'aws_secret_access_key': NEW_SECRET_KEY,
            'region_name': 'us-east-1'
        }
    
    db.commit()
    
    print(f"\n✅ Updated Connection:")
    print(f"  Name: {target_conn.name}")
    print(f"  Bucket: {target_conn.database}")
    print(f"  New Access Key: {target_conn.username}")
    print(f"  Secret Key: {'***' + target_conn.password[-4:] if target_conn.password else 'NOT SET'}")
    
    print(f"\n{'='*70}")
    print("Next Steps:")
    print("  1. Update Kafka Connect connector configuration:")
    print(f"     aws.access.key.id: {NEW_ACCESS_KEY}")
    print(f"     aws.secret.access.key: {NEW_SECRET_KEY}")
    print("  2. Restart the connector in Kafka UI")
    print("  3. Verify connector status is RUNNING")
    print(f"{'='*70}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
    sys.exit(1)
finally:
    db.close()



