-- Grant permissions to c##cdc_user on cdc_user.test table for CDC testing
-- Run this as SYSDBA: sqlplus sys/password@XE as sysdba

-- Grant SELECT, INSERT, UPDATE, DELETE on cdc_user.test to c##cdc_user
GRANT SELECT, INSERT, UPDATE, DELETE ON cdc_user.test TO c##cdc_user;

-- Verify permissions
SELECT grantee, table_name, privilege
FROM dba_tab_privs
WHERE owner = 'CDC_USER'
AND table_name = 'TEST'
AND grantee = 'C##CDC_USER'
ORDER BY privilege;

-- Exit
EXIT;

