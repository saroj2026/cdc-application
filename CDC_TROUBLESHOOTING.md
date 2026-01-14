# CDC Troubleshooting Guide

## Current Status

✅ **Fixed:**
- Connector configuration: `cdc_user.test` (without `##`)
- Connector status: RUNNING
- Permissions: SELECT, INSERT, UPDATE, DELETE granted
- Archive logs: Enabled (ARCHIVELOG mode)
- Oracle table: `cdc_user.test` exists with 3 rows

❌ **Issue:**
- CDC changes (INSERT/UPDATE/DELETE) are NOT being captured
- Kafka topic still has only 3 messages (snapshot data)
- Connector topics API returns empty list

## Diagnosis

The connector is RUNNING but not capturing CDC changes. This suggests a **LogMiner configuration or session issue**.

## Next Steps to Diagnose

### 1. Check Debezium Connector Logs

SSH to the server and check connector logs:

```bash
ssh root@72.61.233.209
Password: segmbp@1100

# Find Kafka Connect container
docker ps --filter "name=kafka-connect" --format "{{.Names}}"

# Check connector logs (replace CONTAINER_NAME)
docker logs CONTAINER_NAME 2>&1 | grep -i "oracle\|cdc\|logminer\|error\|exception" | tail -100

# Check for LogMiner-specific errors
docker logs CONTAINER_NAME 2>&1 | grep -i "logminer\|archive\|scn\|session" | tail -50
```

### 2. Check Oracle LogMiner Status

Connect to Oracle and check LogMiner session:

```bash
# Find Oracle container
ORACLE_CONTAINER=$(docker ps --filter "name=oracle" --format "{{.Names}}" | head -1)

# Connect to Oracle
docker exec -it $ORACLE_CONTAINER sqlplus sys/segmbp@1100@XE as sysdba

# Check LogMiner sessions
SELECT session_name, status, start_scn, end_scn 
FROM v$logmnr_session;

# Check archive log status
SELECT sequence#, first_change#, next_change#, archived, status
FROM v$archived_log
WHERE status = 'A'
ORDER BY sequence# DESC
FETCH FIRST 10 ROWS ONLY;

# Check if archive logs are being generated
SELECT log_mode FROM v$database;
```

### 3. Verify Table is Being Monitored

Check if Debezium is actually monitoring the table:

```bash
# Check connector config
curl http://72.61.233.209:8083/connectors/cdc-oracle_sf_p-ora-cdc_user/config | jq '.table.include.list'

# Check connector status
curl http://72.61.233.209:8083/connectors/cdc-oracle_sf_p-ora-cdc_user/status | jq
```

### 4. Test LogMiner Directly

Test if LogMiner can read changes:

```sql
-- Connect as SYSDBA
sqlplus sys/segmbp@1100@XE as sysdba

-- Start LogMiner session
EXECUTE DBMS_LOGMNR.START_LOGMNR(OPTIONS => DBMS_LOGMNR.DICT_FROM_ONLINE_CATALOG);

-- Check if changes are visible
SELECT sql_redo, sql_undo, scn, timestamp
FROM v$logmnr_contents
WHERE table_name = 'TEST'
AND owner_name = 'CDC_USER'
ORDER BY scn DESC
FETCH FIRST 10 ROWS ONLY;

-- Stop LogMiner
EXECUTE DBMS_LOGMNR.END_LOGMNR;
```

### 5. Check Archive Log Destination

Verify archive logs are being written:

```sql
-- Check archive log destination
SHOW PARAMETER log_archive_dest;

-- Check archive log destination status
SELECT destination, status, error FROM v$archive_dest WHERE status != 'INACTIVE';

-- Check if archive log destination has space
SELECT * FROM v$recovery_file_dest;
```

## Possible Issues and Solutions

### Issue 1: LogMiner Session Not Started
**Symptom:** No CDC events captured
**Solution:** Restart connector or check LogMiner session status

### Issue 2: Archive Logs Not Being Generated
**Symptom:** Changes made but no archive logs
**Solution:** Verify archive log mode is enabled and destination is configured

### Issue 3: SCN Not Advancing
**Symptom:** Connector stuck at initial SCN
**Solution:** Check if database is generating new SCNs (make a change and check SCN)

### Issue 4: Table Not in LogMiner Scope
**Symptom:** Other tables work but this one doesn't
**Solution:** Verify table.include.list configuration matches actual table name

### Issue 5: LogMiner Strategy Issue
**Symptom:** online_catalog strategy not working
**Solution:** Try changing to `redo_log_catalog` or check Oracle version compatibility

## Configuration Check

Current configuration:
- `table.include.list`: `cdc_user.test` ✓
- `log.mining.strategy`: `online_catalog`
- `log.mining.continuous.mine`: `true`
- `snapshot.mode`: `initial_only`
- `database.connection.adapter`: `logminer`

## Recommended Actions

1. **Check connector logs first** - This will show any errors or warnings
2. **Verify LogMiner session** - Check if LogMiner is actually running
3. **Test LogMiner directly** - See if LogMiner can read changes
4. **Check archive logs** - Verify archive logs are being generated
5. **Try restarting connector** - Sometimes a restart fixes LogMiner session issues

## Alternative: Use Redo Log Catalog Strategy

If `online_catalog` is not working, try changing to `redo_log_catalog`:

```bash
# Update connector config
curl -X PUT http://72.61.233.209:8083/connectors/cdc-oracle_sf_p-ora-cdc_user/config \
  -H "Content-Type: application/json" \
  -d '{
    "log.mining.strategy": "redo_log_catalog"
  }'
```

Then restart the connector.

