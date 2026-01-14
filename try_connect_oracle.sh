#!/bin/bash
# Script to try connecting to Oracle with different passwords

ORACLE_CONTAINER="oracle-xe"
SYSDBA_USER="sys"

echo "=== TRYING TO CONNECT TO ORACLE AS SYSDBA ==="
echo ""

# Common Oracle XE passwords to try
PASSWORDS=("oracle" "Oracle123" "Oradoc_db1" "manager" "password" "oracle123")

for pass in "${PASSWORDS[@]}"; do
    echo -n "Trying password: $pass ... "
    
    # Try to connect and execute a simple query
    result=$(echo "SELECT 1 FROM DUAL;" | docker exec -i $ORACLE_CONTAINER sqlplus -s $SYSDBA_USER/$pass@XE as sysdba 2>&1)
    
    if echo "$result" | grep -q "ORA-01017"; then
        echo "FAILED (invalid password)"
    elif echo "$result" | grep -q "ORA-"; then
        echo "FAILED (other error)"
        echo "$result" | head -3
    elif echo "$result" | grep -q "1"; then
        echo "SUCCESS!"
        echo ""
        echo "=========================================="
        echo "Password found: $pass"
        echo "=========================================="
        echo ""
        echo "Use this command to connect:"
        echo "  docker exec -it $ORACLE_CONTAINER sqlplus $SYSDBA_USER/$pass@XE as sysdba"
        echo ""
        echo "Or to grant permissions, run:"
        echo "  ORACLE_SYS_PASSWORD=$pass bash grant_oracle_permissions_with_password.sh"
        exit 0
    else
        echo "UNKNOWN (check output)"
        echo "$result" | head -3
    fi
done

echo ""
echo "Could not find correct password automatically."
echo ""
echo "Please:"
echo "1. Check Oracle documentation for the password"
echo "2. Check Docker container setup/environment variables"
echo "3. Try OS authentication: docker exec -it oracle-xe bash -> su - oracle -> sqlplus / as sysdba"
echo "4. Contact Oracle administrator for the SYSDBA password"

