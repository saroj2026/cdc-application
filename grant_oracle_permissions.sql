-- Oracle Permissions Script for Debezium Connector
-- Run this script as SYSDBA to grant all necessary permissions

-- Connect as SYSDBA first:
-- sqlplus sys/password@XE as sysdba

-- ============================================
-- GRANT PERMISSIONS FOR CDC_USER
-- ============================================

-- 1. Basic privileges
GRANT CREATE SESSION TO cdc_user;
GRANT CONNECT TO cdc_user;
GRANT RESOURCE TO cdc_user;

-- 2. LogMiner privileges (required for CDC)
GRANT LOGMINING TO cdc_user;
GRANT SELECT ANY TRANSACTION TO cdc_user;
GRANT SELECT ANY DICTIONARY TO cdc_user;

-- 3. Flashback privileges (required for snapshots)
GRANT FLASHBACK ANY TABLE TO cdc_user;

-- 4. Select privileges on the schema
GRANT SELECT ON cdc_user.test TO cdc_user;
-- Or grant on all tables in schema
-- GRANT SELECT ANY TABLE TO cdc_user;

-- 5. Execute privileges (may be needed)
GRANT EXECUTE ON SYS.DBMS_LOGMNR TO cdc_user;
GRANT EXECUTE ON SYS.DBMS_LOGMNR_D TO cdc_user;

-- 6. Additional privileges for CDC
GRANT SELECT_CATALOG_ROLE TO cdc_user;

-- ============================================
-- GRANT PERMISSIONS FOR C##CDC_USER (if using)
-- ============================================

-- If using c##cdc_user (common user in CDB), grant similar privileges:
GRANT CREATE SESSION TO c##cdc_user;
GRANT CONNECT TO c##cdc_user;
GRANT RESOURCE TO c##cdc_user;
GRANT LOGMINING TO c##cdc_user;
GRANT SELECT ANY TRANSACTION TO c##cdc_user;
GRANT SELECT ANY DICTIONARY TO c##cdc_user;
GRANT FLASHBACK ANY TABLE TO c##cdc_user;
GRANT SELECT_CATALOG_ROLE TO c##cdc_user;

-- Grant execute privileges
GRANT EXECUTE ON SYS.DBMS_LOGMNR TO c##cdc_user;
GRANT EXECUTE ON SYS.DBMS_LOGMNR_D TO c##cdc_user;

-- Grant select on tables in CDC_USER schema
GRANT SELECT ON cdc_user.test TO c##cdc_user;

-- ============================================
-- VERIFY PERMISSIONS
-- ============================================

-- Check granted privileges
SELECT * FROM DBA_SYS_PRIVS WHERE GRANTEE IN ('CDC_USER', 'C##CDC_USER');
SELECT * FROM DBA_TAB_PRIVS WHERE GRANTEE IN ('CDC_USER', 'C##CDC_USER');

-- ============================================
-- NOTES
-- ============================================
-- 1. FLASHBACK ANY TABLE is required for Debezium snapshots
-- 2. LOGMINING is required for Oracle LogMiner-based CDC
-- 3. SELECT ANY DICTIONARY is needed for metadata queries
-- 4. SELECT_CATALOG_ROLE provides access to data dictionary views
-- 5. After granting permissions, restart the Debezium connector

