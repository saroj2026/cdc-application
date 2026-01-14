"""Check pipeline from database and start it."""

import psycopg2
import requests
import json
import sys
import time

# Database connection
DB_URL = "postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest"
PIPELINE_ID = "ae7bb432-2fa8-48eb-90a0-d6bb4c164441"
API_BASE = "http://localhost:8000/api/v1"

print("=" * 70)
print("Checking Pipeline from Database and Starting")
print("=" * 70)

try:
    # Step 1: Check pipeline from database
    print("\n1. Checking pipeline from database...")
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, name, status, cdc_status, full_load_status, mode,
               debezium_connector_name, sink_connector_name, kafka_topics
        FROM pipelines
        WHERE id = %s AND deleted_at IS NULL
    """, (PIPELINE_ID,))
    
    row = cur.fetchone()
    if not row:
        print(f"   ❌ Pipeline not found in database")
        sys.exit(1)
    
    pipeline_id, name, status, cdc_status, full_load_status, mode, dbz_name, sink_name, kafka_topics = row
    print(f"   ✅ Found pipeline: {name}")
    print(f"      Status: {status}")
    print(f"      CDC Status: {cdc_status}")
    print(f"      Full Load Status: {full_load_status}")
    print(f"      Mode: {mode}")
    print(f"      Debezium Connector: {dbz_name or 'None'}")
    print(f"      Sink Connector: {sink_name or 'None'}")
    print(f"      Kafka Topics: {kafka_topics or []}")
    
    cur.close()
    conn.close()
    
    # Step 2: Start pipeline if not running
    print(f"\n2. Pipeline Status Analysis:")
    if status == 'RUNNING' and cdc_status == 'RUNNING':
        print("   ✅ Pipeline and CDC are already RUNNING!")
        print("   CDC should be working.")
    elif status == 'STARTING' or cdc_status == 'STARTING':
        print("   ⚠️  Pipeline is in STARTING state")
        print("   This might indicate:")
        print("      - Connectors are being created")
        print("      - Pipeline is stuck (Kafka Connect unreachable)")
        print("   Attempting to restart...")
    else:
        print(f"   Pipeline is {status}, CDC is {cdc_status}")
        print("   Starting pipeline...")
    
    # Step 3: Start pipeline
    print(f"\n3. Starting/Restarting pipeline...")
    try:
        start_response = requests.post(
            f"{API_BASE}/pipelines/{PIPELINE_ID}/start",
            timeout=180
        )
        
        if start_response.status_code == 200:
            result = start_response.json()
            print("   ✅ Pipeline start requested!")
            print(f"   Response: {json.dumps(result, indent=6)}")
        else:
            error_detail = start_response.text
            print(f"   ⚠️  Start request returned: {start_response.status_code}")
            print(f"   Response: {error_detail[:500]}")
    except requests.exceptions.Timeout:
        print("   ⚠️  Start request timed out (may still be processing)")
    except Exception as e:
        print(f"   ⚠️  Error starting pipeline: {e}")
    
    # Step 4: Wait and check database again
    print(f"\n4. Waiting 10 seconds and checking database again...")
    time.sleep(10)
    
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT status, cdc_status, full_load_status,
               debezium_connector_name, sink_connector_name, updated_at
        FROM pipelines
        WHERE id = %s AND deleted_at IS NULL
    """, (PIPELINE_ID,))
    
    row = cur.fetchone()
    if row:
        status, cdc_status, full_load_status, dbz_name, sink_name, updated_at = row
        print(f"   Updated Status:")
        print(f"      Pipeline: {status}")
        print(f"      CDC: {cdc_status}")
        print(f"      Full Load: {full_load_status}")
        print(f"      Debezium Connector: {dbz_name or 'None'}")
        print(f"      Sink Connector: {sink_name or 'None'}")
        print(f"      Last Updated: {updated_at}")
    
    cur.close()
    conn.close()
    
    # Step 5: Check Kafka Connect directly (if accessible)
    print(f"\n5. Checking Kafka Connect status...")
    try:
        kafka_response = requests.get("http://72.61.233.209:8083/connectors", timeout=5)
        if kafka_response.status_code == 200:
            connectors = kafka_response.json()
            print(f"   ✅ Kafka Connect is accessible")
            print(f"   Found {len(connectors)} connector(s)")
            
            # Check for our connectors
            if dbz_name and dbz_name in connectors:
                print(f"   ✅ Debezium connector '{dbz_name}' exists")
            if sink_name and sink_name in connectors:
                print(f"   ✅ Sink connector '{sink_name}' exists")
        else:
            print(f"   ⚠️  Kafka Connect returned: {kafka_response.status_code}")
    except requests.exceptions.Timeout:
        print("   ⚠️  Kafka Connect is unreachable (timeout)")
        print("   This is why connectors may not be created")
    except requests.exceptions.ConnectionError:
        print("   ⚠️  Kafka Connect is unreachable (connection refused)")
        print("   This is why connectors may not be created")
    except Exception as e:
        print(f"   ⚠️  Error checking Kafka Connect: {e}")
    
    # Summary
    print(f"\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    
    if status == 'RUNNING' and cdc_status == 'RUNNING' and dbz_name and sink_name:
        print("✅ CDC SHOULD BE WORKING!")
        print(f"   - Pipeline: {status}")
        print(f"   - CDC: {cdc_status}")
        print(f"   - Connectors are created")
        print(f"\n   To verify CDC is actually working:")
        print(f"   1. Make a change in the source table (projects_simple)")
        print(f"   2. Check if it appears in Snowflake target table")
        print(f"   3. Check replication events in the monitoring page")
    else:
        print("⚠️  CDC Status:")
        print(f"   - Pipeline: {status}")
        print(f"   - CDC: {cdc_status}")
        if not dbz_name or not sink_name:
            print(f"   - Connectors not yet created")
            print(f"\n   Issue: Kafka Connect is unreachable")
            print(f"   Solution: Ensure Kafka Connect is running on 72.61.233.209:8083")
        else:
            print(f"   - Debezium: {dbz_name}")
            print(f"   - Sink: {sink_name}")
    
    print(f"\n" + "=" * 70)
    
except psycopg2.Error as e:
    print(f"❌ Database error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


