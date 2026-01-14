"""Update Snowflake connection with new account and test."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.database.session import SessionLocal
from ingestion.database.models_db import ConnectionModel
from ingestion.connection_service import ConnectionService
import json

def update_and_test_snowflake():
    db = SessionLocal()
    try:
        # Get the snowflake-s connection
        connection = db.query(ConnectionModel).filter(
            ConnectionModel.name == 'snowflake-s',
            ConnectionModel.deleted_at.is_(None)
        ).first()
        
        if not connection:
            print("❌ Connection 'snowflake-s' not found")
            return
        
        print("=" * 70)
        print("📋 CURRENT VALUES")
        print("=" * 70)
        print(f"Account (Host): {connection.host}")
        print(f"Database: {connection.database}")
        print(f"Username: {connection.username}")
        print()
        
        # Update with new account
        new_account = "YBVYVAW-UV44557"
        print(f"🔄 Updating account to: {new_account}")
        
        connection.host = new_account
        if connection.additional_config:
            connection.additional_config['account'] = new_account
        else:
            connection.additional_config = {'account': new_account}
        
        db.commit()
        db.refresh(connection)
        
        print("✅ Account updated in database")
        print()
        
        # Test the connection
        print("=" * 70)
        print("🧪 TESTING CONNECTION WITH NEW ACCOUNT")
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
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        import traceback
        print(traceback.format_exc())
    finally:
        db.close()

if __name__ == "__main__":
    update_and_test_snowflake()


