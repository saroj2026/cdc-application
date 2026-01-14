# Snowflake CDC Format Analysis

## ✅ Current Format Status: **CORRECT & STANDARD**

After performing INSERT, UPDATE, DELETE operations in Oracle and analyzing the data in Snowflake, **your current format matches Snowflake CDC best practices**.

## Current Format Structure

### Table Schema
```
TEST table:
  - RECORD_CONTENT: VARIANT ✅
  - RECORD_METADATA: VARIANT ✅
```

### RECORD_CONTENT Structure (Debezium Envelope)

#### INSERT Operation (op='c')
```json
{
  "op": "c",
  "after": {
    "ID": {"scale": 0, "value": "ARli"},
    "NAME": "CDC Test INSERT 20260113_123628",
    "CREATED_AT": 1768287990592824
  },
  "before": null,
  "source": {
    "connector": "oracle",
    "name": "oracle_sf_p",
    "ts_ms": 1768287990000,
    "snapshot": "false",
    "db": "XE",
    "schema": "CDC_USER",
    "table": "TEST",
    "scn": "18300268",
    "commit_scn": "18300269",
    "txId": "05001f00982e0000",
    "user_name": "C##CDC_USER"
  },
  "ts_ms": 1768287992211,
  "transaction": null
}
```

#### UPDATE Operation (op='u')
```json
{
  "op": "u",
  "after": {
    "ID": {...},
    "NAME": "Updated Name",
    "CREATED_AT": ...
  },
  "before": {
    "ID": {...},
    "NAME": "Original Name",
    "CREATED_AT": ...
  },
  "source": {...},
  "ts_ms": ...,
  "transaction": null
}
```

#### DELETE Operation (op='d')
```json
{
  "op": "d",
  "after": null,
  "before": {
    "ID": {...},
    "NAME": "Deleted Record",
    "CREATED_AT": ...
  },
  "source": {...},
  "ts_ms": ...,
  "transaction": null
}
```

### RECORD_METADATA Structure
```json
{
  "CreateTime": 1768287992795,
  "key": "{\"ID\":{\"scale\":0,\"value\":\"ARli\"}}",
  "offset": 49,
  "partition": 0,
  "topic": "oracle_sf_p.CDC_USER.TEST"
}
```

## Comparison with Snowflake Best Practices

### ✅ Matches Best Practices

1. **RECORD_CONTENT (VARIANT)**: Contains full Kafka message payload ✅
2. **RECORD_METADATA (VARIANT)**: Contains Kafka metadata ✅
3. **Debezium Envelope**: Full envelope with `op`, `after`, `before`, `source`, `ts_ms` ✅
4. **Operation Types**: Correctly represented (`c`=INSERT, `u`=UPDATE, `d`=DELETE) ✅
5. **DELETE Operations**: `after=null`, `before=deleted record data` ✅
6. **UPDATE Operations**: Both `after` and `before` present ✅
7. **INSERT Operations**: `after=new record`, `before=null` ✅

### Based on Research

According to Snowflake documentation and best practices:
- **VARIANT format is standard** for CDC data
- **Full Debezium envelope** should be preserved (no transforms that remove fields)
- **RECORD_METADATA** should contain Kafka metadata (offset, partition, topic, etc.)
- **Operation field (`op`)** is essential for identifying CDC operation type

## Optional Enhancements

### Schema Detection (Optional)

You can optionally enable schema detection to create individual columns:

```json
{
  "schematization.enabled": "true"
}
```

**Pros:**
- Creates individual columns for each field
- Easier to query (no JSON path expressions)
- Auto-evolves when new fields appear

**Cons:**
- Less flexible for schema changes
- Requires more storage
- Current VARIANT format is more standard for CDC

**Recommendation:** Keep current VARIANT format (standard for CDC)

## Querying Examples

### Query by Operation Type
```sql
SELECT 
  RECORD_CONTENT:op as operation,
  RECORD_CONTENT:after:NAME as name_after,
  RECORD_CONTENT:before:NAME as name_before
FROM TEST
WHERE RECORD_CONTENT:op = 'u'  -- UPDATE operations
```

### Query INSERT Operations
```sql
SELECT 
  RECORD_CONTENT:after:ID as id,
  RECORD_CONTENT:after:NAME as name,
  RECORD_METADATA:CreateTime as create_time
FROM TEST
WHERE RECORD_CONTENT:op = 'c'  -- INSERT operations
```

### Query DELETE Operations
```sql
SELECT 
  RECORD_CONTENT:before:ID as deleted_id,
  RECORD_CONTENT:before:NAME as deleted_name,
  RECORD_METADATA:CreateTime as delete_time
FROM TEST
WHERE RECORD_CONTENT:op = 'd'  -- DELETE operations
```

## Conclusion

✅ **Your current Snowflake CDC format is STANDARD and CORRECT!**

- No changes needed
- Format matches Snowflake best practices
- Full Debezium envelope is preserved
- All operation types are properly represented
- DELETE operations show `before` data (not empty)

The format you're receiving is exactly what Snowflake recommends for CDC data ingestion.

