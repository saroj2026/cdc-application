# CDC Not Sending Data to Kafka and MS SQL - Diagnosis

## 🔍 Root Cause Identified

**Issue**: Replication slot has **907 KB of lag**, meaning there ARE changes waiting to be processed, but Debezium is not reading them.

## Current Status

### ✅ What's Working:
- Debezium Connector: RUNNING
- Sink Connector: RUNNING
- Replication Slot: Active
- REPLICA IDENTITY: FULL (correctly set)

### ❌ What's NOT Working:
- **Replication Slot Lag: 907 KB** - Changes are stuck in WAL
- Debezium is not consuming from the replication slot
- No new data reaching Kafka topics
- No new data reaching MS SQL

## Diagnosis Details

### Replication Slot Status:
```
Slot: pg_to_mssql_projects_simple_slot
CDC LSN: 0/28ABE88 (where CDC is reading from)
Current WAL LSN: 0/298EDF8 (where new changes are)
Lag: 929,648 bytes (907.86 KB)
```

**This means**:
- PostgreSQL has written 907 KB of changes to WAL
- Debezium should have read these changes
- But Debezium is stuck at LSN 0/28ABE88
- Changes between 0/28ABE88 and 0/298EDF8 are not being processed

### Connector Configuration:
- **Snapshot Mode**: `never` (only captures NEW changes)
- **Slot Name**: `pg_to_mssql_projects_simple_slot`
- **Topic**: `pg_to_mssql_projects_simple.public.projects_simple`

## Possible Causes

### 1. Debezium Connector Stuck
- Connector shows RUNNING but not actually reading
- Common after connector restart or network issues
- **Solution**: Restart the connector

### 2. Replication Slot Issue
- Slot might be in a bad state
- PostgreSQL might not be sending changes
- **Solution**: Check PostgreSQL logs, restart connector

### 3. Network/Connection Issue
- Debezium might have lost connection to PostgreSQL
- Connection might be timing out
- **Solution**: Check connectivity, restart connector

### 4. Kafka Topic Issue
- Messages might be produced but not visible
- Topic might have retention issues
- **Solution**: Check Kafka topic directly

## Solutions

### Solution 1: Restart Debezium Connector (Recommended)

```bash
# Pause and resume the connector
curl -X PUT "http://72.61.233.209:8083/connectors/cdc-pg_to_mssql_projects_simple-pg-public/pause"
sleep 2
curl -X PUT "http://72.61.233.209:8083/connectors/cdc-pg_to_mssql_projects_simple-pg-public/resume"
```

This forces Debezium to:
- Reconnect to PostgreSQL
- Resume reading from the replication slot
- Process the 907 KB of pending changes

### Solution 2: Restart Both Connectors

```bash
# Restart Debezium
curl -X PUT "http://72.61.233.209:8083/connectors/cdc-pg_to_mssql_projects_simple-pg-public/pause"
curl -X PUT "http://72.61.233.209:8083/connectors/cdc-pg_to_mssql_projects_simple-pg-public/resume"

# Restart Sink
curl -X PUT "http://72.61.233.209:8083/connectors/sink-pg_to_mssql_projects_simple-mssql-dbo/pause"
curl -X PUT "http://72.61.233.209:8083/connectors/sink-pg_to_mssql_projects_simple-mssql-dbo/resume"
```

### Solution 3: Check Kafka Connect Logs

SSH to the server and check logs:
```bash
ssh ssh@72.61.233.209
# Password: segmbp@1100

# Check Kafka Connect logs
docker logs kafka-connect-cdc | tail -100
# Or
docker logs kafka-connect | grep -i error
```

### Solution 4: Make a Test Change

After restarting, make a test change to verify CDC is working:

```sql
-- In PostgreSQL
INSERT INTO projects_simple (project_id, project_name, department_id, employee_id, start_date, status)
VALUES (999, 'CDC Test After Restart', 1, 1, '2024-01-01', 'ACTIVE');
```

Then check:
1. Replication slot lag (should process quickly)
2. Kafka topic (should have new message)
3. SQL Server (should have new row)

## Verification Steps

### 1. Check Replication Slot Lag
```sql
SELECT 
    slot_name,
    confirmed_flush_lsn AS cdc_lsn,
    pg_current_wal_lsn() AS current_lsn,
    pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) AS lag_bytes
FROM pg_replication_slots
WHERE slot_name = 'pg_to_mssql_projects_simple_slot';
```

**Expected**: Lag should decrease after restart

### 2. Check Kafka Topic
```bash
# If you have Kafka CLI access
kafka-console-consumer \
  --bootstrap-server 72.61.233.209:9092 \
  --topic pg_to_mssql_projects_simple.public.projects_simple \
  --from-beginning \
  --max-messages 5
```

**Expected**: Should see recent messages

### 3. Check SQL Server
```sql
SELECT COUNT(*) FROM dbo.projects_simple;
SELECT TOP 5 * FROM dbo.projects_simple ORDER BY project_id DESC;
```

**Expected**: Should match PostgreSQL row count

## Prevention

To prevent this issue in the future:

1. **Monitor Replication Slot Lag**:
   - Set up alerts for lag > 1 MB
   - Check lag regularly

2. **Monitor Connector Health**:
   - Check connector status regularly
   - Set up alerts for FAILED state

3. **Regular Restarts**:
   - Restart connectors periodically if lag accumulates
   - Or implement auto-restart on high lag

## Summary

**Root Cause**: Debezium connector is stuck and not reading from replication slot despite showing RUNNING status.

**Solution**: Restart the Debezium connector to force it to resume reading from the slot and process the 907 KB of pending changes.

**Next Steps**:
1. Restart Debezium connector (already attempted)
2. Wait 30-60 seconds for lag to process
3. Make a test change to verify CDC is working
4. Check SQL Server for new data


