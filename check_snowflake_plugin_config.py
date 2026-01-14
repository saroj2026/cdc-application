"""Check Snowflake connector plugin configuration schema and requirements."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
PLUGIN_CLASS = "com.snowflake.kafka.connector.SnowflakeSinkConnector"

print("=" * 70)
print("Checking Snowflake Connector Plugin Configuration")
print("=" * 70)

try:
    # Get plugin config schema
    print(f"\n1. Getting configuration schema for {PLUGIN_CLASS}...")
    response = requests.get(
        f"{KAFKA_CONNECT_URL}/connector-plugins/{PLUGIN_CLASS}/config",
        timeout=10
    )
    
    if response.status_code == 200:
        config_schema = response.json()
        
        # Handle both dict and list responses
        if isinstance(config_schema, list):
            config_items = config_schema
        elif isinstance(config_schema, dict):
            config_items = list(config_schema.items())
        else:
            config_items = []
        
        print(f"   Found {len(config_items)} configuration items")
        
        # Filter authentication-related configs
        auth_configs = []
        all_configs = []
        
        for item in config_items:
            if isinstance(item, dict):
                config_name = item.get('definition', {}).get('name', item.get('name', ''))
                config_def = item.get('definition', item)
            elif isinstance(item, tuple):
                config_name, config_def = item
            else:
                continue
            
            all_configs.append({
                'name': config_name,
                'definition': config_def
            })
            
            # Check if it's auth-related
            if any(keyword in config_name.lower() for keyword in ['password', 'private.key', 'key', 'auth', 'credential']):
                auth_configs.append({
                    'name': config_name,
                    'definition': config_def
                })
        
        if auth_configs:
            print(f"\n2. Authentication-related configurations:")
            for cfg in auth_configs:
                name = cfg['name']
                defn = cfg['definition']
                
                # Extract properties
                if isinstance(defn, dict):
                    required = defn.get('required', defn.get('importance') == 'HIGH')
                    default = defn.get('default_value', defn.get('default', 'N/A'))
                    importance = defn.get('importance', 'N/A')
                    doc = defn.get('documentation', defn.get('doc', ''))
                    group = defn.get('group', 'N/A')
                else:
                    required = False
                    default = 'N/A'
                    importance = 'N/A'
                    doc = ''
                    group = 'N/A'
                
                print(f"\n   [{name}]")
                print(f"   Required: {required}")
                print(f"   Importance: {importance}")
                print(f"   Default: {default}")
                print(f"   Group: {group}")
                if doc:
                    doc_short = doc[:200].replace('\n', ' ')
                    print(f"   Documentation: {doc_short}...")
        else:
            print(f"\n   No auth configs found, showing all configs related to 'snowflake':")
            snowflake_configs = [c for c in all_configs if 'snowflake' in c['name'].lower()]
            for cfg in snowflake_configs[:10]:
                print(f"   - {cfg['name']}")
        
        # Check for password vs private key
        print(f"\n3. Authentication Method Analysis:")
        
        has_password = any('password' in c['name'].lower() for c in all_configs)
        has_private_key = any('private.key' in c['name'].lower() for c in all_configs)
        
        print(f"   Password config exists: {has_password}")
        print(f"   Private key config exists: {has_private_key}")
        
        if has_password and has_private_key:
            # Check which one is required
            password_req = any(
                'password' in c['name'].lower() and 
                (c['definition'].get('required', False) if isinstance(c['definition'], dict) else False)
                for c in all_configs
            )
            pkey_req = any(
                'private.key' in c['name'].lower() and 
                (c['definition'].get('required', False) if isinstance(c['definition'], dict) else False)
                for c in all_configs
            )
            
            print(f"\n   Password required: {password_req}")
            print(f"   Private key required: {pkey_req}")
            
            if pkey_req and not password_req:
                print(f"\n   ⚠️  WARNING: Private key appears to be REQUIRED")
                print(f"   The connector may not support password-only authentication")
            elif password_req and not pkey_req:
                print(f"\n   ✅ Password authentication is supported")
            elif password_req and pkey_req:
                print(f"\n   ⚠️  Both password and private key are marked as required")
                print(f"   This may be a configuration issue")
            else:
                print(f"\n   ✅ Both authentication methods are optional")
                print(f"   Either password or private key can be used")
        elif has_password:
            print(f"   ✅ Only password authentication available")
        elif has_private_key:
            print(f"   ⚠️  Only private key authentication available")
        
        # Show all snowflake config names
        print(f"\n4. All Snowflake configuration parameters:")
        sf_configs = sorted([c['name'] for c in all_configs if 'snowflake' in c['name'].lower()])
        for cfg_name in sf_configs:
            print(f"   - {cfg_name}")
            
    else:
        print(f"   ❌ Error getting config schema: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)

