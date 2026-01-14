"""Check if AS400 record (id=333, name=KISHOR) is in S3 bucket."""
import sys
import os
import json
import boto3
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from ingestion.database import SessionLocal
from ingestion.database.models_db import PipelineModel

# S3 Configuration (will get from pipeline)
S3_CONFIG = {
    "bucket": "mycdcbucket26",
    "aws_access_key_id": "AKIATLTXNANW2EV7QGV2",
    "aws_secret_access_key": "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",
    "region_name": "us-east-1"
}

print("=" * 70)
print("Checking AS400-S3_P Pipeline for Record: id=333, name=KISHOR")
print("=" * 70)

try:
    # Get pipeline details
    db = SessionLocal()
    pipeline = db.query(PipelineModel).filter(PipelineModel.name == 'AS400-S3_P').first()
    
    if not pipeline:
        print("❌ Pipeline 'AS400-S3_P' not found!")
        sys.exit(1)
    
    print(f"\n✅ Pipeline Found: {pipeline.name}")
    print(f"   Pipeline ID: {pipeline.id}")
    print(f"   Source: {pipeline.source_database}/{pipeline.source_schema}")
    print(f"   Target: {pipeline.target_database}")
    print(f"   Status: {pipeline.status.value if pipeline.status else 'Unknown'}")
    print(f"   CDC Status: {pipeline.cdc_status.value if pipeline.cdc_status else 'Unknown'}")
    print(f"   Source Tables: {pipeline.source_tables}")
    
    # Get S3 connection details from target connection
    from ingestion.database.models_db import ConnectionModel
    target_conn = db.query(ConnectionModel).filter(ConnectionModel.id == pipeline.target_connection_id).first()
    
    if target_conn:
        print(f"\n   S3 Bucket: {target_conn.database}")
        print(f"   S3 Prefix: {target_conn.schema or ''}")
        S3_CONFIG["bucket"] = target_conn.database
        if target_conn.schema:
            s3_prefix = target_conn.schema
        else:
            s3_prefix = ""
        
        # Get AWS credentials from target connection
        if target_conn.additional_config:
            if 'aws_access_key_id' in target_conn.additional_config:
                S3_CONFIG["aws_access_key_id"] = target_conn.additional_config['aws_access_key_id']
            if 'aws_secret_access_key' in target_conn.additional_config:
                S3_CONFIG["aws_secret_access_key"] = target_conn.additional_config['aws_secret_access_key']
            if 'region_name' in target_conn.additional_config:
                S3_CONFIG["region_name"] = target_conn.additional_config['region_name']
    else:
        s3_prefix = ""
    
    db.close()
    
    # Create S3 client
    print(f"\n2. Connecting to S3 bucket: {S3_CONFIG['bucket']}")
    s3_client = boto3.client(
        's3',
        aws_access_key_id=S3_CONFIG['aws_access_key_id'],
        aws_secret_access_key=S3_CONFIG['aws_secret_access_key'],
        region_name=S3_CONFIG['region_name']
    )
    
    # List all objects in the bucket (with prefix if specified)
    print(f"   Prefix: {s3_prefix if s3_prefix else '(none)'}")
    print(f"   Region: {S3_CONFIG['region_name']}\n")
    
    print("3. Searching for tables and CDC data...\n")
    
    # List objects
    try:
        if s3_prefix:
            response = s3_client.list_objects_v2(Bucket=S3_CONFIG['bucket'], Prefix=s3_prefix)
        else:
            response = s3_client.list_objects_v2(Bucket=S3_CONFIG['bucket'])
        
        if 'Contents' not in response:
            print("   ⚠️  No objects found in bucket")
            print("   This could mean:")
            print("      - CDC data hasn't been written yet")
            print("      - Data is in a different prefix")
            print("      - Pipeline is not running")
            sys.exit(1)
        
        objects = response['Contents']
        print(f"   ✅ Found {len(objects)} object(s) in bucket\n")
        
        # Group by table/prefix
        table_files = {}
        cdc_files = []
        
        for obj in objects:
            key = obj['Key']
            # Check for CDC format (usually topic-based: server.database.schema.table)
            # Or S3 sink format (table_name/partition files)
            
            # S3 Sink Connector format: topics/<topic>/partition=<n>/<topic>+<partition>+<offset>.json
            if 'topics/' in key or '/partition=' in key:
                cdc_files.append(key)
            # Or table-based structure
            elif '/' in key:
                parts = key.split('/')
                table_name = parts[0] if parts else key
                if table_name not in table_files:
                    table_files[table_name] = []
                table_files[table_name].append({
                    'key': key,
                    'size': obj['Size'],
                    'modified': obj['LastModified']
                })
        
        # Search for the record in all relevant files
        print("4. Searching for record (id=333, name=KISHOR)...\n")
        
        found = False
        search_files = []
        
        # Get all JSON files to search
        all_json_files = []
        for obj in objects:
            if obj['Key'].endswith('.json'):
                all_json_files.append(obj['Key'])
        
        print(f"   Searching in {len(all_json_files)} JSON file(s)...\n")
        
        for file_key in all_json_files[:50]:  # Limit to first 50 files
            try:
                obj_response = s3_client.get_object(
                    Bucket=S3_CONFIG['bucket'],
                    Key=file_key
                )
                content = obj_response['Body'].read().decode('utf-8')
                
                # Try to parse as JSON
                try:
                    # Could be single JSON object or array
                    if content.strip().startswith('['):
                        data = json.loads(content)
                        if isinstance(data, list):
                            for record in data:
                                if isinstance(record, dict):
                                    # Check for id=333 and name=KISHOR
                                    record_id = record.get('id') or record.get('ID') or record.get('Id')
                                    record_name = record.get('name') or record.get('NAME') or record.get('Name')
                                    
                                    if str(record_id) == '333' and str(record_name).upper() == 'KISHOR':
                                        found = True
                                        print(f"   ✅ FOUND in file: {file_key}")
                                        print(f"      Record: {json.dumps(record, indent=6)}")
                                        search_files.append(file_key)
                    else:
                        # Single JSON object or newline-delimited JSON
                        for line in content.strip().split('\n'):
                            if line.strip():
                                try:
                                    record = json.loads(line)
                                    if isinstance(record, dict):
                                        # Check for id=333 and name=KISHOR
                                        record_id = record.get('id') or record.get('ID') or record.get('Id')
                                        record_name = record.get('name') or record.get('NAME') or record.get('Name')
                                        
                                        if str(record_id) == '333' and str(record_name).upper() == 'KISHOR':
                                            found = True
                                            print(f"   ✅ FOUND in file: {file_key}")
                                            print(f"      Record: {json.dumps(record, indent=6)}")
                                            search_files.append(file_key)
                                            break
                                except:
                                    pass
                except json.JSONDecodeError:
                    # Not JSON, skip
                    pass
                    
            except Exception as e:
                # Skip files that can't be read
                pass
        
        if not found:
            print("   ❌ Record NOT FOUND in searched files")
            print(f"\n   Searched {len(all_json_files)} JSON file(s)")
            print(f"   Total objects in bucket: {len(objects)}")
            print("\n   Possible reasons:")
            print("      - Data hasn't been replicated yet (check pipeline status)")
            print("      - Data is in a file not yet searched")
            print("      - Table name or field names are different")
            print("      - Data format is different than expected")
        else:
            print(f"\n   ✅ Record found in {len(search_files)} file(s)")
        
        # Show table structure
        if table_files:
            print(f"\n5. Tables found in S3:\n")
            for table_name in sorted(table_files.keys())[:10]:
                files = table_files[table_name]
                print(f"   📁 {table_name}/ ({len(files)} file(s))")
        
        if cdc_files:
            print(f"\n   CDC files found: {len(cdc_files)}")
            print(f"   Sample: {cdc_files[0] if cdc_files else 'N/A'}")
        
    except Exception as e:
        print(f"   ❌ Error accessing S3: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    if found:
        print("✅ VERIFICATION: Record found in S3 bucket!")
    else:
        print("⚠️  VERIFICATION: Record not found (may need to check more files)")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)



