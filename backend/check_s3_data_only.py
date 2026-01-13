"""Check S3 bucket for recent data writes - no Kafka Connect needed."""
import boto3
import json
from datetime import datetime, timedelta

S3_CONFIG = {
    "bucket": "mycdcbucket26",
    "aws_access_key_id": "AKIATLTXNANW2EV7QGV2",
    "aws_secret_access_key": "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",
    "region_name": "us-east-1"
}

print("=" * 70)
print("Checking S3 Bucket for Recent Data Writes")
print("=" * 70)

s3_client = boto3.client(
    's3',
    aws_access_key_id=S3_CONFIG['aws_access_key_id'],
    aws_secret_access_key=S3_CONFIG['aws_secret_access_key'],
    region_name=S3_CONFIG['region_name']
)

# Check all prefixes that might contain data
prefixes_to_check = ["MYTABLE/", "dbo/", "topics/"]

for prefix in prefixes_to_check:
    print(f"\n{'='*70}")
    print(f"Checking prefix: {prefix}")
    print(f"{'='*70}\n")
    
    try:
        response = s3_client.list_objects_v2(Bucket=S3_CONFIG['bucket'], Prefix=prefix)
        
        if 'Contents' not in response:
            print(f"   ⚠️  No files found in {prefix}")
            continue
        
        files = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)
        print(f"   ✅ Found {len(files)} file(s)")
        
        # Show 10 most recent files
        print(f"\n   Most Recent Files (last 10):")
        recent_cutoff = datetime.now() - timedelta(minutes=10)
        recent_count = 0
        
        for i, obj in enumerate(files[:10], 1):
            file_time = obj['LastModified']
            age_seconds = (datetime.now(file_time.tzinfo) - file_time).total_seconds()
            age_minutes = age_seconds / 60
            
            # Check if recent
            is_recent = file_time.replace(tzinfo=None) > recent_cutoff
            if is_recent:
                recent_count += 1
            
            print(f"   {i}. {obj['Key']}")
            print(f"      Modified: {file_time} ({age_minutes:.1f} minutes ago)")
            print(f"      Size: {obj['Size']:,} bytes")
            if is_recent:
                print(f"      ✅ RECENT (within last 10 minutes)")
            print()
        
        if recent_count > 0:
            print(f"   ✅ Found {recent_count} file(s) modified in last 10 minutes!")
            print(f"   Data IS being written to S3!")
        else:
            print(f"   ⚠️  No files modified in last 10 minutes")
            if len(files) > 0:
                oldest_recent = files[0]['LastModified']
                age_minutes = (datetime.now(oldest_recent.tzinfo) - oldest_recent).total_seconds() / 60
                print(f"   Most recent file is {age_minutes:.1f} minutes old")
        
    except Exception as e:
        print(f"   ❌ Error checking {prefix}: {e}")

# Search for the specific record
print(f"\n{'='*70}")
print("Searching for Record: id=333, name=KISHOR")
print(f"{'='*70}\n")

found = False
search_prefixes = ["MYTABLE/", "dbo/", "topics/"]

for prefix in search_prefixes:
    try:
        response = s3_client.list_objects_v2(Bucket=S3_CONFIG['bucket'], Prefix=prefix)
        if 'Contents' not in response:
            continue
        
        # Check most recent 20 files
        files = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)[:20]
        
        for file_obj in files:
            if not file_obj['Key'].endswith('.json'):
                continue
            
            try:
                obj_response = s3_client.get_object(Bucket=S3_CONFIG['bucket'], Key=file_obj['Key'])
                content = obj_response['Body'].read().decode('utf-8')
                
                # Quick check first
                if '333' not in content or 'KISHOR' not in content.upper():
                    continue
                
                # Parse and search
                try:
                    if content.strip().startswith('['):
                        data = json.loads(content)
                        if isinstance(data, list):
                            for record in data:
                                if isinstance(record, dict):
                                    # Check various field name formats
                                    record_id = (record.get('id') or record.get('ID') or 
                                               record.get('Id') or record.get('_id') or
                                               record.get('ID_'))
                                    record_name = (record.get('name') or record.get('NAME') or 
                                                 record.get('Name') or record.get('NAME_'))
                                    
                                    # Also check Debezium format
                                    if not record_id and 'after' in record:
                                        after = record.get('after', {})
                                        record_id = (after.get('id') or after.get('ID') or 
                                                   after.get('Id'))
                                        record_name = (after.get('name') or after.get('NAME') or 
                                                     after.get('Name'))
                                    
                                    if (record_id and str(record_id) == '333' and 
                                        record_name and 'KISHOR' in str(record_name).upper()):
                                        found = True
                                        print(f"   ✅ FOUND in: {file_obj['Key']}")
                                        print(f"      File modified: {file_obj['LastModified']}")
                                        print(f"      Record: {json.dumps(record, indent=6, default=str)}")
                                        break
                    else:
                        # Newline-delimited JSON
                        for line_num, line in enumerate(content.strip().split('\n'), 1):
                            if '333' in line and 'KISHOR' in line.upper():
                                try:
                                    record = json.loads(line)
                                    if isinstance(record, dict):
                                        record_id = (record.get('id') or record.get('ID') or 
                                                   record.get('Id'))
                                        record_name = (record.get('name') or record.get('NAME') or 
                                                     record.get('Name'))
                                        
                                        # Check Debezium format
                                        if not record_id and 'after' in record:
                                            after = record.get('after', {})
                                            record_id = (after.get('id') or after.get('ID'))
                                            record_name = (after.get('name') or after.get('NAME'))
                                        
                                        if (record_id and str(record_id) == '333' and 
                                            record_name and 'KISHOR' in str(record_name).upper()):
                                            found = True
                                            print(f"   ✅ FOUND in: {file_obj['Key']} (line {line_num})")
                                            print(f"      File modified: {file_obj['LastModified']}")
                                            print(f"      Record: {json.dumps(record, indent=6, default=str)}")
                                            break
                                except:
                                    pass
                except json.JSONDecodeError:
                    pass
                
                if found:
                    break
                    
            except Exception as e:
                pass
        
        if found:
            break
            
    except Exception as e:
        print(f"   ⚠️  Error searching in {prefix}: {e}")

if not found:
    print(f"   ⚠️  Record (id=333, name=KISHOR) not found in recent files")
    print(f"   Possible reasons:")
    print(f"      - Data hasn't been written yet (check if flush.size was updated)")
    print(f"      - Data is in older files not checked")
    print(f"      - Field names might be different in AS400")

print(f"\n{'='*70}")
print("Summary:")
print("  - Checked S3 bucket for recent file modifications")
print("  - Searched for your specific record (id=333, name=KISHOR)")
if found:
    print("  ✅ Record found in S3!")
else:
    print("  ⚠️  Record not found - may need to wait or check connector status")
print(f"{'='*70}")

