"""
Check all connections in the database to see host column values.
This script queries the public.connections table to see what's stored.
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Set DATABASE_URL environment variable FIRST, before any imports that use it
# Backend DB: PostgreSQL on 72.61.233.209:5432, database=cdctest, user=cdc_user, password=cdc_pass
if not os.environ.get("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest"

# Add the ingestion module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Database connection for backend database
DB_URL = os.environ.get("DATABASE_URL", "postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest")

def get_db_session():
    """Get database session."""
    engine = create_engine(DB_URL)
    Session = sessionmaker(bind=engine)
    return Session()

def main():
    print("=" * 80)
    print("CHECKING ALL CONNECTIONS IN public.connections TABLE")
    print("=" * 80)
    print()
    
    session = get_db_session()
    
    try:
        # Query all connections
        result = session.execute(text("""
            SELECT 
                id,
                name,
                connection_type,
                database_type,
                host,
                port,
                database,
                username,
                schema,
                additional_config,
                is_active,
                created_at,
                updated_at,
                deleted_at
            FROM connections
            WHERE deleted_at IS NULL
            ORDER BY created_at DESC
        """))
        
        connections = result.fetchall()
        
        if not connections:
            print("No connections found in the database.")
            return
        
        print(f"Found {len(connections)} connection(s):\n")
        print("-" * 80)
        
        for idx, conn in enumerate(connections, 1):
            conn_id, name, conn_type, db_type, host, port, database, username, schema, additional_config, is_active, created_at, updated_at, deleted_at = conn
            
            print(f"\n{idx}. Connection ID: {conn_id}")
            print(f"   Name: {name}")
            print(f"   Connection Type: {conn_type}")
            print(f"   Database Type: {db_type}")
            print(f"   ⚠️  HOST: {host}")
            print(f"   Port: {port}")
            print(f"   Database: {database}")
            print(f"   Username: {username}")
            print(f"   Schema: {schema}")
            print(f"   Additional Config: {additional_config}")
            print(f"   Is Active: {is_active}")
            print(f"   Created At: {created_at}")
            print(f"   Updated At: {updated_at}")
            
            # Check if host looks like a Snowflake account (not a proper hostname/IP)
            if db_type and db_type.lower() != "snowflake":
                if host and ("." in host and not any(c.isdigit() for c in host.split(".")[0]) and "snowflake" not in host.lower()):
                    # Check if it looks like a Snowflake account name pattern
                    if any(x in host.lower() for x in ["us-east", "us-west", "eu-west", "ap-south", "ap-southeast", ".aws", ".azure"]):
                        print(f"   ⚠️  WARNING: Host field contains what looks like a Snowflake account name!")
                    elif not any(c in host for c in [":", "/"]) and "." not in host:
                        # Doesn't look like IP or hostname
                        print(f"   ⚠️  WARNING: Host field may not be a valid hostname/IP address!")
            
            print("-" * 80)
        
        # Also check for connections where database_type != snowflake but host contains snowflake-like patterns
        print("\n" + "=" * 80)
        print("CHECKING FOR POTENTIAL ISSUES:")
        print("=" * 80)
        print()
        
        suspicious_result = session.execute(text("""
            SELECT 
                id,
                name,
                database_type,
                host
            FROM connections
            WHERE deleted_at IS NULL
            AND database_type != 'snowflake'
            AND (
                host ILIKE '%snowflake%' 
                OR host ILIKE '%.aws%'
                OR host ILIKE '%.azure%'
                OR (host LIKE '%.us-east%' OR host LIKE '%.us-west%' OR host LIKE '%.eu-west%')
                OR (host NOT LIKE '%.%' AND host NOT LIKE '%:%')
            )
        """))
        
        suspicious = suspicious_result.fetchall()
        
        if suspicious:
            print(f"⚠️  Found {len(suspicious)} potentially problematic connection(s):\n")
            for conn_id, name, db_type, host in suspicious:
                print(f"   - {name} (ID: {conn_id})")
                print(f"     Database Type: {db_type}")
                print(f"     Host: {host}")
                print()
        else:
            print("✅ No obvious issues found with host field values.")
        
    except Exception as e:
        print(f"❌ Error querying database: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        session.close()
    
    print("=" * 80)
    return 0

if __name__ == "__main__":
    sys.exit(main())


