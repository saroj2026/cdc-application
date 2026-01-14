# LSN (Log Sequence Number) and CDC Explanation

## What is LSN?

**LSN (Log Sequence Number)** is a unique identifier that represents a specific position in PostgreSQL's Write-Ahead Log (WAL). Think of it as a "bookmark" or "checkpoint" in the database's transaction log.

### For Your Pipeline: `pg_to_mssql_projects_simple`

When you ran the pipeline, you saw:
```
"lsn": "0/28F5168"
```

This LSN (`0/28F5168`) represents the exact position in PostgreSQL's WAL **after** the full load completed.

## How LSN Works in Full Load + CDC

### Step-by-Step Process:

```
1. FULL LOAD PHASE
   ↓
   - Copies all existing data from PostgreSQL to SQL Server
   - Transfers 14 rows from projects_simple table
   - Creates target schema/tables if needed
   ↓
2. LSN CAPTURE (After Full Load Completes)
   ↓
   - System executes: SELECT pg_current_wal_lsn()
   - Captures current WAL position: "0/28F5168"
   - This LSN represents: "All full load data was written BEFORE this point"
   ↓
3. CDC CONNECTOR CREATION
   ↓
   - Debezium connector is created with:
     * snapshot_mode = "initial_only" (because full_load_lsn exists)
     * This tells Debezium: "Skip data, only capture schema"
   - Replication slot is created/used
   - Slot position = Current WAL position (after full load)
   ↓
4. CDC STARTS STREAMING
   ↓
   - Debezium reads from replication slot
   - Slot position is AFTER full load LSN
   - Only NEW changes (after LSN 0/28F5168) are captured
   - No duplicates from full load data
```

## Why LSN is Critical

### Without LSN:
- CDC would start from the beginning of the WAL
- Would capture ALL changes, including data already loaded
- Result: **Duplicate data** in target database

### With LSN:
- CDC knows where full load ended
- Starts streaming from AFTER that point
- Result: **No duplicates**, only new changes

## How CDC Works After Full Load

### 1. Full Load Completes
```python
# Code: ingestion/cdc_manager.py lines 690-704
# Capture LSN after full load
lsn_info = source_connector.extract_lsn_offset(database=pipeline.source_database)

result = {
    "success": True,
    "tables_transferred": 1,
    "total_rows": 14,
    "lsn": "0/28F5168",  # ← This is captured here
    "offset": 42946920,
    "timestamp": "2026-01-04T07:57:24.322920"
}
```

### 2. LSN is Stored
```python
# Code: ingestion/cdc_manager.py lines 284-285
pipeline.full_load_lsn = full_load_result.get("lsn")  # "0/28F5168"
# This is saved to the pipeline object
```

### 3. CDC Configuration Uses LSN
```python
# Code: ingestion/debezium_config.py lines 111-116
if snapshot_mode == "schema_only" and full_load_lsn:
    snapshot_mode = "initial_only"  # Only schema, skip data
elif full_load_lsn:
    snapshot_mode = "initial_only"  # Full load done - skip data
```

**What `initial_only` means:**
- ✅ Capture table schema (structure)
- ❌ Skip existing data (already loaded via full load)
- ✅ Start streaming changes from current position

### 4. Replication Slot Position

When Debezium creates/uses a replication slot:
- **New Slot**: Created at current WAL position (after full load) ✅
- **Existing Slot**: Uses existing position (might need verification)

The replication slot acts as a "pointer" in the WAL that tracks:
- Where CDC started reading
- Where it last confirmed processing
- Ensures no data is lost if CDC restarts

## Real-Time CDC Flow

Once CDC is running:

```
PostgreSQL Database
    ↓
    [INSERT/UPDATE/DELETE happens]
    ↓
    WAL records the change at LSN: 0/28F5170 (after full load LSN)
    ↓
Debezium Connector
    ↓
    Reads from replication slot
    Captures change event
    ↓
Kafka Topic
    ↓
    "pg_to_mssql_projects_simple.public.projects_simple"
    ↓
JDBC Sink Connector
    ↓
    Reads from Kafka
    Applies change to SQL Server
    ↓
SQL Server Database
    ↓
    Change is replicated (INSERT/UPDATE/DELETE)
```

## Your Pipeline Status

Based on your pipeline run:

```
Full Load:
  ✅ Status: COMPLETED
  ✅ Tables: 1 (projects_simple)
  ✅ Rows: 14
  ✅ LSN Captured: 0/28F5168

CDC:
  ✅ Status: RUNNING
  ✅ Debezium Connector: cdc-pg_to_mssql_projects_simple-pg-public (RUNNING)
  ✅ Sink Connector: sink-pg_to_mssql_projects_simple-mssql-dbo (RUNNING)
  ✅ Kafka Topic: pg_to_mssql_projects_simple.public.projects_simple
```

## Key Points

1. **LSN is a checkpoint**: It marks "everything before this point was loaded via full load"

2. **CDC starts after LSN**: Debezium only captures changes that happened AFTER the full load LSN

3. **No duplicates**: Because CDC starts from after the full load position, it won't re-capture data that was already loaded

4. **Real-time replication**: Any new INSERT/UPDATE/DELETE in PostgreSQL after the full load will be automatically replicated to SQL Server

5. **Replication slot**: Ensures no data loss and tracks CDC position even if the system restarts

## Monitoring CDC

You can monitor CDC by:
- Checking Kafka topics for messages
- Monitoring replication lag
- Viewing Debezium connector status
- Checking SQL Server for new changes

The system is now continuously replicating changes from PostgreSQL to SQL Server in real-time! 🚀


