-- Corrected LogMiner Queries (Run these one at a time)
-- Copy and paste each query separately

-- Query 1: Check LogMiner Sessions
SELECT SESSION_ID, SESSION_NAME, SESSION_STATE, START_SCN, END_SCN, PROCESSED_SCN
FROM v$logmnr_session;

-- Query 2: Check Current SCN (you already ran this - it's 17888363)
SELECT current_scn FROM v$database;

-- Query 3: Check Archive Logs (with proper line breaks)
SELECT sequence#, first_change#, next_change#, archived
FROM v$archived_log
WHERE status = 'A'
ORDER BY sequence# DESC
FETCH FIRST 5 ROWS ONLY;

-- Query 4: Check if archive logs exist
SELECT COUNT(*) as total_archive_logs,
       MAX(sequence#) as latest_sequence,
       MAX(next_change#) as latest_scn
FROM v$archived_log
WHERE status = 'A';

-- Query 5: Test LogMiner - Start session
EXECUTE DBMS_LOGMNR.START_LOGMNR(OPTIONS => DBMS_LOGMNR.DICT_FROM_ONLINE_CATALOG);

-- Query 6: Check if LogMiner can see changes in cdc_user.test
SELECT COUNT(*) as change_count, 
       MIN(scn) as min_scn, 
       MAX(scn) as max_scn,
       table_name, 
       owner_name
FROM v$logmnr_contents
WHERE table_name = 'TEST'
AND owner_name = 'CDC_USER'
GROUP BY table_name, owner_name;

-- Query 7: See actual changes
SELECT sql_redo, scn, timestamp, table_name, owner_name
FROM v$logmnr_contents
WHERE table_name = 'TEST'
AND owner_name = 'CDC_USER'
ORDER BY scn DESC
FETCH FIRST 10 ROWS ONLY;

-- Query 8: Stop LogMiner
EXECUTE DBMS_LOGMNR.END_LOGMNR;

-- Query 9: Check recent data in table
SELECT * FROM cdc_user.test ORDER BY ID DESC FETCH FIRST 3 ROWS ONLY;

EXIT;

