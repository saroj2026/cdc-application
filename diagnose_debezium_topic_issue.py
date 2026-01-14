"""Diagnose why Kafka topic is not being created for Debezium connector."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
connector_name = "cdc-ps_sn_p-pg-public"

print("=" * 70)
print("Debezium Connector Topic Issue Diagnosis")
print("=" * 70)

try:
    # Get connector config
    print(f"\n1. Getting connector configuration...")
    config_response = requests.get(
        f"{KAFKA_CONNECT_URL}/connectors/{connector_name}/config",
        timeout=10
    )
    
    if config_response.status_code == 200:
        config = config_response.json()
        
        print(f"   Topic Prefix: {config.get('topic.prefix')}")
        print(f"   Database: {config.get('database.dbname')}")
        print(f"   Schema Include: {config.get('schema.include.list', config.get('schema.whitelist', 'N/A'))}")
        print(f"   Table Include: {config.get('table.include.list', config.get('table.whitelist', 'N/A'))}")
        
        # Issue: table.include.list has "public.projects_simple" which includes schema
        # This causes topic name to be: {prefix}.{schema}.{table} = ps_sn_p.public.public.projects_simple
        table_include = config.get('table.include.list', config.get('table.whitelist', ''))
        schema_include = config.get('schema.include.list', config.get('schema.whitelist', ''))
        
        print(f"\n2. Topic Name Analysis:")
        if table_include and '.' in table_include:
            print(f"   ⚠️  ISSUE: table.include.list contains schema prefix: {table_include}")
            print(f"   This causes duplicate schema in topic name!")
            print(f"   Expected format: table.include.list should be just table name, not schema.table")
        
        # Calculate expected topic
        topic_prefix = config.get('topic.prefix', 'ps_sn_p')
        if schema_include:
            schema = schema_include
        elif table_include and '.' in table_include:
            # Extract schema from table.include.list
            parts = table_include.split('.')
            if len(parts) >= 2:
                schema = parts[0]
                table = '.'.join(parts[1:])
            else:
                schema = 'public'
                table = table_include
        else:
            schema = 'public'
            table = table_include or 'projects_simple'
        
        expected_topic_correct = f"{topic_prefix}.{schema}.{table}" if schema else f"{topic_prefix}.{table}"
        print(f"   Correct Topic Name: {expected_topic_correct}")
        
        # Current (wrong) topic name
        if table_include and '.' in table_include and schema_include:
            wrong_topic = f"{topic_prefix}.{schema_include}.{table_include}"
            print(f"   Wrong Topic Name: {wrong_topic}")
    
    # Get connector status and errors
    print(f"\n3. Getting connector status...")
    status_response = requests.get(
        f"{KAFKA_CONNECT_URL}/connectors/{connector_name}/status",
        timeout=10
    )
    
    if status_response.status_code == 200:
        status = status_response.json()
        connector_state = status.get('connector', {}).get('state', 'N/A')
        print(f"   Connector State: {connector_state}")
        
        tasks = status.get('tasks', [])
        for task in tasks:
            task_id = task.get('id')
            task_state = task.get('state', 'N/A')
            print(f"   Task {task_id} State: {task_state}")
            
            if task_state == 'FAILED':
                trace = task.get('trace', '')
                print(f"   Task {task_id} Error: {trace[:500]}")
    
    # Check connector restart
    print(f"\n4. Recommendation:")
    print(f"   The table.include.list should be just 'projects_simple', not 'public.projects_simple'")
    print(f"   OR schema.include.list should be empty if table.include.list includes schema")
    print(f"   This will create topic: ps_sn_p.public.projects_simple")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)


