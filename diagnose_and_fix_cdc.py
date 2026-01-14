#!/usr/bin/env python3
"""Diagnose and fix CDC issue by checking Oracle LogMiner and Debezium connector."""

import subprocess
import sys
import time

print("=" * 70)
print("DIAGNOSING AND FIXING CDC ISSUE")
print("=" * 70)

# Oracle credentials
ORACLE_USER = "c##cdc_user"
ORACLE_PASSWORD = "segmbp@1100"
ORACLE_SERVICE = "XE"

print("\n1. Checking Oracle LogMiner status...")

# SQL queries to check LogMiner
logminer_check_sql = """
SET PAGESIZE 1000
SET LINESIZE 200
SET FEEDBACK OFF

PROMPT === LogMiner Sessions ===
SELECT SESSION_ID, SESSION_NAME, SESSION_STATE, START_SCN, END_SCN, PROCESSED_SCN
FROM v$logmnr_session;

PROMPT === Archive Log Count ===
SELECT COUNT(*) as total_archive_logs,
       MAX(sequence#) as latest_sequence,
       MAX(next_change#) as latest_scn
FROM v$archived_log
WHERE status = 'A';

PROMPT === Current SCN ===
SELECT current_scn FROM v$database;

PROMPT === Test LogMiner - Start ===
EXECUTE DBMS_LOGMNR.START_LOGMNR(OPTIONS => DBMS_LOGMNR.DICT_FROM_ONLINE_CATALOG);

PROMPT === Check if LogMiner sees changes ===
SELECT COUNT(*) as change_count, 
       MIN(scn) as min_scn, 
       MAX(scn) as max_scn
FROM v$logmnr_contents
WHERE table_name = 'TEST'
AND owner_name = 'CDC_USER';

PROMPT === Stop LogMiner ===
EXECUTE DBMS_LOGMNR.END_LOGMNR;

EXIT;
"""

# Save SQL to temp file
import tempfile
import os

with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
    f.write(logminer_check_sql)
    sql_file = f.name

try:
    print("\n2. Running LogMiner diagnostics via SSH...")
    print("   (This will require SSH password: segmbp@1100)")
    
    # SSH command to run SQL
    ssh_cmd = f"""
    docker exec -i oracle-xe sqlplus -s / as sysdba < {sql_file}
    """
    
    # Note: We'll need to handle SSH password
    print("\n   Note: SSH password required. Running diagnostic...")
    
    # For now, provide the command to run
    print("\n" + "=" * 70)
    print("RUN THIS COMMAND ON THE SERVER:")
    print("=" * 70)
    print(f"ssh root@72.61.233.209")
    print("Password: segmbp@1100")
    print("Then run:")
    print(f"docker exec -i oracle-xe sqlplus -s / as sysdba < /tmp/logminer_check.sql")
    print("\nOr run these queries directly:")
    print("-" * 70)
    print(logminer_check_sql)
    print("-" * 70)
    
finally:
    if os.path.exists(sql_file):
        os.unlink(sql_file)

print("\n" + "=" * 70)
print("Next: Check Debezium connector logs")
print("=" * 70)

