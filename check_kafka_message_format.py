#!/usr/bin/env python3
"""Check Kafka message format to see if Snowflake connector can process them."""

import requests
import json

print("=" * 70)
print("CHECKING KAFKA MESSAGE FORMAT")
print("=" * 70)

kafka_ui_url = "http://72.61.233.209:8080"
topic_name = "oracle_sf_p.CDC_USER.TEST"

print(f"\n1. Getting sample messages from topic: {topic_name}")
print("-" * 70)

try:
    # Get topic info
    r = requests.get(f"{kafka_ui_url}/api/clusters/local/topics/{topic_name}")
    if r.status_code == 200:
        topic_info = r.json()
        partitions = topic_info.get('partitions', [])
        if partitions:
            partition = partitions[0]
            partition_id = partition.get('partition', 0)
            
            # Get messages from the topic
            # Try to get a few messages to see the format
            messages_url = f"{kafka_ui_url}/api/clusters/local/topics/{topic_name}/partitions/{partition_id}/messages"
            
            # Get first message (offset 0)
            params = {
                'offset': '0',
                'limit': '3'  # Get first 3 messages
            }
            
            r = requests.get(messages_url, params=params)
            if r.status_code == 200:
                messages_data = r.json()
                messages = messages_data.get('messages', [])
                
                print(f"\n   Found {len(messages)} messages")
                
                for i, msg in enumerate(messages, 1):
                    print(f"\n   Message {i} (Offset {msg.get('offset', 'N/A')}):")
                    print(f"   Key: {msg.get('key', 'N/A')}")
                    
                    value = msg.get('value', {})
                    if isinstance(value, dict):
                        # Try to parse as JSON
                        print(f"   Value (JSON):")
                        print(f"   {json.dumps(value, indent=2)[:500]}...")
                        
                        # Check if it's a Debezium message
                        if 'payload' in value:
                            payload = value['payload']
                            op = payload.get('op', 'N/A')
                            print(f"\n   Operation: {op}")
                            if 'after' in payload:
                                print(f"   After: {payload['after']}")
                            if 'before' in payload:
                                print(f"   Before: {payload['before']}")
                    else:
                        print(f"   Value: {str(value)[:200]}...")
            else:
                print(f"   ⚠️ Could not get messages: {r.status_code}")
    else:
        print(f"   ⚠️ Could not get topic info: {r.status_code}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("ANALYSIS")
print("=" * 70)
print("The Snowflake Kafka connector expects Debezium messages in a specific format.")
print("If messages are in the correct format, they should be processed.")
print("If not, the connector might be silently failing or buffering incorrectly.")
print("=" * 70)
