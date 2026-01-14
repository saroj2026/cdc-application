#!/bin/bash
# Directly fix CDC issue by checking everything

echo "=========================================="
echo "DIAGNOSING AND FIXING CDC ISSUE"
echo "=========================================="

# Check Oracle LogMiner
echo ""
echo "1. Checking Oracle LogMiner Status..."
docker exec -i oracle-xe sqlplus -s / as sysdba << 'ORACLE_SQL'
SET PAGESIZE 1000
SET FEEDBACK OFF

PROMPT === LogMiner Sessions ===
SELECT SESSION_ID, SESSION_NAME, SESSION_STATE, START_SCN, END_SCN, PROCESSED_SCN
FROM v$logmnr_session;

PROMPT === Archive Log Count ===
SELECT COUNT(*) as total_archive_logs,
       MAX(sequence#) as latest_sequence,
       MAX(next_change#) as latest_scn
FROM v$archived_log
WHERE status = 'A';

PROMPT === Current SCN ===
SELECT current_scn FROM v$database;

PROMPT === Test LogMiner ===
EXECUTE DBMS_LOGMNR.START_LOGMNR(OPTIONS => DBMS_LOGMNR.DICT_FROM_ONLINE_CATALOG);

SELECT COUNT(*) as change_count, MIN(scn) as min_scn, MAX(scn) as max_scn
FROM v$logmnr_contents
WHERE table_name = 'TEST' AND owner_name = 'CDC_USER';

EXECUTE DBMS_LOGMNR.END_LOGMNR;

EXIT;
ORACLE_SQL

# Check Debezium connector logs
echo ""
echo "2. Checking Debezium Connector Logs..."
KAFKA_CONNECT_CONTAINER=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1)
if [ ! -z "$KAFKA_CONNECT_CONTAINER" ]; then
    echo "Found Kafka Connect container: $KAFKA_CONNECT_CONTAINER"
    echo "Recent connector logs (last 50 lines with errors):"
    docker logs "$KAFKA_CONNECT_CONTAINER" 2>&1 | grep -i "oracle\|logminer\|error\|exception\|cdc" | tail -50
else
    echo "Kafka Connect container not found!"
fi

# Check connector status
echo ""
echo "3. Checking Connector Status via API..."
curl -s http://localhost:8083/connectors/cdc-oracle_sf_p-ora-cdc_user/status | python3 -m json.tool

echo ""
echo "=========================================="
echo "DIAGNOSIS COMPLETE"
echo "=========================================="

