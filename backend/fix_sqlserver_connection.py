"""Fix SQL Server connection to include trust_server_certificate."""

import requests
import json

API_URL = "http://localhost:8000/api"

print("=" * 80)
print("Fixing SQL Server Connection")
print("=" * 80)

# Get SQL Server connection
print("\n1. Finding SQL Server connection...")
try:
    response = requests.get(f"{API_URL}/connections")
    if response.status_code == 200:
        connections = response.json()
        sql_conn = None
        for conn in connections:
            if conn.get('database_type') in ['sqlserver', 'mssql']:
                sql_conn = conn
                break
        
        if sql_conn:
            print(f"   [OK] Found connection: {sql_conn.get('name')} (ID: {sql_conn.get('id')})")
            conn_id = sql_conn.get('id')
            
            # Check current additional_config
            additional_config = sql_conn.get('additional_config', {})
            print(f"   Current additional_config: {additional_config}")
            
            # Update to include trust_server_certificate
            additional_config['trust_server_certificate'] = True
            additional_config['encrypt'] = False  # Disable encryption for self-signed certs
            
            print(f"\n2. Updating connection with trust_server_certificate=True...")
            update_data = {
                "name": sql_conn.get('name'),
                "database_type": sql_conn.get('database_type'),
                "host": sql_conn.get('host'),
                "port": sql_conn.get('port'),
                "database": sql_conn.get('database'),
                "username": sql_conn.get('username'),
                "password": sql_conn.get('password'),
                "schema": sql_conn.get('schema'),
                "additional_config": additional_config
            }
            
            update_response = requests.put(
                f"{API_URL}/connections/{conn_id}",
                json=update_data
            )
            
            if update_response.status_code == 200:
                print(f"   [OK] Connection updated")
                print(f"   New additional_config: {additional_config}")
            else:
                print(f"   [ERROR] Failed to update: {update_response.status_code}")
                print(f"   Response: {update_response.text[:300]}")
        else:
            print(f"   [ERROR] SQL Server connection not found")
    else:
        print(f"   [ERROR] Failed to get connections: {response.status_code}")
        
except Exception as e:
    print(f"   [ERROR] Exception: {e}")

print("\n" + "=" * 80)
print("Connection Update Complete!")
print("=" * 80)
print("\nNow restart the pipeline to use the updated connection settings.")


import requests
import json

API_URL = "http://localhost:8000/api"

print("=" * 80)
print("Fixing SQL Server Connection")
print("=" * 80)

# Get SQL Server connection
print("\n1. Finding SQL Server connection...")
try:
    response = requests.get(f"{API_URL}/connections")
    if response.status_code == 200:
        connections = response.json()
        sql_conn = None
        for conn in connections:
            if conn.get('database_type') in ['sqlserver', 'mssql']:
                sql_conn = conn
                break
        
        if sql_conn:
            print(f"   [OK] Found connection: {sql_conn.get('name')} (ID: {sql_conn.get('id')})")
            conn_id = sql_conn.get('id')
            
            # Check current additional_config
            additional_config = sql_conn.get('additional_config', {})
            print(f"   Current additional_config: {additional_config}")
            
            # Update to include trust_server_certificate
            additional_config['trust_server_certificate'] = True
            additional_config['encrypt'] = False  # Disable encryption for self-signed certs
            
            print(f"\n2. Updating connection with trust_server_certificate=True...")
            update_data = {
                "name": sql_conn.get('name'),
                "database_type": sql_conn.get('database_type'),
                "host": sql_conn.get('host'),
                "port": sql_conn.get('port'),
                "database": sql_conn.get('database'),
                "username": sql_conn.get('username'),
                "password": sql_conn.get('password'),
                "schema": sql_conn.get('schema'),
                "additional_config": additional_config
            }
            
            update_response = requests.put(
                f"{API_URL}/connections/{conn_id}",
                json=update_data
            )
            
            if update_response.status_code == 200:
                print(f"   [OK] Connection updated")
                print(f"   New additional_config: {additional_config}")
            else:
                print(f"   [ERROR] Failed to update: {update_response.status_code}")
                print(f"   Response: {update_response.text[:300]}")
        else:
            print(f"   [ERROR] SQL Server connection not found")
    else:
        print(f"   [ERROR] Failed to get connections: {response.status_code}")
        
except Exception as e:
    print(f"   [ERROR] Exception: {e}")

print("\n" + "=" * 80)
print("Connection Update Complete!")
print("=" * 80)
print("\nNow restart the pipeline to use the updated connection settings.")

