#!/usr/bin/env python3
"""Fix aws_s3 database_type to s3 for AS400-S3_P pipeline target connection"""
import requests
import sys

API_BASE_URL = "http://localhost:8000"

def main():
    print("="*70)
    print("FIXING AWS_S3 DATABASE TYPE")
    print("="*70 + "\n")
    
    # Get pipeline
    print("1. Finding AS400-S3_P pipeline...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/pipelines")
        response.raise_for_status()
        pipelines = response.json()
        
        pipeline = next((p for p in pipelines if p.get("name") == "AS400-S3_P"), None)
        if not pipeline:
            print("❌ Pipeline not found")
            return 1
        
        pipeline_id = pipeline.get("id")
        target_conn_id = pipeline.get("target_connection_id")
        source_conn_id = pipeline.get("source_connection_id")
        
        print(f"   ✅ Found pipeline: {pipeline_id}")
        print(f"   Target Connection ID: {target_conn_id}")
        print(f"   Source Connection ID: {source_conn_id}")
        
    except Exception as e:
        print(f"❌ Error getting pipeline: {e}")
        return 1
    
    if not target_conn_id:
        print("❌ Target connection ID is None")
        return 1
    
    # Get target connection
    print(f"\n2. Getting target connection {target_conn_id}...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/connections/{target_conn_id}")
        response.raise_for_status()
        target_conn = response.json()
        
        print(f"   Name: {target_conn.get('name')}")
        print(f"   Current database_type: {target_conn.get('database_type')}")
        
        if target_conn.get('database_type') == 's3':
            print("   ✅ Already using 's3', no fix needed")
            return 0
        
        if target_conn.get('database_type') not in ['aws_s3', 's3']:
            print(f"   ⚠️  Unexpected database_type: {target_conn.get('database_type')}")
            return 1
        
    except Exception as e:
        print(f"❌ Error getting connection: {e}")
        return 1
    
    # Update connection
    print(f"\n3. Updating connection database_type from 'aws_s3' to 's3'...")
    try:
        update_data = {
            "name": target_conn.get('name'),
            "connection_type": target_conn.get('connection_type'),
            "database_type": "s3",  # Fix: change from aws_s3 to s3
            "host": target_conn.get('host'),
            "port": target_conn.get('port'),
            "database": target_conn.get('database'),
            "username": target_conn.get('username'),
            "password": target_conn.get('password'),
            "schema": target_conn.get('schema'),
            "additional_config": target_conn.get('additional_config', {})
        }
        
        response = requests.put(
            f"{API_BASE_URL}/api/v1/connections/{target_conn_id}",
            json=update_data
        )
        
        if response.status_code == 200:
            print("   ✅ Connection updated successfully")
            updated = response.json()
            print(f"   New database_type: {updated.get('database_type')}")
        else:
            print(f"   ❌ Update failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return 1
            
    except Exception as e:
        print(f"❌ Error updating connection: {e}")
        return 1
    
    print("\n" + "="*70)
    print("✅ FIX COMPLETE")
    print("="*70)
    print("\nYou can now try starting the pipeline again:")
    print("  python3 start_as400_pipeline.py")
    print("="*70 + "\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

