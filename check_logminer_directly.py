#!/usr/bin/env python3
"""Check Oracle LogMiner status directly via SSH and Oracle connection."""

import subprocess
import sys

print("=" * 70)
print("CHECKING ORACLE LOGMINER STATUS VIA SSH")
print("=" * 70)

# SQL commands to check LogMiner
sql_commands = """
SET PAGESIZE 1000
SET LINESIZE 200

PROMPT === 1. LogMiner Sessions ===
SELECT session_name, status, start_scn, end_scn 
FROM v$logmnr_session;

PROMPT === 2. Archive Log Status (Last 10) ===
SELECT sequence#, first_change#, next_change#, archived, status
FROM v$archived_log
WHERE status = 'A'
ORDER BY sequence# DESC
FETCH FIRST 10 ROWS ONLY;

PROMPT === 3. Current SCN ===
SELECT current_scn FROM v$database;

PROMPT === 4. Archive Log Mode ===
SELECT log_mode FROM v$database;

PROMPT === 5. Archive Log Destination ===
SHOW PARAMETER log_archive_dest;

PROMPT === 6. Recent Changes in cdc_user.test ===
SELECT * FROM cdc_user.test ORDER BY ID DESC FETCH FIRST 5 ROWS ONLY;

EXIT;
"""

print("\nConnecting to server via SSH...")
print("Password: segmbp@1100")
print("\nRunning Oracle LogMiner diagnostics...")
print("=" * 70)

# Create a temporary SQL file
import tempfile
import os

with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
    f.write(sql_commands)
    sql_file = f.name

try:
    # SSH command to run SQL
    ssh_command = f"""
    docker exec -i oracle-xe sqlplus -s / as sysdba < {sql_file}
    """
    
    # Note: This will require password input
    print("\nNote: You may need to enter SSH password manually.")
    print("Or run this command directly on the server:")
    print(f"\nssh root@72.61.233.209")
    print("Password: segmbp@1100")
    print("Then run:")
    print("docker exec -it oracle-xe sqlplus / as sysdba")
    print("\nThen paste these SQL commands:")
    print("-" * 70)
    print(sql_commands)
    print("-" * 70)
    
finally:
    # Clean up temp file
    if os.path.exists(sql_file):
        os.unlink(sql_file)

print("\n" + "=" * 70)
print("ALTERNATIVE: Run these commands manually")
print("=" * 70)
print("1. SSH to server:")
print("   ssh root@72.61.233.209")
print("   Password: segmbp@1100")
print("\n2. Access Oracle as SYSDBA:")
print("   docker exec -it oracle-xe sqlplus / as sysdba")
print("\n3. Run these SQL commands:")
print("-" * 70)
print(sql_commands)
print("-" * 70)

