"""Check Snowflake connector plugin version and configuration requirements."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

print("=" * 70)
print("Checking Snowflake Connector Plugin Configuration")
print("=" * 70)

try:
    # Get all connector plugins
    print("\n1. Getting all connector plugins...")
    response = requests.get(f"{KAFKA_CONNECT_URL}/connector-plugins", timeout=10)
    
    if response.status_code == 200:
        plugins = response.json()
        print(f"   Found {len(plugins)} connector plugins")
        
        # Find Snowflake plugin
        snowflake_plugins = [
            p for p in plugins 
            if 'snowflake' in p.get('class', '').lower()
        ]
        
        if not snowflake_plugins:
            print("\n   ❌ No Snowflake connector plugin found!")
            print("\n   Available plugins:")
            for p in plugins[:10]:
                print(f"      - {p.get('class', 'N/A')}")
            if len(plugins) > 10:
                print(f"      ... and {len(plugins) - 10} more")
        else:
            for plugin in snowflake_plugins:
                print(f"\n2. Snowflake Plugin Details:")
                print(f"   Class: {plugin.get('class', 'N/A')}")
                print(f"   Type: {plugin.get('type', 'N/A')}")
                print(f"   Version: {plugin.get('version', 'N/A')}")
                
                # Try to get plugin configuration
                print(f"\n3. Getting plugin configuration schema...")
                plugin_class = plugin.get('class', '')
                
                # Try to get config definition
                try:
                    config_response = requests.get(
                        f"{KAFKA_CONNECT_URL}/connector-plugins/{plugin_class}/config",
                        timeout=10
                    )
                    
                    if config_response.status_code == 200:
                        config_schema = config_response.json()
                        
                        # Look for authentication-related configs
                        print(f"   Configuration definitions found")
                        
                        auth_configs = []
                        for config_name, config_info in config_schema.items():
                            if any(keyword in config_name.lower() for keyword in ['password', 'private.key', 'key', 'auth']):
                                auth_configs.append({
                                    'name': config_name,
                                    'required': config_info.get('required', False),
                                    'default': config_info.get('default_value', 'N/A'),
                                    'importance': config_info.get('importance', 'N/A'),
                                    'documentation': config_info.get('documentation', '')[:100]
                                })
                        
                        if auth_configs:
                            print(f"\n   Authentication-related configurations:")
                            for cfg in auth_configs:
                                print(f"\n   - {cfg['name']}:")
                                print(f"     Required: {cfg['required']}")
                                print(f"     Default: {cfg['default']}")
                                print(f"     Importance: {cfg['importance']}")
                                if cfg['documentation']:
                                    print(f"     Docs: {cfg['documentation']}")
                        else:
                            print(f"   No authentication configs found in schema")
                            
                    else:
                        print(f"   Could not get config schema (status: {config_response.status_code})")
                        
                except Exception as e:
                    print(f"   Error getting config schema: {e}")
                
                # Try to validate a sample config
                print(f"\n4. Testing configuration validation...")
                
                # Test with password
                test_config_password = {
                    "snowflake.url.name": "https://test-account.snowflakecomputing.com",
                    "snowflake.user.name": "test_user",
                    "snowflake.password": "test_password",
                    "snowflake.database.name": "test_db",
                    "snowflake.schema.name": "test_schema",
                    "topics": "test_topic",
                    "connector.class": plugin_class
                }
                
                try:
                    validate_response = requests.put(
                        f"{KAFKA_CONNECT_URL}/connector-plugins/{plugin_class}/config/validate",
                        json={"name": "test-connector", "config": test_config_password},
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                    
                    if validate_response.status_code == 200:
                        validation_result = validate_response.json()
                        configs = validation_result.get('configs', [])
                        
                        print(f"   Validation result (with password):")
                        errors = [c for c in configs if c.get('value', {}).get('errors')]
                        if errors:
                            print(f"   ❌ Errors found:")
                            for err in errors:
                                print(f"      {err.get('value', {}).get('name', 'N/A')}: {err.get('value', {}).get('errors', [])}")
                        else:
                            print(f"   ✅ Password authentication configuration is valid!")
                    else:
                        print(f"   Could not validate (status: {validate_response.status_code})")
                        print(f"   Response: {validate_response.text[:500]}")
                        
                except Exception as e:
                    print(f"   Error during validation: {e}")
                
                # Test with private key
                test_config_pkey = {
                    "snowflake.url.name": "https://test-account.snowflakecomputing.com",
                    "snowflake.user.name": "test_user",
                    "snowflake.private.key": "test_private_key",
                    "snowflake.database.name": "test_db",
                    "snowflake.schema.name": "test_schema",
                    "topics": "test_topic",
                    "connector.class": plugin_class
                }
                
                try:
                    validate_response = requests.put(
                        f"{KAFKA_CONNECT_URL}/connector-plugins/{plugin_class}/config/validate",
                        json={"name": "test-connector", "config": test_config_pkey},
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                    
                    if validate_response.status_code == 200:
                        validation_result = validate_response.json()
                        configs = validation_result.get('configs', [])
                        
                        print(f"\n   Validation result (with private key):")
                        errors = [c for c in configs if c.get('value', {}).get('errors')]
                        if errors:
                            print(f"   ❌ Errors found:")
                            for err in errors:
                                print(f"      {err.get('value', {}).get('name', 'N/A')}: {err.get('value', {}).get('errors', [])}")
                        else:
                            print(f"   ✅ Private key authentication configuration is valid!")
                    else:
                        print(f"   Could not validate (status: {validate_response.status_code})")
                        
                except Exception as e:
                    print(f"   Error during validation: {e}")
                    
    else:
        print(f"   ❌ Error getting plugins: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
