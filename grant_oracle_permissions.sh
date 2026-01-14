#!/bin/bash
# Script to grant Oracle permissions to c##cdc_user
# Run this on the VPS server where Oracle container is running

echo "=========================================="
echo "Granting Oracle Permissions to c##cdc_user"
echo "=========================================="
echo ""

# Oracle container name
ORACLE_CONTAINER="oracle-xe"
SYSDBA_USER="sys"
SYSDBA_PASSWORD="oracle"  # Default Oracle XE password

echo "Oracle Container: $ORACLE_CONTAINER"
echo "SYSDBA User: $SYSDBA_USER"
echo ""

# Check if container is running
if ! docker ps | grep -q "$ORACLE_CONTAINER"; then
    echo "ERROR: Oracle container '$ORACLE_CONTAINER' is not running!"
    echo "Please start the Oracle container first."
    exit 1
fi

echo "Connecting to Oracle as SYSDBA..."
echo ""

# Create SQL script
SQL_COMMANDS=$(cat <<'EOF'
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
SELECT PRIVILEGE FROM DBA_SYS_PRIVS WHERE GRANTEE = 'C##CDC_USER' ORDER BY PRIVILEGE;
SELECT GRANTED_ROLE FROM DBA_ROLE_PRIVS WHERE GRANTEE = 'C##CDC_USER' ORDER BY GRANTED_ROLE;
SELECT OWNER, TABLE_NAME, PRIVILEGE FROM DBA_TAB_PRIVS WHERE GRANTEE = 'C##CDC_USER';
EXIT;
EOF
)

# Execute SQL commands
echo "$SQL_COMMANDS" | docker exec -i $ORACLE_CONTAINER sqlplus $SYSDBA_USER/$SYSDBA_PASSWORD@XE as sysdba

echo ""
echo "=========================================="
echo "Permissions granted!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Restart the Debezium connector"
echo "2. The connector should now be able to perform snapshots"
echo "3. The topic will be created automatically"

