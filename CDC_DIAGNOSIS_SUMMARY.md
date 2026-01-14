# CDC Flow Diagnosis Summary

## Current Status

✅ **Working:**
- PostgreSQL source: Row 110 exists
- Debezium connector: RUNNING
- Kafka topic: Has messages (confirmed by user)
- Sink connector: RUNNING
- SQL Server connection: Works (tested direct INSERT)

❌ **Not Working:**
- Sink connector is NOT writing to SQL Server
- Row 110 is not appearing in SQL Server
- 4 rows missing (PostgreSQL: 13, SQL Server: 9)

## Issue Location

**Problem:** Kafka → Sink → SQL Server step is broken

The Sink connector is:
- ✅ Running and consuming from correct Kafka topic
- ✅ Configured with ExtractField transform to extract 'after' field
- ❌ NOT processing/writing messages to SQL Server

## Root Cause Analysis

Since `errors.tolerance=all` is set, errors are being logged but not failing the connector. This means:
- The connector shows as RUNNING even if it's encountering errors
- Errors are in the Kafka Connect worker logs on the server

## Possible Issues

1. **ExtractField Transform Issue:**
   - The 'after' field might not be at the expected path
   - With `schemas.enable=true`, the structure is: `{schema: {...}, payload: {after: {...}}}`
   - ExtractField might need to extract from `payload.after` not just `after`

2. **Message Format Mismatch:**
   - Actual Kafka message format might differ from expected
   - Debezium might be sending a different structure

3. **Data Type Conversion:**
   - Date format from Debezium (integer) might not convert to SQL Server DATE
   - Column type mismatches

4. **Table Name Format:**
   - `table.name.format: dbo.projects_simple` might not be resolving correctly
   - SQL Server JDBC connector might need different format

## Next Steps to Diagnose

1. **Check Kafka Message Format:**
   ```bash
   kafka-console-consumer --bootstrap-server 72.61.233.209:9092 \
     --topic pg_to_mssql_projects_simple.public.projects_simple \
     --from-beginning --property print.key=true
   ```
   This will show the actual message structure.

2. **Check Kafka Connect Logs:**
   - SSH to 72.61.233.209
   - Find Kafka Connect worker logs
   - Look for errors related to:
     - ExtractField transform
     - JDBC Sink connector
     - SQL Server insert errors
     - Data type conversion errors

3. **Verify Message Structure:**
   - Check if messages have `payload.after` or just `after`
   - Check if `after` field is null for some operations
   - Verify date format in messages

## Recommended Fixes to Try

### Option 1: Use Unwrap Transform in Debezium
Instead of extracting in Sink, unwrap in Debezium:
- Set Debezium config: `transforms=unwrap`
- Remove ExtractField from Sink
- Sink receives flat structure directly

### Option 2: Fix ExtractField Path
If messages have structure `{payload: {after: {...}}}`:
- Use Flatten transform first, then ExtractField
- Or use a custom transform

### Option 3: Check Actual Message Format
First, verify what the actual Kafka message looks like, then adjust transforms accordingly.

## Current Configuration

**Sink Connector:**
- Transforms: `extractAfter`
- Extract field: `after`
- Table format: `dbo.projects_simple`
- Errors tolerance: `all` (errors logged but not failing)

**Debezium Connector:**
- Schema enabled: `true`
- Message format: Debezium envelope with schemas

## Action Items

1. ✅ Check Kafka message format (user can do this)
2. ⏳ Check Kafka Connect logs on server
3. ⏳ Try alternative transform configuration
4. ⏳ Verify if ExtractField is working correctly

