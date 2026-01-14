"""Get S3 connection credentials from database."""
import sys
sys.path.insert(0, '.')

from ingestion.database import SessionLocal
from ingestion.database.models_db import ConnectionModel, PipelineModel

db = SessionLocal()

try:
    pipeline = db.query(PipelineModel).filter(PipelineModel.name == 'AS400-S3_P').first()
    
    if pipeline:
        print("=" * 70)
        print("S3 Target Connection Credentials")
        print("=" * 70)
        
        target_conn = db.query(ConnectionModel).filter(
            ConnectionModel.id == pipeline.target_connection_id
        ).first()
        
        if target_conn:
            print(f"\nConnection Name: {target_conn.name}")
            print(f"Database (Bucket): {target_conn.database}")
            print(f"Username (Access Key ID): {target_conn.username}")
            print(f"Password (Secret Key): {'***' + target_conn.password[-4:] if target_conn.password else 'NOT SET'}")
            print(f"\nAdditional Config:")
            if target_conn.additional_config:
                import json
                config = target_conn.additional_config
                print(f"  aws_access_key_id: {config.get('aws_access_key_id', 'NOT SET')}")
                print(f"  aws_secret_access_key: {'SET' if config.get('aws_secret_access_key') else 'NOT SET'} (hidden)")
                print(f"  region_name: {config.get('region_name', 'NOT SET')}")
            else:
                print("  No additional config")
            
            print(f"\n{'='*70}")
            print("Use these credentials in the connector config:")
            print(f"  aws.access.key.id: {target_conn.username or (target_conn.additional_config.get('aws_access_key_id') if target_conn.additional_config else 'NOT SET')}")
            print(f"  aws.secret.access.key: (from password field or additional_config)")
            print(f"{'='*70}")
        else:
            print("❌ Target connection not found!")
    else:
        print("❌ Pipeline not found!")
        
finally:
    db.close()



