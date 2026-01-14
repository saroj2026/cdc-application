"""Check the latest department file in S3 for the new record."""

import boto3
import json
from datetime import datetime

S3_CONFIG = {
    "bucket": "mycdcbucket26",
    "aws_access_key_id": "AKIATLTXNANW2EV7QGV2",
    "aws_secret_access_key": "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",
    "region_name": "us-east-1"
}

print("=" * 60)
print("Check Latest Department File in S3")
print("=" * 60)

try:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=S3_CONFIG['aws_access_key_id'],
        aws_secret_access_key=S3_CONFIG['aws_secret_access_key'],
        region_name=S3_CONFIG['region_name']
    )
    
    bucket_name = S3_CONFIG['bucket']
    
    # List all department files
    print("\n1. Listing all department files...")
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix="department/")
    
    if 'Contents' not in response:
        print("   ⚠️  No department files found")
    else:
        files = response['Contents']
        print(f"   ✅ Found {len(files)} department file(s)\n")
        
        # Sort by modification time (newest first)
        files_sorted = sorted(files, key=lambda x: x['LastModified'], reverse=True)
        
        print("2. All department files (newest first):\n")
        for i, file_info in enumerate(files_sorted, 1):
            print(f"   {i}. {file_info['Key']}")
            print(f"      Size: {file_info['Size'] / 1024:.2f} KB")
            print(f"      Modified: {file_info['LastModified']}")
            print()
        
        # Get the latest file
        latest_file = files_sorted[0]
        file_key = latest_file['Key']
        
        print("3. Latest file data:\n")
        print(f"   File: {file_key}")
        print(f"   Modified: {latest_file['LastModified']}\n")
        
        # Download and verify
        obj_response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        data = json.loads(obj_response['Body'].read().decode('utf-8'))
        
        if isinstance(data, list):
            print(f"   ✅ File contains {len(data)} rows\n")
            
            print("4. All records in latest file:\n")
            for i, row in enumerate(data, 1):
                print(f"   Row {i}:")
                for key, value in row.items():
                    print(f"      {key}: {value}")
                print()
            
            # Check for the new Sales department
            department_names = [row.get('name') for row in data]
            if 'Sales' in department_names:
                print("   ✅ New 'Sales' department found in S3!")
            else:
                print("   ⚠️  'Sales' department not found in latest file")
                print(f"   Departments in file: {department_names}")
            
            # Check if we have 5 records
            if len(data) == 5:
                print(f"\n   ✅ All 5 records are present (including the new Sales record)")
            else:
                print(f"\n   ⚠️  Expected 5 records, found {len(data)}")
                
        else:
            print(f"   ⚠️  File format is not a list: {type(data)}")
    
    print("\n" + "=" * 60)
    print("Verification Complete")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

