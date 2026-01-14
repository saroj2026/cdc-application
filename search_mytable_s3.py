"""Search MYTABLE files in S3 for record id=333, name=KISHOR."""
import sys
import os
import json
import boto3

sys.path.insert(0, os.path.dirname(__file__))

S3_CONFIG = {
    "bucket": "mycdcbucket26",
    "aws_access_key_id": "AKIATLTXNANW2EV7QGV2",
    "aws_secret_access_key": "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",
    "region_name": "us-east-1"
}

print("=" * 70)
print("Searching MYTABLE in S3 for: id=333, name=KISHOR")
print("=" * 70)

s3_client = boto3.client(
    's3',
    aws_access_key_id=S3_CONFIG['aws_access_key_id'],
    aws_secret_access_key=S3_CONFIG['aws_secret_access_key'],
    region_name=S3_CONFIG['region_name']
)

# Search in MYTABLE files
print("\n1. Searching MYTABLE files...\n")
response = s3_client.list_objects_v2(Bucket=S3_CONFIG['bucket'], Prefix="MYTABLE/")
mytable_files = []

if 'Contents' in response:
    mytable_files = [obj['Key'] for obj in response['Contents'] if obj['Key'].endswith('.json')]
    print(f"   Found {len(mytable_files)} MYTABLE JSON file(s)\n")
    
    found = False
    for file_key in mytable_files:
        try:
            obj_response = s3_client.get_object(Bucket=S3_CONFIG['bucket'], Key=file_key)
            content = obj_response['Body'].read().decode('utf-8')
            
            # Try different JSON formats
            records_checked = 0
            
            # Format 1: Array of objects
            if content.strip().startswith('['):
                try:
                    data = json.loads(content)
                    if isinstance(data, list):
                        for record in data:
                            records_checked += 1
                            if isinstance(record, dict):
                                # Check various field name variations
                                record_id = (record.get('id') or record.get('ID') or 
                                            record.get('Id') or record.get('_id'))
                                record_name = (record.get('name') or record.get('NAME') or 
                                             record.get('Name') or record.get('NAME_'))
                                
                                # Also check Debezium format
                                if not record_id and 'after' in record:
                                    after = record['after']
                                    record_id = (after.get('id') or after.get('ID') or 
                                                after.get('Id'))
                                    record_name = (after.get('name') or after.get('NAME') or 
                                                 after.get('Name'))
                                
                                if (record_id and str(record_id) == '333' and 
                                    record_name and str(record_name).upper() == 'KISHOR'):
                                    found = True
                                    print(f"   ✅ FOUND in: {file_key}")
                                    print(f"      Records checked: {records_checked}")
                                    print(f"      Record: {json.dumps(record, indent=6, default=str)}")
                                    break
                except:
                    pass
            
            # Format 2: Newline-delimited JSON
            for line_num, line in enumerate(content.strip().split('\n'), 1):
                if line.strip():
                    try:
                        record = json.loads(line)
                        records_checked += 1
                        if isinstance(record, dict):
                            # Check various field name variations
                            record_id = (record.get('id') or record.get('ID') or 
                                        record.get('Id') or record.get('_id'))
                            record_name = (record.get('name') or record.get('NAME') or 
                                         record.get('Name') or record.get('NAME_'))
                            
                            # Also check Debezium format
                            if not record_id and 'after' in record:
                                after = record['after']
                                record_id = (after.get('id') or after.get('ID') or 
                                            after.get('Id'))
                                record_name = (after.get('name') or after.get('NAME') or 
                                             after.get('Name'))
                            
                            if (record_id and str(record_id) == '333' and 
                                record_name and str(record_name).upper() == 'KISHOR'):
                                found = True
                                print(f"   ✅ FOUND in: {file_key} (line {line_num})")
                                print(f"      Records checked: {records_checked}")
                                print(f"      Record: {json.dumps(record, indent=6, default=str)}")
                                break
                    except:
                        pass
            
            if found:
                break
                
        except Exception as e:
            print(f"   ⚠️  Error reading {file_key}: {e}")
    
    if not found:
        print(f"   ❌ Not found in {len(mytable_files)} MYTABLE file(s)")

# Search in CDC topic files
print("\n2. Searching CDC topic files...\n")
response = s3_client.list_objects_v2(Bucket=S3_CONFIG['bucket'], Prefix="topics/")
topic_files = []

if 'Contents' in response:
    # Filter for AS400-related topics
    topic_files = [obj['Key'] for obj in response['Contents'] 
                   if obj['Key'].endswith('.json') and 'MYTABLE' in obj['Key'].upper()]
    print(f"   Found {len(topic_files)} topic file(s) with MYTABLE\n")
    
    if topic_files:
        found_topic = False
        for file_key in topic_files[:20]:  # Check first 20
            try:
                obj_response = s3_client.get_object(Bucket=S3_CONFIG['bucket'], Key=file_key)
                content = obj_response['Body'].read().decode('utf-8')
                
                # Parse newline-delimited JSON
                for line in content.strip().split('\n'):
                    if line.strip():
                        try:
                            record = json.loads(line)
                            if isinstance(record, dict):
                                # Debezium format: check 'after' field
                                after = record.get('after') or record.get('payload', {}).get('after', {})
                                if after:
                                    record_id = (after.get('id') or after.get('ID') or 
                                                after.get('Id'))
                                    record_name = (after.get('name') or after.get('NAME') or 
                                                 after.get('Name'))
                                    
                                    if (record_id and str(record_id) == '333' and 
                                        record_name and str(record_name).upper() == 'KISHOR'):
                                        found_topic = True
                                        print(f"   ✅ FOUND in topic file: {file_key}")
                                        print(f"      Record: {json.dumps(record, indent=6, default=str)}")
                                        break
                        except:
                            pass
                
                if found_topic:
                    break
                    
            except Exception as e:
                pass
        
        if not found_topic:
            print(f"   ❌ Not found in topic files")

print("\n" + "=" * 70)
if found or (topic_files and found_topic):
    print("✅ Record found in S3!")
else:
    print("⚠️  Record not found. Check:")
    print("   1. Pipeline CDC status (should be RUNNING)")
    print("   2. Kafka topics for AS400-S3_P pipeline")
    print("   3. S3 sink connector status")
    print("   4. Field names might be different (check AS400 table schema)")
print("=" * 70)



