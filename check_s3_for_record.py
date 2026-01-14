"""Check S3 for the AS400 record (id=333, name=KISHOR)."""
import boto3
import json
from datetime import datetime, timedelta

S3_CONFIG = {
    "bucket": "mycdcbucket26",
    "aws_access_key_id": "AKIATLTXNANW2EV7QGV2",
    "aws_secret_access_key": "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",
    "region_name": "us-east-1"
}

AS400_TOPIC = "AS400-S3_P.SEGMETRIQ1.MYTABLE"

print("=" * 70)
print("Checking S3 for Record: id=333, name=KISHOR")
print("=" * 70)

s3_client = boto3.client(
    's3',
    aws_access_key_id=S3_CONFIG['aws_access_key_id'],
    aws_secret_access_key=S3_CONFIG['aws_secret_access_key'],
    region_name=S3_CONFIG['region_name']
)

# Search in topics/ prefix for AS400 topic
print(f"\n1. Searching for AS400 topic files...\n")

try:
    # List all objects in topics/
    response = s3_client.list_objects_v2(Bucket=S3_CONFIG['bucket'], Prefix="topics/")
    
    if 'Contents' not in response:
        print("   ⚠️  No files in topics/ prefix")
    else:
        # Filter for AS400 topic files
        as400_files = []
        for obj in response['Contents']:
            key = obj['Key']
            if 'AS400-S3_P' in key or 'SEGMETRIQ1' in key or 'MYTABLE' in key.upper():
                as400_files.append(obj)
        
        if not as400_files:
            print(f"   ⚠️  No files found for AS400 topic")
            print(f"   Checking all topics found:")
            all_topics = set()
            for obj in response['Contents'][:20]:  # Check first 20
                parts = obj['Key'].split('/')
                if len(parts) >= 2:
                    all_topics.add(parts[1])
            for topic in sorted(all_topics):
                print(f"      - {topic}")
        else:
            print(f"   ✅ Found {len(as400_files)} AS400 topic file(s)")
            
            # Sort by modification time (newest first)
            as400_files = sorted(as400_files, key=lambda x: x['LastModified'], reverse=True)
            
            # Check for recent files
            recent_cutoff = datetime.now() - timedelta(minutes=30)
            recent_files = [f for f in as400_files 
                          if f['LastModified'].replace(tzinfo=None) > recent_cutoff]
            
            if recent_files:
                print(f"   ✅ Found {len(recent_files)} file(s) modified in last 30 minutes!")
                print(f"   Data IS being written to S3!\n")
            else:
                print(f"   ⚠️  No files modified in last 30 minutes")
                if as400_files:
                    oldest = as400_files[0]['LastModified']
                    age_minutes = (datetime.now(oldest.tzinfo) - oldest).total_seconds() / 60
                    print(f"   Most recent file is {age_minutes:.1f} minutes old\n")
            
            # Search for the record in recent files
            print(f"2. Searching for record (id=333, name=KISHOR)...\n")
            
            found = False
            files_to_check = recent_files[:20] if recent_files else as400_files[:10]
            
            for file_obj in files_to_check:
                file_key = file_obj['Key']
                if not file_key.endswith('.json'):
                    continue
                
                try:
                    obj_response = s3_client.get_object(Bucket=S3_CONFIG['bucket'], Key=file_key)
                    content = obj_response['Body'].read().decode('utf-8')
                    
                    # Quick check first
                    if '333' not in content or 'KISHOR' not in content.upper():
                        continue
                    
                    # Parse and search
                    for line in content.strip().split('\n'):
                        if line.strip() and '333' in line and 'KISHOR' in line.upper():
                            try:
                                record = json.loads(line)
                                if isinstance(record, dict):
                                    # Check Debezium format
                                    after = record.get('after') or record.get('payload', {}).get('after', {})
                                    if after:
                                        record_id = (after.get('id') or after.get('ID') or 
                                                   after.get('Id'))
                                        record_name = (after.get('name') or after.get('NAME') or 
                                                     after.get('Name'))
                                        
                                        if (record_id and str(record_id) == '333' and 
                                            record_name and 'KISHOR' in str(record_name).upper()):
                                            found = True
                                            print(f"   ✅ FOUND in: {file_key}")
                                            print(f"      File modified: {file_obj['LastModified']}")
                                            print(f"      Record: {json.dumps(record, indent=6, default=str)}")
                                            break
                            except:
                                pass
                    
                    if found:
                        break
                        
                except Exception as e:
                    pass
            
            if not found:
                print(f"   ⚠️  Record not found in checked files")
                print(f"   Possible reasons:")
                print(f"      - Data hasn't been written yet (wait a few more minutes)")
                print(f"      - Record is in a file not yet checked")
                print(f"      - Field names might be different in AS400")
            
            # Show recent files
            print(f"\n3. Recent AS400 Files:\n")
            for i, file_obj in enumerate(as400_files[:5], 1):
                age_minutes = (datetime.now(file_obj['LastModified'].tzinfo) - file_obj['LastModified']).total_seconds() / 60
                print(f"   {i}. {file_obj['Key']}")
                print(f"      Modified: {age_minutes:.1f} minutes ago")
                print(f"      Size: {file_obj['Size']:,} bytes")
                print()
        
except Exception as e:
    print(f"   ❌ Error checking S3: {e}")
    import traceback
    traceback.print_exc()

print("=" * 70)
if found:
    print("✅ SUCCESS! Record found in S3!")
else:
    print("⚠️  Record not found yet - may need to wait a bit longer")
    print("   The connector is RUNNING, so data should appear soon.")
print("=" * 70)



