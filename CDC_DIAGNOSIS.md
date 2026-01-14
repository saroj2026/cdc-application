# CDC Diagnosis for oracle_sf_p Pipeline

## Current Status

### ✅ Working:
1. **Debezium Source Connector**: RUNNING
   - Connector: `cdc-oracle_sf_p-ora-cdc_user`
   - State: RUNNING
   - Task: RUNNING

2. **Snowflake Sink Connector**: RUNNING
   - Connector: `sink-oracle_sf_p-snow-public`
   - State: RUNNING
   - Task: RUNNING
   - Topic: `oracle_sf_p.CDC_USER.TEST` ✓

3. **Kafka Topics**:
   - Schema topic (`oracle_sf_p`): 8 messages (schema changes)
   - Table topic (`oracle_sf_p.CDC_USER.TEST`): 3 messages (initial snapshot only)

4. **Snapshot**: Completed successfully (3 records in topic)

### ❌ Issue:
**CDC changes (INSERT/UPDATE/DELETE) are NOT being captured after snapshot**

- Configuration: `snapshot.mode: initial_only` ✓
- Table topic should have new messages after INSERT/UPDATE/DELETE operations
- Currently: Table topic has only 3 messages (snapshot data)
- Expected: Should have 6+ messages after INSERT/UPDATE/DELETE operations

## Root Cause Analysis

The connector is RUNNING but not capturing CDC changes. This typically indicates:

1. **Oracle Archive Logs Not Enabled** (Most Common)
   - Oracle XE may not have archive logs enabled by default
   - LogMiner requires archive logs for CDC

2. **LogMiner Not Reading Archive Logs**
   - LogMiner strategy: `online_catalog` (requires archive logs)
   - If archive logs aren't available, LogMiner can't capture changes

3. **Oracle User Permissions**
   - User `c##cdc_user` has LOGMINING privilege ✓
   - But if archive logs aren't available, permission doesn't help

## Solution

### Check Oracle Archive Log Mode:

```sql
-- Connect as SYSDBA
sqlplus sys/password@XE as sysdba

-- Check archive log mode
SELECT log_mode FROM v$database;

-- If LOG_MODE is NOARCHIVELOG, enable it:
SHUTDOWN IMMEDIATE;
STARTUP MOUNT;
ALTER DATABASE ARCHIVELOG;
ALTER DATABASE OPEN;
```

### Alternative: Use Online Log Mining (if archive logs can't be enabled)

If archive logs can't be enabled (e.g., Oracle XE limitations), we may need to:
- Use a different LogMiner strategy (if available)
- Or use a different CDC approach for Oracle XE

## Next Steps

1. Check Oracle archive log mode
2. If NOARCHIVELOG, enable it (if possible)
3. If archive logs can't be enabled, investigate alternative CDC strategies
4. Restart Debezium connector after enabling archive logs

