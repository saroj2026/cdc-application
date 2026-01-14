#!/bin/bash
# Check Oracle LogMiner status via SSH

echo "Connecting to server and checking Oracle LogMiner status..."

ssh root@72.61.233.209 << 'ENDSSH'
echo "=== Checking Oracle LogMiner Status ==="

# Check if oracle-xe container exists
echo ""
echo "1. Checking Oracle container..."
docker ps --filter "name=oracle-xe" --format "{{.Names}}"

echo ""
echo "2. Checking LogMiner sessions..."
docker exec -i oracle-xe sqlplus -s / as sysdba << 'SQL'
SET PAGESIZE 1000
SET LINESIZE 200

-- Check LogMiner sessions
SELECT session_name, status, start_scn, end_scn 
FROM v$logmnr_session;

-- Check archive log status
SELECT sequence#, first_change#, next_change#, archived, status
FROM v$archived_log
WHERE status = 'A'
ORDER BY sequence# DESC
FETCH FIRST 10 ROWS ONLY;

-- Check current SCN
SELECT current_scn FROM v$database;

-- Check archive log mode
SELECT log_mode FROM v$database;

-- Check archive log destination
SHOW PARAMETER log_archive_dest;

EXIT;
SQL

echo ""
echo "3. Checking recent changes in cdc_user.test table..."
docker exec -i oracle-xe sqlplus -s c##cdc_user/segmbp@1100@XE << 'SQL'
SET PAGESIZE 1000
SELECT * FROM cdc_user.test ORDER BY ID DESC FETCH FIRST 5 ROWS ONLY;
EXIT;
SQL

ENDSSH

echo ""
echo "Done!"

