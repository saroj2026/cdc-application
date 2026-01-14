"""Wait for Kafka Connect to be ready."""

import requests
import time

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

print("Waiting for Kafka Connect to be ready...")
print(f"URL: {KAFKA_CONNECT_URL}\n")

max_wait = 120  # 2 minutes
waited = 0
ready = False

while waited < max_wait and not ready:
    try:
        response = requests.get(f"{KAFKA_CONNECT_URL}/", timeout=5)
        if response.status_code == 200:
            print(f"✅ Kafka Connect is accessible! (after {waited} seconds)")
            ready = True
            
            # Check for Debezium connector
            try:
                plugins_response = requests.get(f"{KAFKA_CONNECT_URL}/connector-plugins", timeout=10)
                if plugins_response.status_code == 200:
                    plugins = plugins_response.json()
                    pg_connector = [p for p in plugins if 'PostgresConnector' in p.get('class', '')]
                    if pg_connector:
                        print(f"✅ Debezium PostgreSQL connector found!")
                        print(f"   Class: {pg_connector[0].get('class')}")
                        print(f"   Version: {pg_connector[0].get('version', 'N/A')}")
                    else:
                        print("⚠️  Debezium PostgreSQL connector not found in plugins")
            except Exception as e:
                print(f"⚠️  Could not check plugins: {e}")
        else:
            print(f"   Waiting... ({waited}/{max_wait} seconds) - Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"   Waiting... ({waited}/{max_wait} seconds) - Connection refused")
    except Exception as e:
        print(f"   Waiting... ({waited}/{max_wait} seconds) - Error: {str(e)[:50]}")
    
    if not ready:
        time.sleep(5)
        waited += 5

if not ready:
    print(f"\n❌ Kafka Connect not ready after {max_wait} seconds")
    print("   Please check if Kafka Connect is running on the VPS")
else:
    print("\n✅ Ready to start pipeline!")


import requests
import time

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

print("Waiting for Kafka Connect to be ready...")
print(f"URL: {KAFKA_CONNECT_URL}\n")

max_wait = 120  # 2 minutes
waited = 0
ready = False

while waited < max_wait and not ready:
    try:
        response = requests.get(f"{KAFKA_CONNECT_URL}/", timeout=5)
        if response.status_code == 200:
            print(f"✅ Kafka Connect is accessible! (after {waited} seconds)")
            ready = True
            
            # Check for Debezium connector
            try:
                plugins_response = requests.get(f"{KAFKA_CONNECT_URL}/connector-plugins", timeout=10)
                if plugins_response.status_code == 200:
                    plugins = plugins_response.json()
                    pg_connector = [p for p in plugins if 'PostgresConnector' in p.get('class', '')]
                    if pg_connector:
                        print(f"✅ Debezium PostgreSQL connector found!")
                        print(f"   Class: {pg_connector[0].get('class')}")
                        print(f"   Version: {pg_connector[0].get('version', 'N/A')}")
                    else:
                        print("⚠️  Debezium PostgreSQL connector not found in plugins")
            except Exception as e:
                print(f"⚠️  Could not check plugins: {e}")
        else:
            print(f"   Waiting... ({waited}/{max_wait} seconds) - Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"   Waiting... ({waited}/{max_wait} seconds) - Connection refused")
    except Exception as e:
        print(f"   Waiting... ({waited}/{max_wait} seconds) - Error: {str(e)[:50]}")
    
    if not ready:
        time.sleep(5)
        waited += 5

if not ready:
    print(f"\n❌ Kafka Connect not ready after {max_wait} seconds")
    print("   Please check if Kafka Connect is running on the VPS")
else:
    print("\n✅ Ready to start pipeline!")

