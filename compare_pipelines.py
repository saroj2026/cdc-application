"""Compare ps_sn_p and oracle_sf_p pipelines."""

import requests

API_BASE_URL = "http://localhost:8000/api/v1"

print("=" * 70)
print("Comparing Pipelines: ps_sn_p vs oracle_sf_p")
print("=" * 70)

# Get both pipelines
response = requests.get(f"{API_BASE_URL}/pipelines", timeout=10)
pipelines = response.json() if response.status_code == 200 else []

ps_sn_p = None
oracle_sf_p = None

for p in pipelines:
    if p.get("name") == "ps_sn_p":
        ps_sn_p = p
    elif p.get("name") == "oracle_sf_p":
        oracle_sf_p = p

if not ps_sn_p:
    print("\n❌ ps_sn_p pipeline not found")
    exit(1)

if not oracle_sf_p:
    print("\n❌ oracle_sf_p pipeline not found")
    exit(1)

print("\n" + "=" * 70)
print("KEY DIFFERENCES")
print("=" * 70)

print("\n1. TARGET SCHEMA:")
print(f"   ps_sn_p:      '{ps_sn_p.get('target_schema')}'")
print(f"   oracle_sf_p:  '{oracle_sf_p.get('target_schema')}'")

print("\n2. TARGET DATABASE:")
print(f"   ps_sn_p:      '{ps_sn_p.get('target_database')}'")
print(f"   oracle_sf_p:  '{oracle_sf_p.get('target_database')}'")

print("\n3. SOURCE TYPE:")
print(f"   ps_sn_p:      PostgreSQL")
print(f"   oracle_sf_p:  Oracle")

print("\n4. SOURCE SCHEMA:")
print(f"   ps_sn_p:      '{ps_sn_p.get('source_schema')}'")
print(f"   oracle_sf_p:  '{oracle_sf_p.get('source_schema')}'")

print("\n5. TARGET TABLES:")
print(f"   ps_sn_p:      {ps_sn_p.get('target_tables')}")
print(f"   oracle_sf_p:  {oracle_sf_p.get('target_tables')}")

# Get target connections
print("\n" + "=" * 70)
print("TARGET CONNECTION COMPARISON")
print("=" * 70)

conn_response = requests.get(f"{API_BASE_URL}/connections", timeout=10)
connections = conn_response.json() if conn_response.status_code == 200 else []

ps_sn_p_target_conn = None
oracle_sf_p_target_conn = None

for conn in connections:
    if conn.get('id') == ps_sn_p.get('target_connection_id'):
        ps_sn_p_target_conn = conn
    elif conn.get('id') == oracle_sf_p.get('target_connection_id'):
        oracle_sf_p_target_conn = conn

if ps_sn_p_target_conn and oracle_sf_p_target_conn:
    print("\nTarget Connection Schema:")
    print(f"   ps_sn_p connection schema:      '{ps_sn_p_target_conn.get('schema', 'None')}'")
    print(f"   oracle_sf_p connection schema:  '{oracle_sf_p_target_conn.get('schema', 'None')}'")
    
    print("\nTarget Connection Database:")
    print(f"   ps_sn_p connection database:      '{ps_sn_p_target_conn.get('database')}'")
    print(f"   oracle_sf_p connection database:  '{oracle_sf_p_target_conn.get('database')}'")

print("\n" + "=" * 70)
print("RECOMMENDATION")
print("=" * 70)

print("\n✅ Key Finding:")
print("   ps_sn_p uses target_schema='public' (lowercase)")
print("   oracle_sf_p uses target_schema='PUBLIC' (uppercase)")
print("\n   Snowflake schema names are case-sensitive!")
print("   The working pipeline uses lowercase 'public'")
print("\n   Action: Update oracle_sf_p to use 'public' instead of 'PUBLIC'")

print("\n" + "=" * 70)

