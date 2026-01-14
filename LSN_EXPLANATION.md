# LSN (Log Sequence Number) - What It Is and Where It's Stored

## What is LSN?

**LSN (Log Sequence Number)** is a unique identifier that represents a specific position in a database's transaction log (Write-Ahead Log or WAL).

### For PostgreSQL:
- LSN is a position in the **Write-Ahead Log (WAL)**
- Format: `XXXXXXXX/YYYYYYYY` (e.g., `0/15D7E90`)
- Represents the exact byte position in the WAL file
- Used to track replication progress and CDC position

### For SQL Server:
- LSN is a position in the **Transaction Log**
- Format: Different structure than PostgreSQL
- Used similarly for tracking replication progress

## Why LSN is Important for CDC

1. **Prevents Duplicates**: When full load completes, LSN is captured. CDC starts from this LSN, ensuring no duplicate data.

2. **Tracks Progress**: Shows how far CDC has processed changes from the source database.

3. **Resume Capability**: If CDC stops, it can resume from the last processed LSN.

4. **Lag Monitoring**: Compare source LSN vs processed LSN to measure replication lag.

## Where LSN is Stored

### 1. Database Table: `pipelines` table

**Column**: `full_load_lsn` (Text/JSON type)

**Location**: `ingestion/database/models_db.py` line 106

```python
class PipelineModel(Base):
    __tablename__ = "pipelines"
    
    # ... other fields ...
    full_load_lsn = Column(Text, nullable=True)  # LSN captured after full load
    # ... other fields ...
```

**What's Stored**:
- LSN captured **AFTER** full load completes
- This is the WAL position at the moment full load finished
- Format: PostgreSQL LSN string (e.g., `"0/15D7E90"`)

**When It's Set**:
- After full load completes successfully
- Code: `ingestion/cdc_manager.py` line ~138
```python
pipeline.full_load_lsn = full_load_result.get("lsn")
```

### 2. In-Memory Pipeline Object

**Field**: `pipeline.full_load_lsn`

**Location**: `ingestion/models.py` - `Pipeline` class

**What's Stored**:
- Same LSN value as database
- Used during runtime for CDC configuration

### 3. Debezium Replication Slot

**Location**: PostgreSQL database (not in our application database)

**What's Stored**:
- PostgreSQL replication slot maintains its own LSN position
- Slot name format: `{pipeline_name}_slot`
- This is the actual position Debezium is reading from

**How It Works**:
- When Debezium connector starts, it creates/uses a replication slot
- Slot position = Current WAL position when slot was created
- Debezium reads changes from this position forward

## How LSN is Captured

### 1. After Full Load

**Code**: `ingestion/connectors/postgresql.py` - `extract_lsn_offset()` method

```python
def extract_lsn_offset(self, database: Optional[str] = None) -> Dict[str, Any]:
    """Extract LSN (Log Sequence Number) from PostgreSQL."""
    
    # Get current WAL LSN
    cursor.execute("SELECT pg_current_wal_lsn() AS current_lsn")
    result = cursor.fetchone()
    current_lsn = result["current_lsn"]  # e.g., "0/15D7E90"
    
    return {"lsn": current_lsn, ...}
```

**When Called**:
- After full load completes
- Captures the WAL position at that exact moment

### 2. For Monitoring (Source LSN)

**Code**: `ingestion/lag_monitor.py` - `_get_source_lsn()` method

**Purpose**: Get current source database LSN for lag calculation

```python
def _get_source_lsn(self, connection_id: str, database: Optional[str] = None):
    connector = self.connection_service._get_connector(connection)
    lsn_info = connector.extract_lsn_offset(database)
    return {"lsn": lsn_info.get("lsn"), ...}
```

## LSN Usage in CDC

### 1. Snapshot Mode Configuration

**Code**: `ingestion/cdc_manager.py` line ~147

```python
# Set snapshot mode based on full load
snapshot_mode = "schema_only" if pipeline.full_load_lsn else "initial"
```

**What This Means**:
- If `full_load_lsn` exists → Use `"initial_only"` (skip data, only schema)
- If `full_load_lsn` is None → Use `"initial"` (capture all data)

### 2. Debezium Configuration

**Code**: `ingestion/debezium_config.py` line ~151

```python
# If we have LSN from full load, configure starting position
if full_load_lsn:
    logger.info(f"Using full load LSN for PostgreSQL: {full_load_lsn}")
    # Debezium will automatically resume from replication slot position
```

**Note**: Debezium doesn't directly use the LSN value in config. Instead:
- Replication slot position = Current WAL when slot created
- Since slot is created AFTER full load, position is correct

## LSN Monitoring

### Frontend Display

**Location**: `frontend/app/analytics/page.tsx`

**What's Shown**:
- Source LSN: Current WAL position in source database
- Processed LSN: Last LSN processed by CDC
- Gap: Difference between source and processed LSN
- Latency: Time delay in processing

**API Endpoint**: `/api/v1/monitoring/pipelines/{pipeline_id}/lag`

## Database Schema

### PostgreSQL `pipelines` Table

```sql
CREATE TABLE pipelines (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    -- ... other columns ...
    full_load_lsn TEXT,  -- LSN captured after full load
    -- ... other columns ...
);
```

### Example LSN Values

**PostgreSQL**:
- `"0/15D7E90"` - Hexadecimal format
- `"1/2345678"` - Higher position

**SQL Server**:
- Different format (not shown in current codebase)

## Summary

| Aspect | Details |
|--------|---------|
| **What** | Log Sequence Number - position in transaction log |
| **Where Stored** | `pipelines.full_load_lsn` column (PostgreSQL database) |
| **When Captured** | After full load completes |
| **Format** | PostgreSQL: `"0/15D7E90"` (hexadecimal) |
| **Purpose** | Prevent duplicates, track CDC progress, resume capability |
| **Used By** | CDC Manager, Debezium connector, Lag Monitor |

## Related Files

1. **Database Model**: `ingestion/database/models_db.py` (line 106)
2. **LSN Extraction**: `ingestion/connectors/postgresql.py` (line 532)
3. **LSN Usage**: `ingestion/cdc_manager.py` (line 138, 147)
4. **Lag Monitoring**: `ingestion/lag_monitor.py` (line 78)
5. **Frontend Display**: `frontend/app/analytics/page.tsx` (line 53)


