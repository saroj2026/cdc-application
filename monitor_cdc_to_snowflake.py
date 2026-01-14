#!/usr/bin/env python3
"""Comprehensive monitoring of CDC flow from Kafka to Snowflake."""

import requests
import paramiko
import time
from datetime import datetime

print("=" * 70)
print("CDC FLOW MONITORING: KAFKA → SNOWFLAKE")
print("=" * 70)
print(f"Timestamp: {datetime.now().isoformat()}")
print()

hostname = "72.61.233.209"
kafka_connect_url = "http://72.61.233.209:8083"
kafka_ui_url = "http://72.61.233.209:8080"
sink_connector_name = "sink-oracle_sf_p-snow-public"
topic_name = "oracle_sf_p.CDC_USER.TEST"
consumer_group = "connect-sink-oracle_sf_p-snow-public"

# Get Snowflake connection details
from ingestion.database.models_db import ConnectionModel, PipelineModel
from ingestion.database.session import SessionLocal
from ingestion.connectors.snowflake import SnowflakeConnector

db = SessionLocal()
try:
    pipeline = db.query(PipelineModel).filter(PipelineModel.name == "oracle_sf_p").first()
    if not pipeline:
        print("❌ Pipeline 'oracle_sf_p' not found!")
        exit(1)
    
    snowflake_conn_model = db.query(ConnectionModel).filter(
        ConnectionModel.id == pipeline.target_connection_id
    ).first()
    
    if not snowflake_conn_model:
        print("❌ Snowflake connection not found!")
        exit(1)
finally:
    db.close()

print("1. CHECKING SINK CONNECTOR STATUS")
print("-" * 70)
try:
    r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector_name}/status", timeout=5)
    if r.status_code == 200:
        status = r.json()
        connector_state = status.get('connector', {}).get('state', 'N/A')
        print(f"   Connector State: {connector_state}")
        
        tasks = status.get('tasks', [])
        for task in tasks:
            task_id = task.get('id', 'N/A')
            task_state = task.get('state', 'N/A')
            worker_id = task.get('worker_id', 'N/A')
            print(f"   Task {task_id} State: {task_state} on {worker_id}")
            
            if task_state == 'FAILED':
                trace = task.get('trace', '')
                if trace:
                    print(f"\n   ⚠ Task Error (first 500 chars):")
                    print(f"   {trace[:500]}")
    else:
        print(f"   ❌ Error getting status: {r.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n2. CHECKING KAFKA TOPIC MESSAGE COUNT")
print("-" * 70)
try:
    r = requests.get(f"{kafka_ui_url}/api/clusters/local/topics/{topic_name}", timeout=5)
    if r.status_code == 200:
        topic_info = r.json()
        partitions = topic_info.get('partitions', [])
        if partitions:
            partition = partitions[0]
            offset_max = partition.get('offsetMax', 0)
            offset_min = partition.get('offsetMin', 0)
            message_count = offset_max - offset_min
            
            print(f"   Topic: {topic_name}")
            print(f"   Total Messages: {message_count}")
            print(f"   Offset Range: {offset_min} to {offset_max}")
            print(f"   Latest Offset: {offset_max}")
    else:
        print(f"   ⚠ Could not get topic info: {r.status_code}")
except Exception as e:
    print(f"   ⚠ Error getting topic info: {e}")

print("\n3. CHECKING CONSUMER GROUP OFFSETS")
print("-" * 70)
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username="root", password="segmbp@1100", timeout=10)
    
    # Check consumer group offsets
    offset_cmd = f'docker exec kafka-cdc kafka-consumer-groups --bootstrap-server localhost:9092 --group {consumer_group} --describe 2>&1'
    
    stdin, stdout, stderr = ssh.exec_command(offset_cmd)
    output = stdout.read().decode()
    errors = stderr.read().decode()
    
    if output:
        print("   Consumer Group Offsets:")
        # Parse output to find our topic
        lines = output.split('\n')
        found_topic = False
        for line in lines:
            if topic_name in line or 'TOPIC' in line or 'PARTITION' in line:
                print(f"   {line}")
                found_topic = True
        
        if not found_topic and 'TOPIC' not in output:
            print(f"   ⚠ Consumer group may not have started consuming yet")
            print(f"   Raw output: {output[:200]}")
    else:
        print(f"   ⚠ No output from consumer group command")
        if errors:
            print(f"   Errors: {errors[:200]}")
    
    ssh.close()
except Exception as e:
    print(f"   ⚠ Error checking consumer group: {e}")

print("\n4. CHECKING SINK CONNECTOR LOGS (Recent Activity)")
print("-" * 70)
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username="root", password="segmbp@1100", timeout=10)
    
    log_cmd = """KAFKA_CONNECT=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1); \
docker logs "$KAFKA_CONNECT" 2>&1 | grep -i "sink-oracle_sf_p.*snowflake\\|sink-oracle_sf_p.*buffer\\|sink-oracle_sf_p.*flush\\|sink-oracle_sf_p.*pipe" | tail -10"""
    
    stdin, stdout, stderr = ssh.exec_command(log_cmd)
    output = stdout.read().decode()
    
    if output.strip():
        print("   Recent Sink Connector Activity:")
        for line in output.strip().split('\n'):
            print(f"   {line[:150]}")
    else:
        print("   ⚠ No recent activity logs found")
    
    ssh.close()
except Exception as e:
    print(f"   ⚠ Error checking logs: {e}")

print("\n5. CHECKING SNOWFLAKE FOR CDC EVENTS")
print("-" * 70)
try:
    snowflake_config = {
        'host': snowflake_conn_model.host,
        'port': snowflake_conn_model.port,
        'database': snowflake_conn_model.database,
        'user': snowflake_conn_model.username,
        'password': snowflake_conn_model.password,
    }
    
    if snowflake_conn_model.additional_config:
        if snowflake_conn_model.additional_config.get('account'):
            snowflake_config['account'] = snowflake_conn_model.additional_config['account']
        if snowflake_conn_model.additional_config.get('private_key'):
            snowflake_config['private_key'] = snowflake_conn_model.additional_config['private_key']
        if snowflake_conn_model.additional_config.get('warehouse'):
            snowflake_config['warehouse'] = snowflake_conn_model.additional_config['warehouse']
        if snowflake_conn_model.additional_config.get('role'):
            snowflake_config['role'] = snowflake_conn_model.additional_config['role']
    
    snowflake_schema = snowflake_conn_model.schema or 'public'
    
    sf_conn = SnowflakeConnector(snowflake_config)
    sf_c = sf_conn.connect()
    sf_cur = sf_c.cursor()
    
    sf_cur.execute(f'USE DATABASE {snowflake_config["database"]}')
    sf_cur.execute(f'USE SCHEMA {snowflake_schema}')
    
    # Get total record count
    sf_cur.execute("SELECT COUNT(*) FROM TEST")
    total_count = sf_cur.fetchone()[0]
    print(f"   Total Records in TEST table: {total_count}")
    
    # Get operation counts - check both RECORD_METADATA:operation (for full load) and RECORD_CONTENT:op (for CDC)
    sf_cur.execute("""
        SELECT 
            COALESCE(
                RECORD_METADATA:operation::STRING,
                RECORD_CONTENT:op::STRING,
                'N/A'
            ) as op,
            COUNT(*) as count
        FROM TEST
        GROUP BY COALESCE(
            RECORD_METADATA:operation::STRING,
            RECORD_CONTENT:op::STRING,
            'N/A'
        )
        ORDER BY op
    """)
    op_counts = sf_cur.fetchall()
    
    print("\n   Operation Counts:")
    op_map = {'c': 'CREATE (INSERT)', 'u': 'UPDATE', 'd': 'DELETE', 'r': 'READ (snapshot)'}
    for op_count in op_counts:
        op = op_count[0] or 'N/A'
        count = op_count[1]
        display_name = op_map.get(op, op)
        print(f"     {display_name} ({op}): {count} records")
    
    # Check for CDC events - check both locations
    sf_cur.execute("""
        SELECT COUNT(*) as cdc_count
        FROM TEST
        WHERE COALESCE(
            RECORD_METADATA:operation::STRING,
            RECORD_CONTENT:op::STRING
        ) IN ('c', 'u', 'd')
    """)
    cdc_count = sf_cur.fetchone()[0]
    
    print(f"\n   CDC Events (INSERT/UPDATE/DELETE): {cdc_count}")
    
    if cdc_count > 0:
        print(f"\n   ✅✅✅ CDC EVENTS FOUND IN SNOWFLAKE!")
        print(f"   ✅✅✅ CDC IS WORKING END-TO-END!")
        
        # Get latest CDC events
        sf_cur.execute("""
            SELECT 
                RECORD_CONTENT:ID::INTEGER as id,
                RECORD_CONTENT:NAME::STRING as name,
                RECORD_METADATA:operation::STRING as op,
                RECORD_METADATA:source.ts_ms::NUMBER as ts_ms
            FROM TEST
            WHERE RECORD_METADATA:operation::STRING IN ('c', 'u', 'd')
            ORDER BY RECORD_METADATA:source.ts_ms::NUMBER DESC
            LIMIT 5
        """)
        
        cdc_rows = sf_cur.fetchall()
        if cdc_rows:
            print(f"\n   Latest CDC Events in Snowflake:")
            for i, row in enumerate(cdc_rows, 1):
                op = row[2] if row[2] else 'N/A'
                op_name = op_map.get(op, op)
                print(f"     {i}. ID={row[0]}, NAME={row[1]}, OP={op_name} ({op}), TS={row[3]}")
    else:
        print(f"\n   ⚠ No CDC events in Snowflake yet")
        print(f"   Sink connector may still be processing snapshot messages")
        print(f"   Wait a bit longer and check again")
    
    # Check if sink is processing (compare with Kafka message count)
    print(f"\n   Analysis:")
    print(f"     - Kafka topic has messages (check above)")
    print(f"     - Snowflake has {total_count} total records")
    print(f"     - Snowflake has {cdc_count} CDC events")
    
    if total_count > 0 and cdc_count == 0:
        print(f"     ⚠ Sink is processing snapshot but not CDC messages yet")
    elif cdc_count > 0:
        print(f"     ✅ Sink is processing CDC messages!")
    
    sf_cur.close()
    sf_c.close()
    
except Exception as e:
    print(f"   ❌ Error checking Snowflake: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("MONITORING COMPLETE")
print("=" * 70)
print("\nNext Steps:")
print("  - If CDC events found: ✅ CDC is working end-to-end!")
print("  - If no CDC events: Wait a few minutes and run this script again")
print("  - Check sink connector logs if issues persist")
print("=" * 70)
