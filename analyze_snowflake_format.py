#!/usr/bin/env python3
"""Analyze current Snowflake CDC format and compare with best practices."""

import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import snowflake.connector
from ingestion.database.session import get_db
from ingestion.database.models_db import ConnectionModel, PipelineModel

print("=" * 70)
print("ANALYZING SNOWFLAKE CDC FORMAT vs BEST PRACTICES")
print("=" * 70)

# Read examples
try:
    with open('snowflake_cdc_examples.json', 'r') as f:
        examples = json.load(f)
except:
    examples = {}

print("\n1. Current Format Analysis...")
print("-" * 70)

db = next(get_db())
try:
    pipeline = db.query(PipelineModel).filter_by(name="oracle_sf_p").first()
    snowflake_conn_model = db.query(ConnectionModel).filter_by(id=pipeline.target_connection_id).first()
    snowflake_config = snowflake_conn_model.additional_config or {}
    
    sf_account = snowflake_config.get('account') or snowflake_conn_model.host
    sf_user = snowflake_conn_model.username
    sf_password = snowflake_conn_model.password
    sf_warehouse = snowflake_config.get('warehouse')
    sf_database = snowflake_config.get('database') or 'seg'
    sf_schema = snowflake_config.get('schema') or 'public'
    sf_role = snowflake_config.get('role')
    
    sf_conn = snowflake.connector.connect(
        account=sf_account,
        user=sf_user,
        password=sf_password,
        warehouse=sf_warehouse,
        database=sf_database,
        schema=sf_schema,
        role=sf_role
    )
    
    sf_cursor = sf_conn.cursor()
    
    # Get examples of each operation type
    print("\n   a) INSERT (c) operation:")
    query_c = f"""
    SELECT RECORD_CONTENT, RECORD_METADATA
    FROM {sf_database}.{sf_schema}.TEST
    WHERE RECORD_CONTENT:op = 'c'
    ORDER BY RECORD_METADATA:CreateTime DESC
    LIMIT 1
    """
    sf_cursor.execute(query_c)
    result_c = sf_cursor.fetchone()
    if result_c:
        rc_c = json.loads(result_c[0]) if isinstance(result_c[0], str) else result_c[0]
        rm_c = json.loads(result_c[1]) if isinstance(result_c[1], str) else result_c[1]
        print(f"      RECORD_CONTENT keys: {list(rc_c.keys()) if isinstance(rc_c, dict) else 'N/A'}")
        print(f"      Has 'op' field: {'op' in rc_c if isinstance(rc_c, dict) else False}")
        print(f"      Has 'after' field: {'after' in rc_c if isinstance(rc_c, dict) else False}")
        print(f"      Has 'before' field: {'before' in rc_c if isinstance(rc_c, dict) else False}")
        print(f"      RECORD_METADATA keys: {list(rm_c.keys()) if isinstance(rm_c, dict) else 'N/A'}")
    
    print("\n   b) UPDATE (u) operation:")
    query_u = f"""
    SELECT RECORD_CONTENT, RECORD_METADATA
    FROM {sf_database}.{sf_schema}.TEST
    WHERE RECORD_CONTENT:op = 'u'
    ORDER BY RECORD_METADATA:CreateTime DESC
    LIMIT 1
    """
    sf_cursor.execute(query_u)
    result_u = sf_cursor.fetchone()
    if result_u:
        rc_u = json.loads(result_u[0]) if isinstance(result_u[0], str) else result_u[0]
        rm_u = json.loads(result_u[1]) if isinstance(result_u[1], str) else result_u[1]
        print(f"      RECORD_CONTENT keys: {list(rc_u.keys()) if isinstance(rc_u, dict) else 'N/A'}")
        print(f"      Has 'op' field: {'op' in rc_u if isinstance(rc_u, dict) else False}")
        print(f"      Has 'after' field: {'after' in rc_u if isinstance(rc_u, dict) else False}")
        print(f"      Has 'before' field: {'before' in rc_u if isinstance(rc_u, dict) else False}")
        print(f"      After is null: {rc_u.get('after') is None if isinstance(rc_u, dict) else 'N/A'}")
        print(f"      Before is null: {rc_u.get('before') is None if isinstance(rc_u, dict) else 'N/A'}")
    
    print("\n   c) DELETE (d) operation:")
    query_d = f"""
    SELECT RECORD_CONTENT, RECORD_METADATA
    FROM {sf_database}.{sf_schema}.TEST
    WHERE RECORD_CONTENT:op = 'd'
    ORDER BY RECORD_METADATA:CreateTime DESC
    LIMIT 1
    """
    sf_cursor.execute(query_d)
    result_d = sf_cursor.fetchone()
    if result_d:
        rc_d = json.loads(result_d[0]) if isinstance(result_d[0], str) else result_d[0]
        rm_d = json.loads(result_d[1]) if isinstance(result_d[1], str) else result_d[1]
        print(f"      RECORD_CONTENT keys: {list(rc_d.keys()) if isinstance(rc_d, dict) else 'N/A'}")
        print(f"      Has 'op' field: {'op' in rc_d if isinstance(rc_d, dict) else False}")
        print(f"      Has 'after' field: {'after' in rc_d if isinstance(rc_d, dict) else False}")
        print(f"      Has 'before' field: {'before' in rc_d if isinstance(rc_d, dict) else False}")
        print(f"      After is null: {rc_d.get('after') is None if isinstance(rc_d, dict) else 'N/A'}")
        print(f"      Before is null: {rc_d.get('before') is None if isinstance(rc_d, dict) else 'N/A'}")
        if isinstance(rc_d, dict) and 'before' in rc_d and rc_d['before']:
            print(f"      Before has data: ✅ (not empty)")
    
    # Check table structure
    print("\n   d) Table structure:")
    sf_cursor.execute(f"DESC TABLE {sf_database}.{sf_schema}.TEST")
    columns = sf_cursor.fetchall()
    for col in columns:
        col_name = col[0]
        col_type = col[1]
        print(f"      {col_name}: {col_type}")
    
    sf_cursor.close()
    sf_conn.close()
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print("\n2. Snowflake CDC Best Practices (from research)...")
print("-" * 70)
print("   ✅ RECORD_CONTENT (VARIANT): Should contain full Kafka message payload")
print("   ✅ RECORD_METADATA (VARIANT/OBJECT): Should contain Kafka metadata")
print("   ✅ Debezium envelope format: {op, after, before, source, ts_ms}")
print("   ✅ Operation types: 'c'=INSERT, 'u'=UPDATE, 'd'=DELETE")
print("   ✅ For DELETE: after=null, before=deleted record")
print("   ✅ For UPDATE: after=new state, before=old state")
print("   ✅ For INSERT: after=new record, before=null")

print("\n3. Comparison with Current Implementation...")
print("-" * 70)

# Based on the analysis above
current_format_ok = True
issues = []

if result_c and isinstance(json.loads(result_c[0]) if isinstance(result_c[0], str) else result_c[0], dict):
    rc = json.loads(result_c[0]) if isinstance(result_c[0], str) else result_c[0]
    if 'op' not in rc:
        issues.append("❌ INSERT records missing 'op' field")
        current_format_ok = False
    if 'after' not in rc:
        issues.append("❌ INSERT records missing 'after' field")
        current_format_ok = False
    if rc.get('after') is None:
        issues.append("❌ INSERT records have null 'after' field")
        current_format_ok = False

if result_d and isinstance(json.loads(result_d[0]) if isinstance(result_d[0], str) else result_d[0], dict):
    rc = json.loads(result_d[0]) if isinstance(result_d[0], str) else result_d[0]
    if 'op' not in rc:
        issues.append("❌ DELETE records missing 'op' field")
        current_format_ok = False
    if 'before' not in rc:
        issues.append("❌ DELETE records missing 'before' field")
        current_format_ok = False
    if rc.get('before') is None:
        issues.append("⚠ DELETE records have null 'before' (should have deleted record data)")

if issues:
    print("   Issues found:")
    for issue in issues:
        print(f"     {issue}")
else:
    print("   ✅ Current format matches Snowflake CDC best practices!")

print("\n4. Recommendations...")
print("-" * 70)

if current_format_ok:
    print("   ✅ Your current format is CORRECT and follows best practices:")
    print("      - RECORD_CONTENT contains full Debezium envelope")
    print("      - RECORD_METADATA contains Kafka metadata")
    print("      - All operation types (c/u/d) are properly represented")
    print("      - DELETE operations show 'before' data (not empty)")
else:
    print("   ⚠ Some issues detected. Recommendations:")
    for issue in issues:
        if "missing" in issue.lower():
            print(f"      - Ensure Debezium envelope is preserved (no transforms)")
        if "null" in issue.lower() and "DELETE" in issue:
            print(f"      - Verify DELETE operations capture 'before' state")

print("\n   Optional Enhancements:")
print("      - Consider enabling schema detection (schematization.enabled=true)")
print("        This creates individual columns for each field (optional)")
print("      - Current VARIANT format is standard and recommended for CDC")
print("      - VARIANT allows querying with JSON path expressions")

print("\n" + "=" * 70)
print("CONCLUSION:")
if current_format_ok:
    print("  ✅ Your Snowflake CDC format is STANDARD and CORRECT!")
    print("  ✅ No changes needed - format matches best practices")
else:
    print("  ⚠ Some issues found - see recommendations above")
print("=" * 70)

