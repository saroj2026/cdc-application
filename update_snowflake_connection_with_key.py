"""Update Snowflake connection in database with private key."""

import psycopg2
import json
import sys

DB_CONFIG = {
    "host": "72.61.233.209",
    "port": 5432,
    "database": "cdctest",
    "user": "cdc_user",
    "password": "cdc_pass"
}

def update_connection_with_key(connection_name, private_key_file):
    """Update Snowflake connection with private key."""
    
    print("=" * 70)
    print("Update Snowflake Connection with Private Key")
    print("=" * 70)
    
    # Read private key file
    print(f"\n1. Reading private key from: {private_key_file}")
    try:
        with open(private_key_file, 'r') as f:
            private_key = f.read().strip()
        
        # Validate it looks like a private key
        if 'BEGIN PRIVATE KEY' not in private_key or 'END PRIVATE KEY' not in private_key:
            print(f"   ⚠️  Warning: File doesn't look like a valid private key")
            response = input("   Continue anyway? (y/n): ")
            if response.lower() != 'y':
                print("   Aborted")
                return False
        else:
            print("   ✅ Private key file looks valid")
            
    except FileNotFoundError:
        print(f"   ❌ Error: File not found: {private_key_file}")
        return False
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
        return False
    
    # Connect to database
    print(f"\n2. Connecting to database...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("   ✅ Connected")
    except Exception as e:
        print(f"   ❌ Error connecting: {e}")
        return False
    
    # Find connection
    print(f"\n3. Finding Snowflake connection: {connection_name}")
    try:
        cursor.execute("""
            SELECT id, name, additional_config
            FROM connections
            WHERE name = %s AND database_type = 'snowflake'
        """, (connection_name,))
        
        row = cursor.fetchone()
        if not row:
            print(f"   ❌ Connection not found: {connection_name}")
            print("\n   Available Snowflake connections:")
            cursor.execute("""
                SELECT name FROM connections WHERE database_type = 'snowflake'
            """)
            for name in cursor.fetchall():
                print(f"      - {name[0]}")
            cursor.close()
            conn.close()
            return False
        
        conn_id, conn_name, additional_config = row
        print(f"   ✅ Found connection: {conn_name} (ID: {conn_id})")
        
    except Exception as e:
        print(f"   ❌ Error finding connection: {e}")
        cursor.close()
        conn.close()
        return False
    
    # Parse existing additional_config
    print(f"\n4. Updating additional_config...")
    try:
        if isinstance(additional_config, str):
            config = json.loads(additional_config)
        elif additional_config is None:
            config = {}
        else:
            config = additional_config
        
        # Store existing values for display
        old_keys = list(config.keys())
        
        # Add private key
        config['private_key'] = private_key
        
        # Keep other important configs if they exist
        important_configs = ['account', 'warehouse', 'role', 'ssl_enabled']
        print(f"   Preserving existing configs: {[k for k in old_keys if k in important_configs]}")
        
        print(f"   ✅ Adding private_key to configuration")
        
    except Exception as e:
        print(f"   ❌ Error parsing config: {e}")
        cursor.close()
        conn.close()
        return False
    
    # Update database
    print(f"\n5. Updating connection in database...")
    try:
        cursor.execute("""
            UPDATE connections
            SET additional_config = %s
            WHERE id = %s
        """, (json.dumps(config), conn_id))
        
        conn.commit()
        print(f"   ✅ Connection updated successfully")
        
    except Exception as e:
        print(f"   ❌ Error updating database: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        return False
    
    # Verify update
    print(f"\n6. Verifying update...")
    try:
        cursor.execute("""
            SELECT additional_config
            FROM connections
            WHERE id = %s
        """, (conn_id,))
        
        updated_config = cursor.fetchone()[0]
        if isinstance(updated_config, str):
            updated_config = json.loads(updated_config)
        
        if 'private_key' in updated_config:
            print(f"   ✅ Private key confirmed in database")
            key_preview = updated_config['private_key'][:50] + "..."
            print(f"   Preview: {key_preview}")
        else:
            print(f"   ⚠️  Warning: Private key not found after update")
            
    except Exception as e:
        print(f"   ⚠️  Warning: Could not verify update: {e}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 70)
    print("✅ Connection updated successfully!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Make sure you've associated the PUBLIC key with your Snowflake user")
    print("2. Test the connection by creating the sink connector")
    print("3. If you haven't set the public key in Snowflake yet, run:")
    print("   ALTER USER <your_username> SET RSA_PUBLIC_KEY='<public_key_b64>';")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python update_snowflake_connection_with_key.py <connection_name> <private_key_file>")
        print("\nExample:")
        print("  python update_snowflake_connection_with_key.py snowflake-s snowflake_rsa_key.p8")
        sys.exit(1)
    
    connection_name = sys.argv[1]
    private_key_file = sys.argv[2]
    
    success = update_connection_with_key(connection_name, private_key_file)
    sys.exit(0 if success else 1)

