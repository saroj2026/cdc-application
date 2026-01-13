"""Comprehensive diagnosis of Sink connector issue."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
SINK_CONNECTOR_NAME = "sink-pg_to_mssql_projects_simple-mssql-dbo"

print("="*80)
print("Comprehensive Sink Connector Diagnosis")
print("="*80)

try:
    # Get full connector info
    print("\n1. Full Sink Connector Configuration:")
    response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR_NAME}", timeout=10)
    if response.status_code == 200:
        data = response.json()
        config = data.get('config', {})
        
        # Print all relevant config
        print(json.dumps(config, indent=2))
    
    # Check if there's a way to get connector metrics/offsets
    print("\n2. Checking for connector metrics/offsets...")
    # Try to get connector info endpoint
    try:
        # Some Kafka Connect setups have /connectors/{name}/offsets endpoint
        offsets_url = f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR_NAME}/offsets"
        response = requests.get(offsets_url, timeout=10)
        if response.status_code == 200:
            print("   Offsets:", json.dumps(response.json(), indent=2))
        else:
            print(f"   Offsets endpoint not available (status: {response.status_code})")
    except:
        print("   Offsets endpoint not available")
    
    # Analysis
    print("\n" + "="*80)
    print("Analysis and Potential Fixes")
    print("="*80)
    
    print("\nIssue: Kafka has messages but Sink isn't writing to SQL Server")
    print("\nPossible causes:")
    print("  1. ExtractField transform issue:")
    print("     - The 'after' field might be nested differently")
    print("     - The transform might need to be configured differently")
    print("  2. Date format conversion:")
    print("     - Debezium sends dates as integers (days since epoch)")
    print("     - SQL Server DATE type might not accept this format")
    print("  3. Column name/case mismatch:")
    print("     - Debezium might use different column names")
    print("     - SQL Server is case-sensitive in some contexts")
    print("  4. Message schema mismatch:")
    print("     - The actual Kafka message format might differ from expected")
    
    print("\nRecommended fixes to try:")
    print("  1. Add date conversion transform")
    print("  2. Verify actual Kafka message format")
    print("  3. Check if ExtractField is working (may need Flatten transform first)")
    print("  4. Try using Flatten transform before ExtractField")
    print("  5. Check Sink connector logs for specific error messages")
    
    print("\nSince errors.tolerance=all, errors are being logged but not failing.")
    print("Check Kafka Connect worker logs to see what errors are occurring.")
    
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()

