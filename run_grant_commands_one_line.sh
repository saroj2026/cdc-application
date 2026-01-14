#!/bin/bash
# Run all GRANT commands at once - use this from VPS host (not inside container)

echo "Granting Oracle permissions to c##cdc_user..."
echo ""

docker exec -i oracle-xe sqlplus / as sysdba <<EOF
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
EXIT;
EOF

echo ""
echo "Permissions granted!"
echo ""
echo "Next step: Restart the Debezium connector"

