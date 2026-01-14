#!/bin/bash
# Script to grant Oracle permissions - prompts for password if needed

ORACLE_CONTAINER="oracle-xe"
SYSDBA_USER="sys"

echo "=========================================="
echo "Grant Oracle Permissions to c##cdc_user"
echo "=========================================="
echo ""

# Check if container is running
if ! docker ps | grep -q "$ORACLE_CONTAINER"; then
    echo "ERROR: Oracle container '$ORACLE_CONTAINER' is not running!"
    exit 1
fi

# Try to get password from user or use default
if [ -z "$ORACLE_SYS_PASSWORD" ]; then
    echo "Enter Oracle SYSDBA password (default: oracle):"
    read -s ORACLE_SYS_PASSWORD
    ORACLE_SYS_PASSWORD=${ORACLE_SYS_PASSWORD:-oracle}
fi

echo ""
echo "Connecting to Oracle as SYSDBA..."
echo ""

# Test connection first
if echo "SELECT 1 FROM DUAL;" | docker exec -i $ORACLE_CONTAINER sqlplus $SYSDBA_USER/$ORACLE_SYS_PASSWORD@XE as sysdba 2>&1 | grep -q "ORA-01017"; then
    echo "ERROR: Invalid password! Cannot connect as SYSDBA."
    echo ""
    echo "Please provide the correct SYSDBA password."
    echo "Oracle XE default passwords might be:"
    echo "  - oracle"
    echo "  - Oracle123"
    echo "  - Oradoc_db1"
    echo "  - (password set during installation)"
    echo ""
    echo "You can also try connecting manually to test:"
    echo "  docker exec -it $ORACLE_CONTAINER sqlplus $SYSDBA_USER/<password>@XE as sysdba"
    exit 1
fi

echo "Connection successful!"
echo ""

# Grant permissions
SQL_COMMANDS=$(cat <<EOF
-- Grant all necessary permissions to c##cdc_user
GRANT CREATE SESSION TO c##cdc_user;
GRANT CONNECT TO c##cdc_user;
GRANT RESOURCE TO c##cdc_user;
GRANT LOGMINING TO c##cdc_user;
GRANT SELECT ANY TRANSACTION TO c##cdc_user;
GRANT SELECT ANY DICTIONARY TO c##cdc_user;
GRANT FLASHBACK ANY TABLE TO c##cdc_user;
GRANT SELECT ON cdc_user.test TO c##cdc_user;
GRANT EXECUTE ON SYS.DBMS_LOGMNR TO c##cdc_user;
GRANT EXECUTE ON SYS.DBMS_LOGMNR_D TO c##cdc_user;
GRANT SELECT_CATALOG_ROLE TO c##cdc_user;

-- Verify permissions
SELECT 'System Privileges:' FROM DUAL;
SELECT PRIVILEGE FROM DBA_SYS_PRIVS WHERE GRANTEE = 'C##CDC_USER' ORDER BY PRIVILEGE;
SELECT 'Roles:' FROM DUAL;
SELECT GRANTED_ROLE FROM DBA_ROLE_PRIVS WHERE GRANTEE = 'C##CDC_USER' ORDER BY GRANTED_ROLE;
SELECT 'Table Privileges:' FROM DUAL;
SELECT OWNER, TABLE_NAME, PRIVILEGE FROM DBA_TAB_PRIVS WHERE GRANTEE = 'C##CDC_USER';
EXIT;
EOF
)

echo "Granting permissions..."
echo ""

echo "$SQL_COMMANDS" | docker exec -i $ORACLE_CONTAINER sqlplus $SYSDBA_USER/$ORACLE_SYS_PASSWORD@XE as sysdba

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓ Permissions granted successfully!"
    echo "=========================================="
else
    echo ""
    echo "ERROR: Failed to grant permissions"
    exit 1
fi

