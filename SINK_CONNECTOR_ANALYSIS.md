# Sink Connector Analysis

## Current Status

**Connector**: `sink-pg_to_mssql_projects_simple-mssql-dbo`
- **State**: RUNNING ✅
- **Task**: RUNNING ✅

## Configuration

### Topics
- **Consuming from**: `pg_to_mssql_projects_simple.public.projects_simple` ✅

### Target
- **Table**: `dbo.projects_simple` ✅
- **Database**: `cdctest`
- **Connection**: `jdbc:sqlserver://72.61.233.209:1433;databaseName=cdctest;encrypt=false`

### Transforms
The sink connector uses a two-step transform to extract data from Debezium envelope:

1. **extractPayload**: Extracts `payload` field
   ```json
   Input: {
     "schema": {...},
     "payload": {
       "after": {...}
     }
   }
   
   Output: {
     "after": {...}
   }
   ```

2. **extractAfter**: Extracts `after` field from payload
   ```json
   Input: {
     "after": {
       "project_id": 1,
       "project_name": "...",
       ...
     }
   }
   
   Output: {
     "project_id": 1,
     "project_name": "...",
     ...
   }
   ```

### Settings
- **Insert Mode**: `insert`
- **Batch Size**: `3000`
- **Auto Create**: `true`
- **Auto Evolve**: `true`
- **PK Mode**: `none`
- **Error Tolerance**: `all` (errors are logged but don't fail the connector)

## Potential Issues

### 1. Transform Chain
The transform chain `extractPayload,extractAfter` should work, but there might be issues:
- If Debezium message format is different than expected
- If the `after` field structure is nested differently

### 2. Data Format Mismatch
- Debezium sends dates as integers (days since epoch)
- SQL Server expects DATE type
- The JDBC connector should handle this, but might fail silently

### 3. Error Tolerance
With `errors.tolerance=all`, errors are logged but the connector continues running.
- Check Kafka Connect logs for errors
- Errors might be happening but not visible in status

## Diagnostic Steps

### 1. Check Kafka Connect Logs
```bash
# SSH to server
ssh ssh@72.61.233.209
# Password: segmbp@1100

# Check logs
docker logs kafka-connect-cdc | grep -i "sink-pg_to_mssql" | tail -50
docker logs kafka-connect-cdc | grep -i error | tail -20
```

### 2. Verify Data in SQL Server
```sql
-- Check if table exists
SELECT * FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'dbo' 
AND TABLE_NAME = 'projects_simple';

-- Check row count
SELECT COUNT(*) FROM dbo.projects_simple;

-- Check sample data
SELECT TOP 5 * FROM dbo.projects_simple;
```

### 3. Check Kafka Topic Messages
Verify messages are actually in the Kafka topic:
```bash
kafka-console-consumer --bootstrap-server 72.61.233.209:9092 \
  --topic pg_to_mssql_projects_simple.public.projects_simple \
  --from-beginning --max-messages 1
```

### 4. Test Transform Chain
The transforms should extract:
- `payload` from root
- `after` from payload

If the structure is different, transforms will fail silently (due to `errors.tolerance=all`).

## Common Issues

### Issue 1: Transform Not Working
**Symptom**: No data in SQL Server, but messages in Kafka topic

**Solution**: Check if Debezium message format matches expected structure. The transform expects:
```json
{
  "schema": {...},
  "payload": {
    "after": {...}
  }
}
```

### Issue 2: Date Format Issues
**Symptom**: Data in SQL Server but dates are wrong

**Solution**: Debezium sends dates as integers. JDBC connector should convert, but might need explicit format.

### Issue 3: Column Mismatch
**Symptom**: Some columns missing or wrong

**Solution**: Check if `auto.evolve=true` is working. Table schema should match Debezium schema.

## Recommendations

1. **Check Logs**: Most important - check Kafka Connect logs for errors
2. **Verify Topic**: Make sure messages are in the Kafka topic
3. **Test Connection**: Verify SQL Server connection works with connector credentials
4. **Check Table**: Verify table exists and has correct schema
5. **Monitor Metrics**: Check if connector is actually consuming messages

## Next Steps

1. Check Kafka Connect logs for errors
2. Verify data is in SQL Server table
3. If no data, check if messages are in Kafka topic
4. If messages exist but no data in SQL Server, check transform chain
5. Consider temporarily setting `errors.tolerance=none` to see errors immediately


