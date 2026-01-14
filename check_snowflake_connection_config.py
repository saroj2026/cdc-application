"""Check if Snowflake connection has private key configured."""

import psycopg2
import json

DB_CONFIG = {
    "host": "72.61.233.209",
    "port": 5432,
    "database": "cdctest",
    "user": "cdc_user",
    "password": "cdc_pass"
}

print("=" * 70)
print("Checking Snowflake Connection Configuration")
print("=" * 70)

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Find Snowflake connections
    cursor.execute("""
        SELECT id, name, username, host, database, schema, additional_config
        FROM connections
        WHERE database_type = 'snowflake'
    """)
    
    connections = cursor.fetchall()
    
    if not connections:
        print("\n❌ No Snowflake connections found")
        exit(1)
    
    for conn_row in connections:
        conn_id, name, username, host, database, schema, additional_config = conn_row
        
        print(f"\n{'='*70}")
        print(f"Connection: {name} (ID: {conn_id})")
        print(f"{'='*70}")
        
        print(f"\nBasic Info:")
        print(f"  Username: {username}")
        print(f"  Host/Account: {host}")
        print(f"  Database: {database}")
        print(f"  Schema: {schema}")
        
        # Parse additional_config
        if isinstance(additional_config, str):
            config = json.loads(additional_config)
        elif additional_config is None:
            config = {}
        else:
            config = additional_config
        
        print(f"\nAdditional Config:")
        print(f"  Account: {config.get('account', 'N/A')}")
        print(f"  Warehouse: {config.get('warehouse', 'N/A')}")
        print(f"  Role: {config.get('role', 'N/A')}")
        print(f"  SSL Enabled: {config.get('ssl_enabled', 'N/A')}")
        
        # Check for private key
        has_private_key = 'private_key' in config
        print(f"\nAuthentication:")
        print(f"  Private Key: {'✅ Present' if has_private_key else '❌ Missing'}")
        
        if has_private_key:
            private_key = config['private_key']
            if isinstance(private_key, str):
                # Check if it looks valid
                has_header = 'BEGIN PRIVATE KEY' in private_key or 'BEGIN RSA PRIVATE KEY' in private_key
                has_footer = 'END PRIVATE KEY' in private_key or 'END RSA PRIVATE KEY' in private_key
                
                if has_header and has_footer:
                    print(f"  Key Format: ✅ Valid (contains headers)")
                    key_length = len(private_key)
                    print(f"  Key Length: {key_length} characters")
                    
                    # Preview
                    if 'BEGIN PRIVATE KEY' in private_key:
                        lines = private_key.split('\n')
                        if len(lines) > 2:
                            preview = f"{lines[0]}\\n{lines[1][:30]}...\\n{lines[-1]}"
                        else:
                            preview = private_key[:100] + "..."
                    else:
                        preview = private_key[:100] + "..."
                    print(f"  Preview: {preview}")
                else:
                    print(f"  Key Format: ⚠️  Warning - missing headers/footers")
                    print(f"  Preview: {private_key[:100]}...")
            else:
                print(f"  Key Format: ❌ Invalid (not a string)")
        
        # Status
        print(f"\nStatus:")
        if has_private_key:
            print(f"  ✅ Ready for sink connector creation")
        else:
            print(f"  ❌ Not ready - private key required")
            print(f"\n  To add private key, run:")
            print(f"    python update_snowflake_connection_with_key.py {name} <private_key_file>")
    
    cursor.close()
    conn.close()
    
    print(f"\n{'='*70}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

