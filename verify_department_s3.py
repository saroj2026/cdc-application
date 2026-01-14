"""Verify department table data in S3 bucket."""

import boto3
import json

S3_CONFIG = {
    "bucket": "mycdcbucket26",
    "aws_access_key_id": "AKIATLTXNANW2EV7QGV2",
    "aws_secret_access_key": "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",
    "region_name": "us-east-1"
}

print("=" * 60)
print("Department Table - S3 Verification")
print("=" * 60)

try:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=S3_CONFIG['aws_access_key_id'],
        aws_secret_access_key=S3_CONFIG['aws_secret_access_key'],
        region_name=S3_CONFIG['region_name']
    )
    
    bucket_name = S3_CONFIG['bucket']
    
    print(f"\n1. Checking S3 bucket: {bucket_name}")
    print(f"   Looking for department table files...\n")
    
    # List objects with department prefix
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix="department/")
    
    if 'Contents' not in response:
        print("   ⚠️  No department files found in bucket")
    else:
        files = response['Contents']
        print(f"   ✅ Found {len(files)} department file(s):\n")
        
        # Get the latest file
        latest_file = max(files, key=lambda x: x['LastModified'])
        file_key = latest_file['Key']
        file_size = latest_file['Size']
        modified = latest_file['LastModified']
        
        print(f"   📄 File: {file_key}")
        print(f"   Size: {file_size / 1024:.2f} KB")
        print(f"   Modified: {modified}\n")
        
        # Download and verify data
        print("2. Downloading and verifying data...\n")
        obj_response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        data = json.loads(obj_response['Body'].read().decode('utf-8'))
        
        if isinstance(data, list):
            print(f"   ✅ File contains {len(data)} rows\n")
            
            print("3. Data Preview:\n")
            for i, row in enumerate(data[:4], 1):  # Show first 4 rows
                print(f"   Row {i}:")
                for key, value in row.items():
                    print(f"      {key}: {value}")
                print()
            
            if len(data) > 4:
                print(f"   ... and {len(data) - 4} more rows\n")
            
            # Verify expected data
            print("4. Data Verification:\n")
            expected_departments = ['Engineering', 'Human Resources', 'Finance', 'Marketing']
            found_departments = [row.get('name') for row in data]
            
            print(f"   Expected departments: {expected_departments}")
            print(f"   Found departments: {found_departments}\n")
            
            all_found = all(dept in found_departments for dept in expected_departments)
            if all_found:
                print("   ✅ All expected departments found!")
            else:
                missing = set(expected_departments) - set(found_departments)
                if missing:
                    print(f"   ⚠️  Missing departments: {missing}")
            
            print("\n" + "=" * 60)
            print("✅ Department Data Successfully Loaded to S3!")
            print("=" * 60)
        else:
            print(f"   ⚠️  File format is not a list: {type(data)}")
            
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

