#!/usr/bin/env python3
"""Grant permissions to c##cdc_user on cdc_user.test table via SSH."""

import subprocess
import sys

print("=" * 70)
print("GRANTING PERMISSIONS VIA SSH")
print("=" * 70)

ssh_host = "root@72.61.233.209"
ssh_password = "segmbp@1100"

# SQL command to grant permissions
sql_commands = """
GRANT SELECT, INSERT, UPDATE, DELETE ON cdc_user.test TO c##cdc_user;

SELECT grantee, table_name, privilege
FROM dba_tab_privs
WHERE owner = 'CDC_USER'
AND table_name = 'TEST'
AND grantee = 'C##CDC_USER'
ORDER BY privilege;
"""

print("\n1. Finding Oracle container...")
# SSH command to find Oracle container and grant permissions
ssh_command = f"""
ORACLE_CONTAINER=$(docker ps --filter "name=oracle" --format "{{{{.Names}}}}" | head -1)
if [ -z "$ORACLE_CONTAINER" ]; then
    echo "Oracle container not found!"
    exit 1
fi
echo "Found Oracle container: $ORACLE_CONTAINER"
docker exec -i $ORACLE_CONTAINER sqlplus -s sys/segmbp@1100@XE as sysdba << 'SQL'
{sql_commands}
EXIT;
SQL
"""

print("\n2. Connecting to SSH and granting permissions...")
print("   (You may need to enter SSH password: segmbp@1100)")

# Use sshpass if available, otherwise prompt
try:
    # Try with sshpass
    result = subprocess.run(
        f"sshpass -p '{ssh_password}' ssh -o StrictHostKeyChecking=no {ssh_host} '{ssh_command}'",
        shell=True,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    print("\n3. Output:")
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)
    
    if result.returncode == 0:
        print("\n✓✓✓ Permissions granted successfully!")
    else:
        print(f"\n✗ Command failed with return code: {result.returncode}")
        print("\nTrying without sshpass (will prompt for password)...")
        
        # Try without sshpass
        result = subprocess.run(
            f"ssh -o StrictHostKeyChecking=no {ssh_host} '{ssh_command}'",
            shell=True,
            text=True,
            timeout=30
        )
        
        print("\nOutput:")
        print(result.stdout if hasattr(result, 'stdout') else "No output")
        
except subprocess.TimeoutExpired:
    print("✗ SSH command timed out")
except Exception as e:
    print(f"✗ Error: {e}")
    print("\nPlease run this manually:")
    print(f"ssh {ssh_host}")
    print("Then run:")
    print("ORACLE_CONTAINER=$(docker ps --filter 'name=oracle' --format '{{.Names}}' | head -1)")
    print("docker exec -i $ORACLE_CONTAINER sqlplus -s sys/segmbp@1100@XE as sysdba")
    print("GRANT SELECT, INSERT, UPDATE, DELETE ON cdc_user.test TO c##cdc_user;")
    print("EXIT;")

print("\n" + "=" * 70)

