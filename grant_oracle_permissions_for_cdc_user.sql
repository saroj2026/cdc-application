-- Oracle Permissions Script for Debezium Connector
-- Run this script as SYSDBA to grant all necessary permissions to c##cdc_user
-- This user is used to access cdc_user.test table

-- Connect as SYSDBA first:
-- sqlplus sys/password@XE as sysdba

-- ============================================
-- GRANT PERMISSIONS FOR C##CDC_USER
-- ============================================

-- 1. Basic privileges
GRANT CREATE SESSION TO c##cdc_user;
GRANT CONNECT TO c##cdc_user;
GRANT RESOURCE TO c##cdc_user;

-- 2. LogMiner privileges (required for CDC)
GRANT LOGMINING TO c##cdc_user;
GRANT SELECT ANY TRANSACTION TO c##cdc_user;
GRANT SELECT ANY DICTIONARY TO c##cdc_user;

-- 3. Flashback privileges (required for snapshots - this is the key one!)
GRANT FLASHBACK ANY TABLE TO c##cdc_user;

-- 4. Select privileges on the cdc_user schema tables
GRANT SELECT ON cdc_user.test TO c##cdc_user;

-- 5. Execute privileges on LogMiner packages (required for CDC)
GRANT EXECUTE ON SYS.DBMS_LOGMNR TO c##cdc_user;
GRANT EXECUTE ON SYS.DBMS_LOGMNR_D TO c##cdc_user;

-- 6. Additional privileges for CDC and metadata access
GRANT SELECT_CATALOG_ROLE TO c##cdc_user;

-- ============================================
-- VERIFY PERMISSIONS
-- ============================================

-- Check granted system privileges
SELECT PRIVILEGE, ADMIN_OPTION 
FROM DBA_SYS_PRIVS 
WHERE GRANTEE = 'C##CDC_USER'
ORDER BY PRIVILEGE;

-- Check granted table privileges
SELECT OWNER, TABLE_NAME, PRIVILEGE
FROM DBA_TAB_PRIVS
WHERE GRANTEE = 'C##CDC_USER'
ORDER BY OWNER, TABLE_NAME, PRIVILEGE;

-- Check granted roles
SELECT GRANTED_ROLE, ADMIN_OPTION, DEFAULT_ROLE
FROM DBA_ROLE_PRIVS
WHERE GRANTEE = 'C##CDC_USER'
ORDER BY GRANTED_ROLE;

-- ============================================
-- NOTES
-- ============================================
-- 1. FLASHBACK ANY TABLE is REQUIRED for Debezium snapshots (AS OF SCN queries)
-- 2. LOGMINING is REQUIRED for Oracle LogMiner-based CDC
-- 3. SELECT ANY DICTIONARY is needed for metadata queries
-- 4. SELECT_CATALOG_ROLE provides access to data dictionary views
-- 5. After granting permissions, restart the Debezium connector
-- 6. The user c##cdc_user accesses tables in the cdc_user schema

