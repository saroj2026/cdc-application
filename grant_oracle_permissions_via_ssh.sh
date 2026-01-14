#!/bin/bash
# Grant permissions to c##cdc_user on cdc_user.test table via SSH

echo "Granting permissions to c##cdc_user on cdc_user.test table..."

# Connect to Oracle container and grant permissions
ssh root@72.61.233.209 << 'EOF'
# Find Oracle container
ORACLE_CONTAINER=$(docker ps --filter "name=oracle" --format "{{.Names}}" | head -1)
if [ -z "$ORACLE_CONTAINER" ]; then
    echo "Oracle container not found!"
    exit 1
fi

echo "Found Oracle container: $ORACLE_CONTAINER"

# Grant permissions via SQL*Plus
docker exec -i $ORACLE_CONTAINER sqlplus sys/segmbp@1100@XE as sysdba << 'SQL'
GRANT SELECT, INSERT, UPDATE, DELETE ON cdc_user.test TO c##cdc_user;

-- Verify permissions
SELECT grantee, table_name, privilege
FROM dba_tab_privs
WHERE owner = 'CDC_USER'
AND table_name = 'TEST'
AND grantee = 'C##CDC_USER'
ORDER BY privilege;

EXIT;
SQL

echo "Permissions granted successfully!"
EOF

echo "Done!"

