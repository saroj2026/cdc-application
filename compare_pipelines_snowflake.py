#!/usr/bin/env python3
"""Compare ps_sn_p and oracle_sf_p pipelines to see how Snowflake CDC is configured."""

import requests
import json

print("=" * 70)
print("COMPARING PIPELINES: ps_sn_p vs oracle_sf_p")
print("=" * 70)

kafka_connect_url = "http://72.61.233.209:8083"

# Get sink connectors for both pipelines
ps_sn_p_sink = "sink-ps_sn_p-snow-public"
oracle_sf_p_sink = "sink-oracle_sf_p-snow-public"

print("\n1. CHECKING ps_sn_p SINK CONNECTOR")
print("-" * 70)

try:
    r = requests.get(f"{kafka_connect_url}/connectors/{ps_sn_p_sink}/config", timeout=5)
    if r.status_code == 200:
        ps_config = r.json()
        print(f"   ✅ Connector exists: {ps_sn_p_sink}")
        print(f"   Topics: {ps_config.get('topics', 'N/A')}")
        print(f"   Topic2Table map: {ps_config.get('snowflake.topic2table.map', 'N/A')}")
        print(f"   Transforms: {ps_config.get('transforms', 'N/A')}")
        if ps_config.get('transforms'):
            print(f"   Transform details:")
            for key, value in ps_config.items():
                if key.startswith('transforms.'):
                    print(f"     {key}: {value}")
    else:
        print(f"   ⚠ Connector not found: {r.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n2. CHECKING oracle_sf_p SINK CONNECTOR")
print("-" * 70)

try:
    r = requests.get(f"{kafka_connect_url}/connectors/{oracle_sf_p_sink}/config", timeout=5)
    if r.status_code == 200:
        oracle_config = r.json()
        print(f"   ✅ Connector exists: {oracle_sf_p_sink}")
        print(f"   Topics: {oracle_config.get('topics', 'N/A')}")
        print(f"   Topic2Table map: {oracle_config.get('snowflake.topic2table.map', 'N/A')}")
        print(f"   Transforms: {oracle_config.get('transforms', 'N/A')}")
        if oracle_config.get('transforms'):
            print(f"   Transform details:")
            for key, value in oracle_config.items():
                if key.startswith('transforms.'):
                    print(f"     {key}: {value}")
    else:
        print(f"   ⚠ Connector not found: {r.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n3. COMPARING CONFIGURATIONS")
print("-" * 70)

try:
    ps_r = requests.get(f"{kafka_connect_url}/connectors/{ps_sn_p_sink}/config", timeout=5)
    oracle_r = requests.get(f"{kafka_connect_url}/connectors/{oracle_sf_p_sink}/config", timeout=5)
    
    if ps_r.status_code == 200 and oracle_r.status_code == 200:
        ps_config = ps_r.json()
        oracle_config = oracle_r.json()
        
        # Compare key settings
        print("   Key Differences:")
        
        ps_transforms = ps_config.get('transforms', 'N/A')
        oracle_transforms = oracle_config.get('transforms', 'N/A')
        
        if ps_transforms != oracle_transforms:
            print(f"     ⚠ Transforms differ:")
            print(f"       ps_sn_p: {ps_transforms}")
            print(f"       oracle_sf_p: {oracle_transforms}")
        else:
            print(f"     ✅ Transforms match: {ps_transforms}")
        
        ps_topic_map = ps_config.get('snowflake.topic2table.map', 'N/A')
        oracle_topic_map = oracle_config.get('snowflake.topic2table.map', 'N/A')
        
        print(f"\n     ps_sn_p topic2table.map: {ps_topic_map}")
        print(f"     oracle_sf_p topic2table.map: {oracle_topic_map}")
        
        # Check buffer settings
        ps_buffer_count = ps_config.get('buffer.count.records', 'N/A')
        oracle_buffer_count = oracle_config.get('buffer.count.records', 'N/A')
        
        if ps_buffer_count != oracle_buffer_count:
            print(f"     ⚠ Buffer count differs: ps_sn_p={ps_buffer_count}, oracle_sf_p={oracle_buffer_count}")
        
        ps_buffer_time = ps_config.get('buffer.flush.time', 'N/A')
        oracle_buffer_time = oracle_config.get('buffer.flush.time', 'N/A')
        
        if ps_buffer_time != oracle_buffer_time:
            print(f"     ⚠ Buffer flush time differs: ps_sn_p={ps_buffer_time}, oracle_sf_p={oracle_buffer_time}")
        
        # Check value converter
        ps_value_conv = ps_config.get('value.converter', 'N/A')
        oracle_value_conv = oracle_config.get('value.converter', 'N/A')
        
        if ps_value_conv != oracle_value_conv:
            print(f"     ⚠ Value converter differs: ps_sn_p={ps_value_conv}, oracle_sf_p={oracle_value_conv}")
        
        ps_schema_enable = ps_config.get('value.converter.schemas.enable', 'N/A')
        oracle_schema_enable = oracle_config.get('value.converter.schemas.enable', 'N/A')
        
        if ps_schema_enable != oracle_schema_enable:
            print(f"     ⚠ Schema enable differs: ps_sn_p={ps_schema_enable}, oracle_sf_p={oracle_schema_enable}")
        
except Exception as e:
    print(f"   ❌ Error comparing: {e}")

print("\n4. CHECKING CONNECTOR STATUS")
print("-" * 70)

for connector_name in [ps_sn_p_sink, oracle_sf_p_sink]:
    try:
        r = requests.get(f"{kafka_connect_url}/connectors/{connector_name}/status", timeout=5)
        if r.status_code == 200:
            status = r.json()
            connector_state = status.get('connector', {}).get('state', 'N/A')
            tasks = status.get('tasks', [])
            print(f"\n   {connector_name}:")
            print(f"     State: {connector_state}")
            for task in tasks:
                task_state = task.get('state', 'N/A')
                task_id = task.get('id', 'N/A')
                print(f"     Task {task_id}: {task_state}")
                if task_state == 'FAILED':
                    trace = task.get('trace', '')
                    if trace:
                        print(f"       Error: {trace[:200]}")
        else:
            print(f"   {connector_name}: Not found ({r.status_code})")
    except Exception as e:
        print(f"   {connector_name}: Error - {e}")

print("\n" + "=" * 70)

