# Sink Connector Fixes Applied

## Issue
Data is in Kafka topic `pg_sql_p.public.department` but not appearing in SQL Server `dbo.department` table.

## Fixes Applied

### 1. ✅ Fixed Connection URL
- **Issue:** Missing `trustServerCertificate=true` parameter
- **Fix:** Added `trustServerCertificate=true` to connection URL
- **Result:** Connection should now work with SQL Server SSL

### 2. ✅ Removed Conflicting Transforms
- **Issue:** Config had both `flatten` and `extractPayload,extractAfter` transforms
- **Fix:** Removed conflicting `flatten` transform configuration
- **Result:** Clean transform chain: `extractPayload -> extractAfter`

### 3. ✅ Set Error Tolerance to 'none'
- **Issue:** `errors.tolerance: all` was hiding errors
- **Fix:** Changed to `errors.tolerance: none` to see errors immediately
- **Result:** Connector should show FAILED if there are errors (but it's still RUNNING)

### 4. ✅ Fixed Table Name Format
- **Issue:** Table format was `dbo.department`
- **Fix:** Changed to `department` (schema defaults to dbo when databaseName is in URL)
- **Result:** Should match SQL Server JDBC connector expectations

### 5. ✅ Verified Transform Chain
- **Configuration:**
  - `transforms: extractPayload,extractAfter`
  - `transforms.extractPayload.type: ExtractField$Value`
  - `transforms.extractPayload.field: payload`
  - `transforms.extractAfter.type: ExtractField$Value`
  - `transforms.extractAfter.field: after`

### 6. ✅ Paused/Resumed Connector
- **Action:** Paused and resumed connector to force message reprocessing
- **Result:** Connector resumed but data still not flowing

## Current Status

- **Connector State:** RUNNING
- **Task State:** RUNNING
- **Error Tolerance:** none (errors would be visible)
- **PostgreSQL Rows:** 10
- **SQL Server Rows:** 8
- **Missing Rows:** IDs 9 and 10

## Diagnosis

Since the connector is RUNNING (not FAILED) with `errors.tolerance: none`, this suggests:

1. **Messages not being consumed:** Connector might be stuck at an old offset
2. **Transform silently failing:** Transforms might not be extracting data correctly
3. **Message format mismatch:** Debezium messages might not match expected structure
4. **SQL write failing silently:** Writes might be failing but not causing connector failure

## Required Next Steps

### 1. Check Kafka Connect Logs (CRITICAL)

SSH to the Kafka Connect server and check logs:

```bash
# SSH to server
ssh user@72.61.233.209

# If Kafka Connect is in Docker:
docker logs kafka-connect 2>&1 | grep -i "sink-pg_sql_p\|error\|exception\|transform\|ExtractField" | tail -100

# If running as service:
tail -200 /var/log/kafka-connect/kafka-connect.log | grep -i "sink-pg_sql_p\|error\|exception"
```

**Look for:**
- Transform errors (ExtractField failures)
- SQL errors (table name, syntax errors)
- Connection errors
- Message format errors

### 2. Verify Kafka Topic Messages

Check if messages are actually in the topic and their format:

```bash
# On Kafka server, use kafka-console-consumer
kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic pg_sql_p.public.department \
  --from-beginning \
  --max-messages 5
```

**Expected format:**
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

### 3. Check Connector Offsets

Verify the connector is consuming from the correct offset:

```bash
# Check connector offsets (if available via REST API)
curl http://72.61.233.209:8083/connectors/sink-pg_sql_p-mssql-dbo/status
```

### 4. Test SQL Server Write Directly

Verify SQL Server connection and write capability:

```sql
-- Test insert
INSERT INTO dbo.department (id, name, location) VALUES (999, 'Test', 'TestLoc');
SELECT * FROM dbo.department WHERE id = 999;
DELETE FROM dbo.department WHERE id = 999;
```

## Current Configuration

```json
{
  "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
  "topics": "pg_sql_p.public.department",
  "connection.url": "jdbc:sqlserver://72.61.233.209:1433;databaseName=cdctest;encrypt=false;trustServerCertificate=true",
  "connection.user": "sa",
  "connection.password": "Sql@12345",
  "table.name.format": "department",
  "insert.mode": "insert",
  "pk.mode": "none",
  "batch.size": "1",
  "auto.create": "true",
  "auto.evolve": "true",
  "transforms": "extractPayload,extractAfter",
  "transforms.extractPayload.type": "org.apache.kafka.connect.transforms.ExtractField$Value",
  "transforms.extractPayload.field": "payload",
  "transforms.extractAfter.type": "org.apache.kafka.connect.transforms.ExtractField$Value",
  "transforms.extractAfter.field": "after",
  "value.converter": "org.apache.kafka.connect.json.JsonConverter",
  "value.converter.schemas.enable": "true",
  "errors.tolerance": "none",
  "errors.log.enable": "true",
  "errors.log.include.messages": "true"
}
```

## Alternative Solutions to Try

### Option 1: Use Debezium Unwrap Transform
If ExtractField chain doesn't work, try Debezium's built-in unwrap transform:

```json
{
  "transforms": "unwrap",
  "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
  "transforms.unwrap.drop.tombstones": "false",
  "transforms.unwrap.delete.handling.mode": "none"
}
```

**Note:** Requires Debezium transform library to be available in Kafka Connect.

### Option 2: Disable Transforms and Use Flatten
Try using Flatten transform instead:

```json
{
  "transforms": "flatten",
  "transforms.flatten.type": "org.apache.kafka.connect.transforms.Flatten$Value",
  "transforms.flatten.delimiter": "_"
}
```

### Option 3: Check if Messages Need Schema Registry
If using Confluent Schema Registry, ensure it's configured correctly.

## Summary

All configuration fixes have been applied. The connector is RUNNING but data is not flowing. The next critical step is to **check Kafka Connect logs on the server** to identify the actual error preventing writes.

Once the error is identified from the logs, the configuration can be adjusted accordingly.


