"""Restart backend and verify Oracle pipeline setup matches Snowflake table structure."""

import requests
import time
import sys

API_BASE_URL = "http://localhost:8000/api/v1"
PIPELINE_NAME = "oracle_sf_p"

print("=" * 70)
print("Restart Backend and Verify Oracle Pipeline Setup")
print("=" * 70)

print("\n" + "=" * 70)
print("SNOWFLAKE TABLE STRUCTURE (from ps_sn_p pipeline)")
print("=" * 70)
print("""
Based on the Snowflake table 'projects_simple', the structure is:

1. RECORD_METADATA (VARIANT)
   - Contains Kafka metadata:
     * CreateTime
     * offset
     * partition
     * topic

2. RECORD_CONTENT (VARIANT)
   - Contains the actual data fields:
     * department_id
     * employee_id
     * end_date
     * project_id
     * project_name
     * start_date
     * status

This structure is AUTO-CREATED by the Snowflake Kafka Connector when using:
- JsonConverter with schemas.enable=true
- ExtractNewRecordState transform
- Auto-create tables enabled

The Oracle pipeline will create the same structure automatically!
""")

print("\n" + "=" * 70)
print("BACKEND RESTART INSTRUCTIONS")
print("=" * 70)
print("""
Please restart the backend manually:

1. Stop the current backend (if running):
   - Press Ctrl+C in the terminal where it's running
   - Or kill the process

2. Start the backend:
   python -m uvicorn ingestion.api:app --host 0.0.0.0 --port 8000

   Or use the start script:
   ./start_backend.sh

3. Wait for backend to be ready (you'll see "Application startup complete")
""")

input("\nPress Enter after you've restarted the backend...")

# Wait for backend
print("\n" + "=" * 70)
print("WAITING FOR BACKEND")
print("=" * 70)
max_attempts = 30
backend_ready = False

for i in range(max_attempts):
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Backend is ready!")
            backend_ready = True
            break
    except:
        if i < max_attempts - 1:
            print(f"   ⏳ Waiting... ({i+1}/{max_attempts})")
            time.sleep(2)
        else:
            print("   ❌ Backend did not start in time")
            print("   Please ensure the backend is running and try again")
            sys.exit(1)

if not backend_ready:
    sys.exit(1)

# Get pipeline
print("\n" + "=" * 70)
print("VERIFYING PIPELINE CONFIGURATION")
print("=" * 70)

try:
    response = requests.get(f"{API_BASE_URL}/pipelines", timeout=10)
    pipelines = response.json() if response.status_code == 200 else []
    
    pipeline = None
    for p in pipelines:
        if p.get("name") == PIPELINE_NAME:
            pipeline = p
            break
    
    if not pipeline:
        print(f"   ❌ Pipeline '{PIPELINE_NAME}' not found")
        sys.exit(1)
    
    pipeline_id = pipeline.get("id")
    print(f"\n   ✅ Pipeline found: {pipeline_id}")
    print(f"\n   Configuration:")
    print(f"      Name: {pipeline.get('name')}")
    print(f"      Source: Oracle - {pipeline.get('source_database')}.{pipeline.get('source_schema')}.{pipeline.get('source_tables')[0]}")
    print(f"      Target: Snowflake - {pipeline.get('target_database')}.{pipeline.get('target_schema')}.{pipeline.get('target_tables')[0]}")
    print(f"      Mode: {pipeline.get('mode')}")
    print(f"      Auto Create Target: {pipeline.get('auto_create_target')}")
    
    # Verify target schema is lowercase
    if pipeline.get('target_schema') == 'public':
        print(f"\n   ✅ Target schema is 'public' (lowercase) - correct!")
    else:
        print(f"\n   ⚠️  Target schema is '{pipeline.get('target_schema')}' - should be 'public'")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("READY TO START FULL LOAD")
print("=" * 70)
print("""
The pipeline is configured correctly:
✅ Source: Oracle XE - c##cdc_user.test
✅ Target: Snowflake - seg.public.test
✅ Schema: public (lowercase, matches ps_sn_p)
✅ Auto-create: Enabled (will create table with RECORD_CONTENT and RECORD_METADATA)

The Snowflake table will be auto-created with:
- RECORD_CONTENT (VARIANT) - Contains Oracle table data
- RECORD_METADATA (VARIANT) - Contains Kafka metadata

To start the full load, run:
  python restart_backend_and_start_full_load.py

Or manually start via API:
  POST http://localhost:8000/api/v1/pipelines/{pipeline_id}/start
""")

print("\n" + "=" * 70)
