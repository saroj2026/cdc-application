# Snowflake Auto-Configuration for CDC Pipeline

## ✅ What's Now Automated

When you create a new pipeline with Snowflake as the target, the system will **automatically** configure:

1. **Debezium ExtractNewRecordState Transform** - Extracts the `after` field from Debezium envelope
2. **JsonConverter** - Works with transforms (instead of SnowflakeJsonConverter which doesn't)
3. **Auto-Table Creation** - Snowflake connector will auto-create tables with `RECORD_CONTENT` and `RECORD_METADATA` columns
4. **Full Load Support** - Works with both full load and CDC modes
5. **Proper Schema Mapping** - Automatically maps Kafka topics to Snowflake tables

## How It Works

### 1. Source (Debezium)
- Automatically configured based on source database type (PostgreSQL, SQL Server, etc.)
- Captures changes and sends to Kafka in Debezium envelope format

### 2. Kafka
- Messages are in Debezium format: `{payload: {after: {...}, before: {...}, op: "c/u/d"}}`

### 3. Sink (Snowflake Connector)
The backend now automatically configures:
```json
{
  "value.converter": "org.apache.kafka.connect.json.JsonConverter",
  "value.converter.schemas.enable": "true",
  "transforms": "unwrap",
  "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
  "transforms.unwrap.drop.tombstones": "false",
  "transforms.unwrap.delete.handling.mode": "none"
}
```

This extracts the `after` field from the Debezium envelope, making it compatible with Snowflake.

### 4. Snowflake Table
- Auto-created with:
  - `RECORD_CONTENT` (VARIANT) - Contains the actual data
  - `RECORD_METADATA` (VARIANT) - Contains Kafka metadata (topic, partition, offset)

## Pipeline Flow

```
PostgreSQL/SQL Server
    ↓
Debezium Source Connector
    ↓ (Debezium envelope format)
Kafka Topic
    ↓
Snowflake Sink Connector
    ↓ (ExtractNewRecordState transform extracts 'after' field)
Snowflake Table (auto-created)
```

## Querying Data in Snowflake

Since data is stored in `RECORD_CONTENT` as JSON, use JSON path syntax:

```sql
-- Query specific record
SELECT 
    RECORD_CONTENT:project_id::NUMBER as project_id,
    RECORD_CONTENT:project_name::STRING as project_name,
    RECORD_CONTENT:department_id::NUMBER as department_id,
    RECORD_CONTENT:employee_id::NUMBER as employee_id,
    RECORD_CONTENT:start_date::NUMBER as start_date,
    RECORD_CONTENT:end_date::STRING as end_date,
    RECORD_CONTENT:status::STRING as status
FROM projects_simple 
WHERE RECORD_CONTENT:project_id = 9000;

-- Get all records
SELECT * FROM projects_simple;

-- Check Kafka metadata
SELECT 
    RECORD_CONTENT:project_id::NUMBER as project_id,
    RECORD_METADATA:topic::STRING as kafka_topic,
    RECORD_METADATA:partition::NUMBER as kafka_partition,
    RECORD_METADATA:offset::NUMBER as kafka_offset
FROM projects_simple;
```

## Requirements

1. **Debezium Transform Library** - Must be installed in Kafka Connect
   - Usually included with Debezium connector installation
   - Class: `io.debezium.transforms.ExtractNewRecordState`

2. **Snowflake Authentication** - Either:
   - Private key (recommended for production)
   - Password (if private key not available)

3. **Snowflake Permissions** - User needs:
   - CREATE TABLE permission in target schema
   - INSERT permission
   - USAGE on database and schema

## What You Need to Do

**Nothing!** The system now automatically:
- ✅ Configures the Debezium transform
- ✅ Uses JsonConverter (compatible with transforms)
- ✅ Sets up proper error handling
- ✅ Maps topics to tables correctly
- ✅ Handles authentication (private key or password)

Just create your pipeline with:
1. Source connection (PostgreSQL, SQL Server, etc.)
2. Target connection (Snowflake with credentials)
3. Select tables
4. Choose mode (full_load, cdc, or full_load_and_cdc)

The rest is automatic! 🎉

## Troubleshooting

If data doesn't appear in Snowflake:

1. **Check connector status:**
   ```bash
   curl http://kafka-connect:8083/connectors/sink-<pipeline>-snowflake-<schema>/status
   ```

2. **Verify Debezium transform is available:**
   - Check Kafka Connect logs for: `ExtractNewRecordState`
   - If missing, install Debezium transform library

3. **Check table structure:**
   ```sql
   DESCRIBE TABLE <table_name>;
   ```
   Should show `RECORD_CONTENT` and `RECORD_METADATA` columns

4. **Verify data in Kafka:**
   - Check if messages are in Kafka topic
   - Verify Debezium is sending data

5. **Check connector logs:**
   - Look for errors in Kafka Connect worker logs
   - Check Snowflake connection errors

