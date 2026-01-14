-- Quick LogMiner Check (Run these one by one)
-- docker exec -it oracle-xe sqlplus / as sysdba

-- 1. Check LogMiner session columns first
DESC v$logmnr_session;

-- 2. Check LogMiner sessions (with correct columns)
SELECT session# as session_number, session_name, start_scn, end_scn
FROM v$logmnr_session;

-- 3. Check current SCN
SELECT current_scn FROM v$database;

-- 4. Check archive logs (last 5)
SELECT sequence#, first_change#, next_change#, archived
FROM v$archived_log
WHERE status = 'A'
ORDER BY sequence# DESC
FETCH FIRST 5 ROWS ONLY;

-- 5. Test LogMiner - can it see changes?
EXECUTE DBMS_LOGMNR.START_LOGMNR(OPTIONS => DBMS_LOGMNR.DICT_FROM_ONLINE_CATALOG);

SELECT COUNT(*) as change_count, 
       MIN(scn) as min_scn, 
       MAX(scn) as max_scn,
       table_name, 
       owner_name
FROM v$logmnr_contents
WHERE table_name = 'TEST'
AND owner_name = 'CDC_USER'
GROUP BY table_name, owner_name;

EXECUTE DBMS_LOGMNR.END_LOGMNR;

-- 6. Check recent data in table
SELECT * FROM cdc_user.test ORDER BY ID DESC FETCH FIRST 3 ROWS ONLY;

EXIT;

