"""Verify data uploaded to S3 bucket during full load."""

import boto3
import json
from datetime import datetime

# S3 Connection details from the pipeline
S3_CONFIG = {
    "bucket": "mycdcbucket26",
    "aws_access_key_id": "AKIATLTXNANW2EV7QGV2",
    "aws_secret_access_key": "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",
    "region_name": "us-east-1"
}

# Expected tables from the pipeline
EXPECTED_TABLES = [
    "alembic_version",
    "alert_history",
    "alert_rules",
    "audit_logs",
    "connection_tests"
]

print("=" * 60)
print("S3 Bucket Data Verification")
print("=" * 60)

try:
    # Create S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=S3_CONFIG['aws_access_key_id'],
        aws_secret_access_key=S3_CONFIG['aws_secret_access_key'],
        region_name=S3_CONFIG['region_name']
    )
    
    bucket_name = S3_CONFIG['bucket']
    
    print(f"\n1. Connecting to S3 bucket: {bucket_name}")
    print(f"   Region: {S3_CONFIG['region_name']}\n")
    
    # List all objects in the bucket
    print("2. Listing objects in bucket...\n")
    
    try:
        # List all objects (no prefix filter)
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix="")
        
        if 'Contents' not in response:
            print("   ⚠️  Bucket is empty - no objects found")
            print("   This could mean:")
            print("      - Full load is still in progress")
            print("      - Full load failed silently")
            print("      - Tables were empty (no data to upload)")
            print("      - Upload errors were caught but not logged")
        else:
            objects = response['Contents']
            print(f"   ✅ Found {len(objects)} object(s) in bucket\n")
            
            # Group objects by table name
            table_files = {}
            other_files = []
            
            for obj in objects:
                key = obj['Key']
                size = obj['Size']
                modified = obj['LastModified']
                
                # Check if it's a full load file (format: table_name/full_load_timestamp.json)
                if '/full_load_' in key and key.endswith('.json'):
                    parts = key.split('/')
                    if len(parts) >= 2:
                        table_name = parts[0]
                        if table_name not in table_files:
                            table_files[table_name] = []
                        table_files[table_name].append({
                            'key': key,
                            'size': size,
                            'modified': modified
                        })
                    else:
                        other_files.append({'key': key, 'size': size, 'modified': modified})
                else:
                    other_files.append({'key': key, 'size': size, 'modified': modified})
            
            # Display results
            print("3. Full Load Files Found:\n")
            
            if table_files:
                for table_name in sorted(table_files.keys()):
                    files = table_files[table_name]
                    print(f"   📁 {table_name}/")
                    for file_info in files:
                        size_kb = file_info['size'] / 1024
                        print(f"      ✅ {file_info['key'].split('/')[-1]}")
                        print(f"         Size: {size_kb:.2f} KB")
                        print(f"         Modified: {file_info['modified']}")
                        print()
            else:
                print("   ⚠️  No full load files found matching expected pattern")
            
            if other_files:
                print(f"\n   Other files in bucket ({len(other_files)}):")
                for file_info in other_files[:10]:  # Show first 10
                    print(f"      - {file_info['key']}")
                if len(other_files) > 10:
                    print(f"      ... and {len(other_files) - 10} more")
            
            # Check expected tables
            print("\n4. Expected Tables Check:\n")
            found_tables = set(table_files.keys())
            expected_tables = set(EXPECTED_TABLES)
            
            for table in expected_tables:
                if table in found_tables:
                    print(f"   ✅ {table} - Found")
                else:
                    print(f"   ❌ {table} - Not Found")
            
            missing = expected_tables - found_tables
            extra = found_tables - expected_tables
            
            if missing:
                print(f"\n   ⚠️  Missing tables: {', '.join(missing)}")
            if extra:
                print(f"\n   ℹ️  Extra tables found: {', '.join(extra)}")
            
            # Sample data from first file
            if table_files:
                print("\n5. Sample Data Preview:\n")
                first_table = sorted(table_files.keys())[0]
                first_file = table_files[first_table][0]
                
                print(f"   Reading sample from: {first_file['key']}\n")
                
                try:
                    obj_response = s3_client.get_object(
                        Bucket=bucket_name,
                        Key=first_file['key']
                    )
                    data = json.loads(obj_response['Body'].read().decode('utf-8'))
                    
                    if isinstance(data, list):
                        print(f"   ✅ File contains {len(data)} rows")
                        if data:
                            print(f"\n   First row sample:")
                            print(f"   {json.dumps(data[0], indent=6)}")
                            if len(data) > 1:
                                print(f"\n   ... and {len(data) - 1} more rows")
                    else:
                        print(f"   ⚠️  File format is not a list: {type(data)}")
                        print(f"   Content preview: {str(data)[:200]}...")
                        
                except Exception as e:
                    print(f"   ❌ Error reading file: {e}")
            
            print("\n" + "=" * 60)
            if missing:
                print("⚠️  Verification: Some expected tables are missing")
            else:
                print("✅ Verification: All expected tables found!")
            print("=" * 60)
            
    except Exception as e:
        print(f"   ❌ Error listing objects: {e}")
        if "AccessDenied" in str(e):
            print("   ⚠️  Access denied - check IAM permissions")
        elif "NoSuchBucket" in str(e):
            print("   ⚠️  Bucket not found - check bucket name")
        
except Exception as e:
    print(f"\n❌ Error connecting to S3: {e}")
    print("\nTroubleshooting:")
    print("  1. Check AWS credentials are correct")
    print("  2. Verify bucket name and region")
    print("  3. Ensure IAM user has s3:ListBucket and s3:GetObject permissions")

