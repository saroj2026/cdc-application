#!/bin/bash
# Script to check Oracle container configuration and find credentials

echo "=== CHECKING ORACLE CONTAINER CONFIGURATION ==="
echo ""

# Check if Oracle container is running
ORACLE_CONTAINER="oracle-xe"
if ! docker ps | grep -q "$ORACLE_CONTAINER"; then
    echo "ERROR: Oracle container '$ORACLE_CONTAINER' is not running!"
    exit 1
fi

echo "Oracle container: $ORACLE_CONTAINER"
echo ""

# Check environment variables (might contain password info)
echo "=== ENVIRONMENT VARIABLES ==="
docker inspect $ORACLE_CONTAINER --format '{{range .Config.Env}}{{println .}}{{end}}' | grep -iE "PASSWORD|ORACLE|SYS" || echo "No password-related env vars found"
echo ""

# Check if we can connect with different common passwords
echo "=== TRYING COMMON ORACLE XE PASSWORDS ==="
echo "Trying different SYSDBA passwords..."
echo ""

COMMON_PASSWORDS=("oracle" "Oracle123" "Oradoc_db1" "manager" "sys" "password")

for pass in "${COMMON_PASSWORDS[@]}"; do
    echo -n "Trying password: $pass ... "
    if echo "SELECT 1 FROM DUAL;" | docker exec -i $ORACLE_CONTAINER sqlplus sys/$pass@XE as sysdba 2>&1 | grep -q "ORA-01017"; then
        echo "FAILED"
    else
        echo "SUCCESS! Password is: $pass"
        echo ""
        echo "Use this command to connect:"
        echo "docker exec -it $ORACLE_CONTAINER sqlplus sys/$pass@XE as sysdba"
        exit 0
    fi
done

echo ""
echo "Could not find correct password automatically."
echo ""
echo "=== ALTERNATIVE: Connect as regular user and check ==="
echo "Try connecting as the cdc_user to check if it works:"
echo "docker exec -it $ORACLE_CONTAINER sqlplus c##cdc_user/cdc_user@XE"
echo ""
echo "Or check Oracle documentation for default XE passwords"

