-- Oracle LogMiner Diagnostic Queries (Fixed)
-- Run this as SYSDBA: docker exec -it oracle-xe sqlplus / as sysdba

SET PAGESIZE 1000
SET LINESIZE 200

PROMPT ========================================
PROMPT 1. LogMiner Sessions (Corrected Query)
PROMPT ========================================
-- Check what columns are available first
DESC v$logmnr_session;

-- Then query with correct columns
SELECT session# as session_number, 
       session_name, 
       db_id,
       start_scn, 
       end_scn,
       flags
FROM v$logmnr_session;

PROMPT ========================================
PROMPT 2. Archive Log Status (Last 10)
PROMPT ========================================
SELECT sequence#, first_change#, next_change#, archived, status, name
FROM v$archived_log
WHERE status = 'A'
ORDER BY sequence# DESC
FETCH FIRST 10 ROWS ONLY;

PROMPT ========================================
PROMPT 3. Current SCN (System Change Number)
PROMPT ========================================
SELECT current_scn FROM v$database;

PROMPT ========================================
PROMPT 4. Archive Log Mode
PROMPT ========================================
SELECT log_mode FROM v$database;

PROMPT ========================================
PROMPT 5. Archive Log Destination
PROMPT ========================================
SHOW PARAMETER log_archive_dest;

PROMPT ========================================
PROMPT 6. Archive Log Destination Status
PROMPT ========================================
SELECT destination, status, error FROM v$archive_dest WHERE status != 'INACTIVE';

PROMPT ========================================
PROMPT 7. Recent Changes in cdc_user.test
PROMPT ========================================
SELECT * FROM cdc_user.test ORDER BY ID DESC FETCH FIRST 5 ROWS ONLY;

PROMPT ========================================
PROMPT 8. Check Redo Log Status
PROMPT ========================================
SELECT group#, sequence#, bytes, status, first_change#, next_change#
FROM v$log
ORDER BY group#;

PROMPT ========================================
PROMPT 9. Check if archive logs are being generated
PROMPT ========================================
SELECT COUNT(*) as total_archive_logs,
       MAX(sequence#) as latest_sequence,
       MIN(first_change#) as oldest_scn,
       MAX(next_change#) as latest_scn
FROM v$archived_log
WHERE status = 'A';

PROMPT ========================================
PROMPT 10. Test LogMiner - Check if we can see recent changes
PROMPT ========================================
-- Start LogMiner session
EXECUTE DBMS_LOGMNR.START_LOGMNR(OPTIONS => DBMS_LOGMNR.DICT_FROM_ONLINE_CATALOG);

-- Check if changes are visible
SELECT sql_redo, sql_undo, scn, timestamp, table_name, owner_name
FROM v$logmnr_contents
WHERE table_name = 'TEST'
AND owner_name = 'CDC_USER'
ORDER BY scn DESC
FETCH FIRST 10 ROWS ONLY;

-- Stop LogMiner
EXECUTE DBMS_LOGMNR.END_LOGMNR;

PROMPT ========================================
PROMPT 11. Check Debezium User Permissions
PROMPT ========================================
SELECT grantee, privilege, admin_option
FROM dba_sys_privs
WHERE grantee = 'C##CDC_USER'
ORDER BY privilege;

PROMPT ========================================
PROMPT 12. Check Table Permissions
PROMPT ========================================
SELECT grantee, table_name, privilege
FROM dba_tab_privs
WHERE owner = 'CDC_USER'
AND table_name = 'TEST'
ORDER BY grantee, privilege;

EXIT;

