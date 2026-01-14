"""Update SQL Server connection to include trust_server_certificate."""

import requests
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

print("=" * 80)
print("Updating SQL Server Connection Configuration")
print("=" * 80)

# Connect to database directly
DATABASE_URL = "postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest"

print("\n1. Connecting to database...")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

try:
    from ingestion.database.models_db import ConnectionModel
    
    # Find SQL Server connection
    print("\n2. Finding SQL Server connection...")
    sql_conn = db.query(ConnectionModel).filter(
        ConnectionModel.database_type == "sqlserver",
        ConnectionModel.database == "cdctest",
        ConnectionModel.deleted_at.is_(None)
    ).first()
    
    if sql_conn:
        print(f"   [OK] Found connection: {sql_conn.name} (ID: {sql_conn.id})")
        
        # Get current additional_config
        additional_config = sql_conn.additional_config or {}
        print(f"   Current additional_config: {additional_config}")
        
        # Update to include trust_server_certificate
        additional_config['trust_server_certificate'] = True
        additional_config['encrypt'] = False
        
        sql_conn.additional_config = additional_config
        db.commit()
        
        print(f"   [OK] Updated additional_config:")
        print(f"      trust_server_certificate: {additional_config.get('trust_server_certificate')}")
        print(f"      encrypt: {additional_config.get('encrypt')}")
    else:
        print("   [ERROR] SQL Server connection not found")
    
    db.close()
    
except Exception as e:
    print(f"   [ERROR] Exception: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
    db.close()

print("\n" + "=" * 80)
print("Connection Updated!")
print("=" * 80)
print("\nNow restart the pipeline to use the updated connection settings.")


import requests
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

print("=" * 80)
print("Updating SQL Server Connection Configuration")
print("=" * 80)

# Connect to database directly
DATABASE_URL = "postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest"

print("\n1. Connecting to database...")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

try:
    from ingestion.database.models_db import ConnectionModel
    
    # Find SQL Server connection
    print("\n2. Finding SQL Server connection...")
    sql_conn = db.query(ConnectionModel).filter(
        ConnectionModel.database_type == "sqlserver",
        ConnectionModel.database == "cdctest",
        ConnectionModel.deleted_at.is_(None)
    ).first()
    
    if sql_conn:
        print(f"   [OK] Found connection: {sql_conn.name} (ID: {sql_conn.id})")
        
        # Get current additional_config
        additional_config = sql_conn.additional_config or {}
        print(f"   Current additional_config: {additional_config}")
        
        # Update to include trust_server_certificate
        additional_config['trust_server_certificate'] = True
        additional_config['encrypt'] = False
        
        sql_conn.additional_config = additional_config
        db.commit()
        
        print(f"   [OK] Updated additional_config:")
        print(f"      trust_server_certificate: {additional_config.get('trust_server_certificate')}")
        print(f"      encrypt: {additional_config.get('encrypt')}")
    else:
        print("   [ERROR] SQL Server connection not found")
    
    db.close()
    
except Exception as e:
    print(f"   [ERROR] Exception: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
    db.close()

print("\n" + "=" * 80)
print("Connection Updated!")
print("=" * 80)
print("\nNow restart the pipeline to use the updated connection settings.")

