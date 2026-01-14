"""Update Oracle connection to use new schema if needed."""
from ingestion.database.session import get_db
from ingestion.database.models_db import ConnectionModel

print("=== CHECKING ORACLE CONNECTION ===")

db = next(get_db())
try:
    # Find Oracle connection
    oracle_conn = db.query(ConnectionModel).filter(
        ConnectionModel.database_type == "oracle"
    ).first()
    
    if oracle_conn:
        print(f"Oracle Connection:")
        print(f"  Name: {oracle_conn.name}")
        print(f"  Username: {oracle_conn.username}")
        print(f"  Database: {oracle_conn.database}")
        print(f"  Schema: {getattr(oracle_conn, 'schema', 'N/A')}")
        
        # Check if we need to update username
        if oracle_conn.username == "c##cdc_user":
            print(f"\nNOTE: Connection username is still 'c##cdc_user'")
            print(f"  If you want to use the new 'cdc_user' schema, you may need to:")
            print(f"  1. Create a new connection with username 'cdc_user'")
            print(f"  2. Or update this connection's username")
            print(f"  For now, we'll keep the connection as-is and just update the pipeline schema")
    else:
        print("No Oracle connection found!")
        
finally:
    db.close()

