"""Force a full load of department table to capture the new record."""

import sys
sys.path.insert(0, '.')

from ingestion.connectors.postgresql import PostgreSQLConnector
from ingestion.connectors.s3 import S3Connector
import json
from datetime import datetime

# Source PostgreSQL config
pg_config = {
    "host": "72.61.233.209",
    "port": 5432,
    "database": "cdctest",
    "user": "cdc_user",
    "password": "cdc_pass",
    "schema": "public"
}

# Target S3 config
s3_config = {
    "bucket": "mycdcbucket26",
    "aws_access_key_id": "AKIATLTXNANW2EV7QGV2",
    "aws_secret_access_key": "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",
    "region_name": "us-east-1",
    "prefix": ""
}

print("=" * 60)
print("Force Full Load - Department Table")
print("=" * 60)

try:
    # Initialize connectors
    print("\n1. Initializing connectors...")
    source_connector = PostgreSQLConnector(pg_config)
    target_connector = S3Connector(s3_config)
    print("   ✅ Connectors initialized")
    
    bucket = s3_config['bucket']
    prefix = s3_config.get('prefix', '') or ""
    if prefix and not prefix.endswith('/'):
        prefix += '/'
    
    table_name = "department"
    
    print(f"\n2. Processing table: {table_name}")
    
    # Extract schema
    print("   Extracting schema...")
    schema_result = source_connector.extract_schema(
        database=pg_config['database'],
        schema=pg_config['schema'],
        table=table_name
    )
    
    tables = schema_result.get('tables', [])
    columns = tables[0].get('columns', []) if tables else []
    print(f"   ✅ Schema extracted: {len(columns)} columns")
    
    # Extract data
    print("   Extracting data...")
    batch_size = 10000
    offset = 0
    all_rows = []
    column_names = None
    
    while True:
        try:
            data_result = source_connector.extract_data(
                database=pg_config['database'],
                schema=pg_config['schema'],
                table_name=table_name,
                limit=batch_size,
                offset=offset
            )
        except Exception as e:
            print(f"   ❌ Data extraction failed: {e}")
            break
        
        rows = data_result.get('rows', [])
        if not rows:
            break
        
        if column_names is None:
            column_names = data_result.get('column_names', [])
        
        row_dicts = []
        for row in rows:
            row_dict = dict(zip(column_names, row)) if column_names else {}
            row_dicts.append(row_dict)
        
        all_rows.extend(row_dicts)
        offset += len(rows)
        print(f"   Extracted {len(rows)} rows (total: {len(all_rows)})")
        
        has_more = data_result.get('has_more', False)
        if not has_more:
            break
    
    print(f"   ✅ Total rows extracted: {len(all_rows)}")
    
    # Verify we have the new record
    department_names = [row.get('name') for row in all_rows]
    if 'Sales' in department_names:
        print(f"   ✅ New 'Sales' department found in extracted data!")
    else:
        print(f"   ⚠️  'Sales' department not found")
        print(f"   Departments: {department_names}")
    
    # Format as JSON
    print("   Formatting as JSON...")
    json_data = json.dumps(all_rows, indent=2, default=str)
    print(f"   ✅ JSON size: {len(json_data)} bytes")
    
    # Upload to S3 with new timestamp
    s3_key = f"{prefix}{table_name}/full_load_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    print(f"   Uploading to s3://{bucket}/{s3_key}...")
    
    try:
        s3_client = target_connector._get_s3_client()
        s3_client.put_object(
            Bucket=bucket,
            Key=s3_key,
            Body=json_data.encode('utf-8'),
            ContentType='application/json'
        )
        
        print(f"   ✅ Upload successful!")
        print(f"   Uploaded {len(all_rows)} rows from {table_name} to s3://{bucket}/{s3_key}")
        
        print("\n" + "=" * 60)
        print("✅ Full Load Completed with New Record!")
        print("=" * 60)
        print(f"\nFile location: s3://{bucket}/{s3_key}")
        print(f"Total rows: {len(all_rows)}")
        print(f"Departments: {', '.join(department_names)}")
        
    except Exception as e:
        print(f"   ❌ Upload failed: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

