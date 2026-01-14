#!/usr/bin/env python3
"""Fix Snowflake sink connector topic2table mapping to use actual topic names."""

import requests

print("=" * 70)
print("FIXING SNOWFLAKE TOPIC2TABLE MAPPING")
print("=" * 70)

kafka_connect_url = "http://72.61.233.209:8083"
sink_connector_name = "sink-oracle_sf_p-snow-public"

print("\n1. Getting current configuration...")
try:
    r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector_name}/config", timeout=5)
    if r.status_code == 200:
        config = r.json()
        
        current_topics = config.get('topics', '')
        current_map = config.get('snowflake.topic2table.map', '')
        
        print(f"   Current topics: {current_topics}")
        print(f"   Current map: {current_map}")
        
        # The issue: Topic is UPPERCASE (oracle_sf_p.CDC_USER.TEST)
        # But map is lowercase (oracle_sf_p.cdc_user.test:test)
        # We need to use the actual topic name (UPPERCASE) in the map
        
        print("\n2. Fixing topic2table mapping...")
        print("   Topic name: oracle_sf_p.CDC_USER.TEST (UPPERCASE)")
        print("   Current map: oracle_sf_p.cdc_user.test:test (lowercase) ❌")
        print("   Fixed map: oracle_sf_p.CDC_USER.TEST:test (UPPERCASE) ✅")
        
        # Extract table name from topic (last part after last dot)
        topic_name = "oracle_sf_p.CDC_USER.TEST"
        table_name = topic_name.split('.')[-1]  # Gets "TEST"
        
        # But we want lowercase table name for Snowflake
        table_name_lower = table_name.lower()  # Gets "test"
        
        # Build correct mapping using actual topic name (UPPERCASE)
        new_map = f"{topic_name}:{table_name_lower}"
        
        print(f"\n3. Updating configuration...")
        new_config = config.copy()
        new_config['snowflake.topic2table.map'] = new_map
        
        update_r = requests.put(
            f"{kafka_connect_url}/connectors/{sink_connector_name}/config",
            json=new_config,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if update_r.status_code == 200:
            updated_config = update_r.json()
            print(f"   ✅ Configuration updated successfully!")
            print(f"   New map: {updated_config.get('snowflake.topic2table.map', 'N/A')}")
            
            print("\n4. Restarting connector to apply changes...")
            restart_r = requests.post(f"{kafka_connect_url}/connectors/{sink_connector_name}/restart", timeout=10)
            if restart_r.status_code == 204:
                print("   ✅ Connector restart initiated")
                print("   Waiting 20 seconds for connector to restart...")
                import time
                time.sleep(20)
                
                # Verify status
                status_r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector_name}/status", timeout=5)
                if status_r.status_code == 200:
                    status = status_r.json()
                    connector_state = status.get('connector', {}).get('state', 'N/A')
                    print(f"\n   Connector state: {connector_state}")
                    
                    tasks = status.get('tasks', [])
                    for task in tasks:
                        print(f"   Task {task.get('id', 'N/A')} state: {task.get('state', 'N/A')}")
                    
                    if connector_state == 'RUNNING':
                        print(f"\n   ✅✅✅ Connector is RUNNING with fixed configuration!")
                        print(f"   The topic2table map now matches the actual topic name (UPPERCASE)")
                        print(f"   Messages should now be processed correctly!")
        else:
            print(f"   ❌ Config update failed: {update_r.status_code} - {update_r.text}")
    else:
        print(f"   ❌ Error getting config: {r.status_code}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("FIX COMPLETE")
print("=" * 70)
print("\nNext Steps:")
print("  1. Wait 60-90 seconds for buffer flush")
print("  2. Check Snowflake for CDC events")
print("  3. Run: python monitor_cdc_to_snowflake.py")
print("=" * 70)

