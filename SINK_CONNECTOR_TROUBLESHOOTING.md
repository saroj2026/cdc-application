# Sink Connector Troubleshooting Guide

## Issue: Data in Kafka but Not in SQL Server

**Symptoms:**
- ✅ Data is in Kafka topic: `pg_sql_p.public.department`
- ✅ Debezium connector is RUNNING and capturing changes
- ✅ Sink connector shows RUNNING status
- ❌ Data is NOT appearing in SQL Server `dbo.department` table

**Current Status:**
- PostgreSQL: 10 rows (including IDs 9 and 10)
- SQL Server: 8 rows (missing IDs 9 and 10)
- Sink Connector: RUNNING
- Error Tolerance: `all` (errors are logged but not reported)

## Root Cause Analysis

The sink connector has `errors.tolerance: all` configured, which means:
- Errors are being **silently logged** but not reported
- The connector shows as RUNNING even when it's failing to write data
- Actual error messages are only visible in Kafka Connect logs

## Diagnostic Steps

### 1. Check Kafka Connect Logs

**On the Kafka Connect server (72.61.233.209):**

```bash
# SSH to the server
ssh user@72.61.233.209

# Find Kafka Connect logs
# If running in Docker:
docker logs kafka-connect | grep -i "sink-pg_sql_p\|error\|exception" | tail -50

# If running as a service:
tail -100 /var/log/kafka-connect/kafka-connect.log | grep -i "sink-pg_sql_p\|error\|exception"
```

**Look for:**
- SQL errors (e.g., "Invalid object name", "Incorrect syntax")
- Transform errors (e.g., "Field not found", "ExtractField failed")
- Connection errors (e.g., "Login failed", "Connection refused")

### 2. Check Sink Connector Task Details

```bash
curl http://72.61.233.209:8083/connectors/sink-pg_sql_p-mssql-dbo/status
```

Look for:
- Task state (should be RUNNING)
- Any error traces in the task object

### 3. Verify Debezium Message Format

The sink connector expects Debezium messages in this format:
```json
{
  "schema": {...},
  "payload": {
    "after": {
      "id": 10,
      "name": "...",
      "location": "..."
    },
    "before": null,
    "op": "c"
  }
}
```

The transforms are configured to:
1. Extract `payload` field → `{"after": {...}, "before": null, "op": "c"}`
2. Extract `after` field → `{"id": 10, "name": "...", "location": "..."}`

### 4. Common Issues and Fixes

#### Issue 1: Table Name Format
**Problem:** SQL Server JDBC connector might interpret `dbo.department` incorrectly

**Fix:** Try changing `table.name.format` to just `department` (schema defaults to dbo when `databaseName` is in connection URL)

#### Issue 2: Transform Chain Not Working
**Problem:** The ExtractField transforms might not be chaining correctly

**Fix:** Verify the message structure matches expectations. The second ExtractField should extract from the result of the first.

#### Issue 3: Value Converter Schema Mismatch
**Problem:** `value.converter.schemas.enable=true` but the message structure doesn't match

**Fix:** Check if Debezium is actually sending schemas. If not, set `value.converter.schemas.enable=false`

#### Issue 4: SQL Server Connection/Authentication
**Problem:** Connection might be failing silently

**Fix:** Test connection directly:
```bash
# Test SQL Server connection
sqlcmd -S 72.61.233.209,1433 -U sa -P [password] -d cdctest -Q "SELECT COUNT(*) FROM dbo.department"
```

## Immediate Actions

### Option 1: Check Kafka Connect Logs (Recommended)
1. SSH to Kafka Connect server
2. Check logs for sink connector errors
3. Identify the specific error
4. Fix based on error message

### Option 2: Temporarily Disable Error Tolerance
Change `errors.tolerance` from `all` to `none` to see errors immediately:

```python
# Update connector config
config['errors.tolerance'] = 'none'
# Restart connector
```

**Warning:** This will cause the connector to fail if there are errors, but you'll see them immediately.

### Option 3: Test with a Simple Message
1. Manually produce a test message to the Kafka topic
2. Verify the sink connector processes it
3. Check if it appears in SQL Server

## Current Configuration

```
Connector: sink-pg_sql_p-mssql-dbo
Topics: pg_sql_p.public.department
Table Format: dbo.department
Batch Size: 1 (reduced for immediate processing)
Transforms: extractPayload,extractAfter
Error Tolerance: all
```

## Next Steps

1. **Check Kafka Connect logs** on server 72.61.233.209
2. **Identify the specific error** preventing writes
3. **Fix the configuration** based on the error
4. **Restart the connector** and verify data flow

## Verification

After fixing, verify:
```sql
-- Check SQL Server
SELECT COUNT(*) FROM dbo.department;
-- Should match PostgreSQL: 10 rows

-- Check for specific records
SELECT * FROM dbo.department WHERE id IN (9, 10);
```

## Contact Points

- Kafka Connect: http://72.61.233.209:8083
- Connector Status: http://72.61.233.209:8083/connectors/sink-pg_sql_p-mssql-dbo/status
- Connector Config: http://72.61.233.209:8083/connectors/sink-pg_sql_p-mssql-dbo/config


