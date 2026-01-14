"""Search for AS400 topic files in S3."""
import boto3
import json
from datetime import datetime

S3_CONFIG = {
    "bucket": "mycdcbucket26",
    "aws_access_key_id": "AKIATLTXNANW2EV7QGV2",
    "aws_secret_access_key": "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",
    "region_name": "us-east-1"
}

# AS400 topic from pipeline
AS400_TOPIC = "AS400-S3_P.SEGMETRIQ1.MYTABLE"

print("=" * 70)
print(f"Searching for AS400 Topic Files: {AS400_TOPIC}")
print("=" * 70)

s3_client = boto3.client(
    's3',
    aws_access_key_id=S3_CONFIG['aws_access_key_id'],
    aws_secret_access_key=S3_CONFIG['aws_secret_access_key'],
    region_name=S3_CONFIG['region_name']
)

# Search in topics/ prefix for AS400 topic
print(f"\n1. Searching topics/ prefix for AS400 topic...\n")

try:
    # List all objects in topics/
    response = s3_client.list_objects_v2(Bucket=S3_CONFIG['bucket'], Prefix="topics/")
    
    if 'Contents' not in response:
        print("   ⚠️  No files in topics/ prefix")
    else:
        # Filter for AS400 topic files
        as400_files = [obj for obj in response['Contents'] 
                      if AS400_TOPIC.replace('.', '_') in obj['Key'] or 
                         'AS400' in obj['Key'].upper() or
                         'SEGMETRIQ1' in obj['Key']]
        
        if not as400_files:
            print(f"   ⚠️  No files found for topic: {AS400_TOPIC}")
            print(f"\n   All topics found:")
            all_topics = set()
            for obj in response['Contents']:
                # Extract topic name from path
                parts = obj['Key'].split('/')
                if len(parts) >= 2:
                    topic_part = parts[1]
                    all_topics.add(topic_part)
            
            for topic in sorted(all_topics):
                print(f"      - {topic}")
        else:
            print(f"   ✅ Found {len(as400_files)} file(s) for AS400 topic")
            
            # Sort by modification time
            as400_files = sorted(as400_files, key=lambda x: x['LastModified'], reverse=True)
            
            print(f"\n   Most Recent Files:")
            for i, file_obj in enumerate(as400_files[:10], 1):
                age_minutes = (datetime.now(file_obj['LastModified'].tzinfo) - file_obj['LastModified']).total_seconds() / 60
                print(f"   {i}. {file_obj['Key']}")
                print(f"      Modified: {file_obj['LastModified']} ({age_minutes:.1f} minutes ago)")
                print(f"      Size: {file_obj['Size']:,} bytes")
                
                # Search for the record in this file
                try:
                    obj_response = s3_client.get_object(Bucket=S3_CONFIG['bucket'], Key=file_obj['Key'])
                    content = obj_response['Body'].read().decode('utf-8')
                    
                    if '333' in content and 'KISHOR' in content.upper():
                        print(f"      ✅ Contains '333' and 'KISHOR' - checking...")
                        
                        # Parse and find exact record
                        for line in content.strip().split('\n'):
                            if line.strip() and '333' in line and 'KISHOR' in line.upper():
                                try:
                                    record = json.loads(line)
                                    if isinstance(record, dict):
                                        # Check Debezium format
                                        after = record.get('after') or record.get('payload', {}).get('after', {})
                                        if after:
                                            record_id = (after.get('id') or after.get('ID') or after.get('Id'))
                                            record_name = (after.get('name') or after.get('NAME') or after.get('Name'))
                                            
                                            if (str(record_id) == '333' and 
                                                record_name and 'KISHOR' in str(record_name).upper()):
                                                print(f"\n      🎉 FOUND THE RECORD!")
                                                print(f"      Record: {json.dumps(record, indent=8, default=str)}")
                                                break
                                except:
                                    pass
                except:
                    pass
                print()
            
            # Check for very recent files (last 30 minutes)
            recent_cutoff = datetime.now() - timedelta(minutes=30)
            recent_files = [f for f in as400_files 
                          if f['LastModified'].replace(tzinfo=None) > recent_cutoff]
            
            if recent_files:
                print(f"   ✅ Found {len(recent_files)} file(s) modified in last 30 minutes!")
                print(f"   Data IS being written to S3!")
            else:
                print(f"   ⚠️  No files modified in last 30 minutes")
                if as400_files:
                    oldest = as400_files[0]['LastModified']
                    age_minutes = (datetime.now(oldest.tzinfo) - oldest).total_seconds() / 60
                    print(f"   Most recent file is {age_minutes:.1f} minutes old")

except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*70}")
print("Note: If flush.size was updated to 1, new records should appear")
print("within seconds. If no recent files, the connector may need a restart.")
print(f"{'='*70}")



