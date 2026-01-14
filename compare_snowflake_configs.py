#!/usr/bin/env python3
"""Compare Snowflake sink connector configurations."""

import requests

print("=" * 70)
print("COMPARING SNOWFLAKE SINK CONNECTOR CONFIGURATIONS")
print("=" * 70)

kafka_connect_url = "http://72.61.233.209:8083"

# Get configurations
connectors = {
    "oracle_sf_p": "sink-oracle_sf_p-snow-public",
    "ps_sn_p": "sink-ps_sn_p-snowflake-public"
}

configs = {}

for pipeline_name, connector_name in connectors.items():
    print(f"\n1. Getting configuration for {pipeline_name} ({connector_name})...")
    try:
        r = requests.get(f"{kafka_connect_url}/connectors/{connector_name}/config", timeout=5)
        if r.status_code == 200:
            configs[pipeline_name] = r.json()
            print(f"   ✅ Configuration retrieved")
        else:
            print(f"   ❌ Error: {r.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
print("CONFIGURATION COMPARISON")
print("=" * 70)

if "ps_sn_p" in configs and "oracle_sf_p" in configs:
    ps_config = configs["ps_sn_p"]
    oracle_config = configs["oracle_sf_p"]
    
    print("\nKey Differences:")
    print("-" * 70)
    
    # Compare topics
    print(f"\nTopics:")
    print(f"  ps_sn_p:    {ps_config.get('topics', 'N/A')}")
    print(f"  oracle_sf_p: {oracle_config.get('topics', 'N/A')}")
    
    # Compare topic2table map
    print(f"\nTopic-to-Table Mapping:")
    print(f"  ps_sn_p:    {ps_config.get('snowflake.topic2table.map', 'N/A')}")
    print(f"  oracle_sf_p: {oracle_config.get('snowflake.topic2table.map', 'N/A')}")
    
    # Check for case sensitivity issue
    ps_topics = ps_config.get('topics', '')
    ps_map = ps_config.get('snowflake.topic2table.map', '')
    
    oracle_topics = oracle_config.get('topics', '')
    oracle_map = oracle_config.get('snowflake.topic2table.map', '')
    
    print(f"\n⚠ POTENTIAL ISSUE DETECTED:")
    print("-" * 70)
    
    # Oracle topic is uppercase: oracle_sf_p.CDC_USER.TEST
    # But map might be lowercase: oracle_sf_p.cdc_user.test:test
    if 'CDC_USER' in oracle_topics and 'cdc_user' in oracle_map:
        print(f"  ❌ CASE MISMATCH DETECTED!")
        print(f"     Topic name: {oracle_topics} (UPPERCASE)")
        print(f"     Map entry:  {oracle_map} (lowercase)")
        print(f"     This mismatch will prevent the connector from matching topics!")
        print(f"\n  ✅ FIX: Update topic2table map to use UPPERCASE:")
        print(f"     Current: {oracle_map}")
        print(f"     Should be: oracle_sf_p.CDC_USER.TEST:test")
    else:
        print(f"  ✅ Topic and map case match")
    
    # Compare other settings
    print(f"\nOther Settings Comparison:")
    print(f"  Buffer flush time:")
    print(f"    ps_sn_p:    {ps_config.get('buffer.flush.time', 'N/A')}")
    print(f"    oracle_sf_p: {oracle_config.get('buffer.flush.time', 'N/A')}")
    
    print(f"  Buffer count records:")
    print(f"    ps_sn_p:    {ps_config.get('buffer.count.records', 'N/A')}")
    print(f"    oracle_sf_p: {oracle_config.get('buffer.count.records', 'N/A')}")
    
    print(f"  Value converter:")
    print(f"    ps_sn_p:    {ps_config.get('value.converter', 'N/A')}")
    print(f"    oracle_sf_p: {oracle_config.get('value.converter', 'N/A')}")
    
    print(f"  Schema enable:")
    print(f"    ps_sn_p:    {ps_config.get('value.converter.schemas.enable', 'N/A')}")
    print(f"    oracle_sf_p: {oracle_config.get('value.converter.schemas.enable', 'N/A')}")

print("\n" + "=" * 70)
print("RECOMMENDATION")
print("=" * 70)
if 'CDC_USER' in oracle_topics and 'cdc_user' in oracle_map:
    print("❌ CRITICAL ISSUE: Topic name case mismatch!")
    print("\nThe topic name is UPPERCASE (oracle_sf_p.CDC_USER.TEST)")
    print("but the topic2table map uses lowercase (oracle_sf_p.cdc_user.test:test)")
    print("\nThis will prevent the connector from matching the topic to the table!")
    print("\n✅ SOLUTION: Update the topic2table map to:")
    print("   oracle_sf_p.CDC_USER.TEST:test")
else:
    print("✅ Configuration looks correct")
print("=" * 70)

