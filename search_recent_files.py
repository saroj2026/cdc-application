"""Search recent AS400 files for the record."""
import boto3
import json

S3_CONFIG = {
    "bucket": "mycdcbucket26",
    "aws_access_key_id": "AKIATLTXNANW2EV7QGV2",
    "aws_secret_access_key": "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",
    "region_name": "us-east-1"
}

print("=" * 70)
print("Searching Recent AS400 Files for Record: id=333, name=KISHOR")
print("=" * 70)

s3_client = boto3.client(
    's3',
    aws_access_key_id=S3_CONFIG['aws_access_key_id'],
    aws_secret_access_key=S3_CONFIG['aws_secret_access_key'],
    region_name=S3_CONFIG['region_name']
)

# Get all AS400 topic files
response = s3_client.list_objects_v2(Bucket=S3_CONFIG['bucket'], Prefix="topics/AS400-S3_P.SEGMETRIQ1.MYTABLE/")

if 'Contents' not in response:
    print("❌ No AS400 topic files found")
    exit(1)

# Sort by modification time (newest first)
files = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)

print(f"\nFound {len(files)} AS400 topic files")
print(f"Checking the 30 most recent files...\n")

found = False
checked = 0

for file_obj in files[:30]:
    file_key = file_obj['Key']
    if not file_key.endswith('.json'):
        continue
    
    checked += 1
    try:
        obj_response = s3_client.get_object(Bucket=S3_CONFIG['bucket'], Key=file_key)
        content = obj_response['Body'].read().decode('utf-8')
        
        # Parse each line (newline-delimited JSON)
        for line_num, line in enumerate(content.strip().split('\n'), 1):
            if not line.strip():
                continue
            
            try:
                record = json.loads(line)
                
                # Check Debezium format
                after = record.get('after') or record.get('payload', {}).get('after', {})
                if not after:
                    after = record  # Might be direct format
                
                # Check all possible field name variations
                record_id = (after.get('id') or after.get('ID') or after.get('Id') or 
                           after.get('_id') or after.get('ID_'))
                record_name = (after.get('name') or after.get('NAME') or 
                             after.get('Name') or after.get('NAME_'))
                
                # Also check if values are in the entire record
                record_str = json.dumps(record).upper()
                if '333' in record_str and 'KISHOR' in record_str:
                    # Found potential match
                    if (record_id and str(record_id) == '333') or '333' in str(record):
                        if (record_name and 'KISHOR' in str(record_name).upper()) or 'KISHOR' in record_str:
                            found = True
                            print(f"✅ FOUND in: {file_key}")
                            print(f"   Line: {line_num}")
                            print(f"   File modified: {file_obj['LastModified']}")
                            print(f"   Full record:")
                            print(f"   {json.dumps(record, indent=4, default=str)}")
                            break
            except json.JSONDecodeError:
                pass
        
        if found:
            break
            
    except Exception as e:
        pass

if not found:
    print(f"⚠️  Record not found in {checked} most recent files")
    print(f"\nLet's check the actual data format...")
    
    # Check first file to see format
    if files:
        first_file = files[0]
        try:
            obj_response = s3_client.get_object(Bucket=S3_CONFIG['bucket'], Key=first_file['Key'])
            content = obj_response['Body'].read().decode('utf-8')
            lines = [l for l in content.strip().split('\n') if l.strip()]
            if lines:
                print(f"\nSample record from most recent file ({first_file['Key']}):")
                try:
                    sample = json.loads(lines[0])
                    print(f"{json.dumps(sample, indent=4, default=str)}")
                except:
                    print(f"{lines[0][:500]}")
        except:
            pass

print("\n" + "=" * 70)



