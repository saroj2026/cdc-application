"""Read Snowflake connection from database and test with exact stored credentials."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.database.session import SessionLocal
from ingestion.database.models_db import ConnectionModel
from ingestion.connection_service import ConnectionService
import json

def check_and_test_snowflake():
    db = SessionLocal()
    try:
        # Get the snowflake-s connection
        connection = db.query(ConnectionModel).filter(
            ConnectionModel.name == 'snowflake-s',
            ConnectionModel.deleted_at.is_(None)
        ).first()
        
        if not connection:
            print("❌ Connection 'snowflake-s' not found in database")
            return
        
        print("=" * 70)
        print("📋 CURRENT DATABASE VALUES")
        print("=" * 70)
        print(f"ID: {connection.id}")
        print(f"Name: {connection.name}")
        print(f"Database Type: {connection.database_type.value if hasattr(connection.database_type, 'value') else connection.database_type}")
        print(f"Host (Account): {connection.host}")
        print(f"Port: {connection.port}")
        print(f"Database: {connection.database}")
        print(f"Username: {connection.username}")
        print(f"Password: {'***' if connection.password else '(empty)'}")
        print(f"Schema: {connection.schema or '(empty)'}")
        print(f"Additional Config: {json.dumps(connection.additional_config, indent=2)}")
        print()
        
        # Extract Snowflake-specific config
        account = connection.host or (connection.additional_config.get('account') if connection.additional_config else None)
        warehouse = connection.additional_config.get('warehouse') if connection.additional_config else None
        role = connection.additional_config.get('role') if connection.additional_config else None
        
        print("=" * 70)
        print("🔍 SNOWFLAKE CONFIGURATION EXTRACTED")
        print("=" * 70)
        print(f"Account: {account}")
        print(f"User: {connection.username}")
        print(f"Password: {'***' if connection.password else '(empty)'}")
        print(f"Database: {connection.database}")
        print(f"Schema: {connection.schema or 'PUBLIC (default)'}")
        print(f"Warehouse: {warehouse or '(not set)'}")
        print(f"Role: {role or '(not set)'}")
        print()
        
        # Test the connection using ConnectionService
        print("=" * 70)
        print("🧪 TESTING CONNECTION WITH STORED CREDENTIALS")
        print("=" * 70)
        
        connection_service = ConnectionService()
        
        try:
            result = connection_service.test_connection(connection.id, save_history=True)
            
            if result.get('success'):
                print("✅ CONNECTION SUCCESSFUL!")
                print(f"Version: {result.get('version', 'Unknown')}")
                print(f"Message: {result.get('message', '')}")
                print(f"Response Time: {result.get('response_time_ms', 0)}ms")
            else:
                print("❌ CONNECTION FAILED")
                print(f"Status: {result.get('status', 'UNKNOWN')}")
                print(f"Error: {result.get('error', 'Unknown error')}")
                print(f"Response Time: {result.get('response_time_ms', 0)}ms")
                
        except Exception as test_error:
            print("❌ CONNECTION TEST EXCEPTION")
            print(f"Error Type: {type(test_error).__name__}")
            print(f"Error Message: {str(test_error)}")
            
            # Try to get more details
            import traceback
            print("\n📝 Full Traceback:")
            print(traceback.format_exc())
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        print(traceback.format_exc())
    finally:
        db.close()

if __name__ == "__main__":
    check_and_test_snowflake()


