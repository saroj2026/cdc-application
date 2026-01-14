"""Verify connector status after granting Oracle permissions."""
import requests
import time

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
BACKEND_URL = "http://localhost:8000"
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-cdc_user"

print("=== VERIFYING CONNECTOR AFTER PERMISSIONS GRANTED ===")
print("")

# Wait a bit for connector to restart
print("Waiting 5 seconds for connector to initialize...")
time.sleep(5)

# Check connector status
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
status = r.json()

connector_state = status.get('connector', {}).get('state')
tasks = status.get('tasks', [])

print(f"Connector state: {connector_state}")
print(f"Number of tasks: {len(tasks)}")
print("")

if tasks:
    task = tasks[0]
    task_state = task.get('state')
    task_id = task.get('id')
    
    print(f"Task {task_id} state: {task_state}")
    
    if task_state == 'RUNNING':
        print("✓✓✓ SUCCESS: Connector task is RUNNING!")
        print("The connector can now perform snapshots and start CDC!")
    elif task_state == 'FAILED':
        error = task.get('trace', 'Unknown error')
        print(f"\n⚠ Task is FAILED")
        print(f"Error: {error[:600]}")
        print("")
        if "ORA-01031" in error or "insufficient privileges" in error:
            print("⚠ Still getting privilege error - permissions might not be applied yet")
            print("Try restarting the connector again")
        else:
            print("Different error - check the error message above")
    else:
        print(f"Task state: {task_state} (may be starting)")

# Check topics
print("\n=== CHECKING KAFKA TOPICS ===")
try:
    r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/topics")
    if r2.status_code == 200:
        topics_data = r2.json()
        topics = topics_data.get('topics', {}).get(CONNECTOR_NAME, [])
        if topics:
            print(f"Topics: {topics}")
            if 'oracle_sf_p.cdc_user.test' in topics or any('cdc_user.test' in t for t in topics):
                print("✓ Topic is assigned to connector!")
            else:
                print("⚠ Topic not yet assigned (may be created soon)")
        else:
            print("No topics yet (connector may still be starting)")
except:
    print("Cannot query topics (API may not be available)")

# Check pipeline status
print("\n=== PIPELINE STATUS ===")
r3 = requests.get(f"{BACKEND_URL}/api/v1/pipelines")
pipelines = r3.json()
oracle_pipelines = [p for p in pipelines if 'oracle' in p.get('name', '').lower() and 'sf' in p.get('name', '').lower()]
if oracle_pipelines:
    pipeline = oracle_pipelines[0]
    print(f"Pipeline: {pipeline.get('name')}")
    print(f"Status: {pipeline.get('status')}")
    print(f"CDC Status: {pipeline.get('cdc_status')}")

print("\n=== SUMMARY ===")
if tasks and tasks[0].get('state') == 'RUNNING':
    print("✓✓✓ SUCCESS: All permissions granted and connector is RUNNING!")
    print("The topic should be created automatically now.")
    print("CDC is ready to capture changes from Oracle to Snowflake!")
else:
    print("Permissions granted, but connector needs to be restarted or is still starting.")
    print("If connector is FAILED, restart the pipeline to apply the new permissions.")

