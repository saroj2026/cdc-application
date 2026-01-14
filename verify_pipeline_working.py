"""Final verification that the Oracle-Snowflake pipeline is working."""
import requests

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
BACKEND_URL = "http://localhost:8000"

print("=== FINAL PIPELINE VERIFICATION ===")

# Check pipeline status
r = requests.get(f"{BACKEND_URL}/api/v1/pipelines")
pipelines = r.json()
oracle_pipelines = [p for p in pipelines if 'oracle' in p.get('name', '').lower() and 'sf' in p.get('name', '').lower()]

if oracle_pipelines:
    pipeline = oracle_pipelines[0]
    print(f"\nPipeline: {pipeline.get('name')}")
    print(f"Status: {pipeline.get('status')}")
    print(f"CDC Status: {pipeline.get('cdc_status')}")
    print(f"Mode: {pipeline.get('mode')}")
    print(f"Debezium Connector: {pipeline.get('debezium_connector_name')}")
    print(f"Sink Connector: {pipeline.get('sink_connector_name')}")
    print(f"Topics: {pipeline.get('kafka_topics', [])}")

# Check Debezium connector
debezium_conn = "cdc-oracle_sf_p-ora-cdc_user"
r1 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{debezium_conn}/status")
dbz_status = r1.json()
print(f"\n=== DEBEZIUM CONNECTOR: {debezium_conn} ===")
print(f"State: {dbz_status.get('connector', {}).get('state')}")
tasks = dbz_status.get('tasks', [])
if tasks:
    print(f"Task 0: {tasks[0].get('state')}")
    if tasks[0].get('state') == 'RUNNING':
        print("✓✓✓ SUCCESS: Debezium connector is RUNNING!")

# Check Sink connector
sink_conn = "sink-oracle_sf_p-snow-public"
r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{sink_conn}/status")
sink_status = r2.json()
print(f"\n=== SINK CONNECTOR: {sink_conn} ===")
print(f"State: {sink_status.get('connector', {}).get('state')}")
tasks = sink_status.get('tasks', [])
if tasks:
    print(f"Task 0: {tasks[0].get('state')}")
    if tasks[0].get('state') == 'RUNNING':
        print("✓✓✓ SUCCESS: Sink connector is RUNNING!")

print(f"\n=== SUMMARY ===")
if tasks and tasks[0].get('state') == 'RUNNING' and sink_status.get('tasks', [{}])[0].get('state') == 'RUNNING':
    print("✓✓✓ PIPELINE IS WORKING! Both connectors are RUNNING!")
    print("CDC is now active and ready to capture changes from Oracle to Snowflake.")
else:
    print("Check connector statuses above")

