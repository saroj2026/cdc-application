# CDC LSN - How CDC Tracks LSN During Real-Time Replication

## What is CDC LSN?

**CDC LSN** refers to the **current LSN position** that CDC (Change Data Capture) is processing during real-time replication. This is different from the **full load LSN** which is captured once after full load completes.

## Two Types of LSN in the System

### 1. Full Load LSN (`full_load_lsn`)
- **Stored**: `pipelines.full_load_lsn` column in database
- **When**: Captured once after full load completes
- **Purpose**: Starting point for CDC to avoid duplicates
- **Example**: `"0/28F5168"`

### 2. CDC LSN (Current Processing Position)
- **Stored**: PostgreSQL replication slot (in source database)
- **When**: Continuously updated as CDC processes changes
- **Purpose**: Tracks current CDC position for lag monitoring
- **Example**: `"0/2A1B2C3"` (always advancing)

## Where CDC LSN is Stored

### 1. PostgreSQL Replication Slot (Primary Storage)

**Location**: PostgreSQL source database system tables

**Table**: `pg_replication_slots`

**Key Fields**:
- `slot_name`: Name of the replication slot (e.g., `{pipeline_name}_slot`)
- `confirmed_flush_lsn`: Last LSN that has been confirmed flushed (CDC position)
- `wal_status`: Status of WAL files
- `active`: Whether slot is currently active

**Query to Check CDC LSN**:
```sql
SELECT 
    slot_name,
    confirmed_flush_lsn AS cdc_lsn,
    pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) AS lag_bytes,
    active
FROM pg_replication_slots
WHERE slot_name = '{pipeline_name}_slot';
```

**What This Shows**:
- `confirmed_flush_lsn`: Current CDC LSN (last processed position)
- `lag_bytes`: Gap between source WAL and CDC position
- `active`: Whether CDC is currently running

### 2. Source Database Current WAL LSN

**Location**: PostgreSQL source database

**Query**: `SELECT pg_current_wal_lsn() AS current_lsn`

**What This Shows**:
- Current WAL position in source database
- This is the "source LSN" - where new changes are being written

### 3. Monitoring Metrics (Calculated)

**Location**: `pipeline_metrics` table (optional, for historical tracking)

**Fields**:
- `source_offset`: Source LSN at time of measurement
- `target_offset`: Processed LSN at time of measurement
- `lag_seconds`: Time-based lag

## How CDC LSN Works

### Flow Diagram

```
1. SOURCE DATABASE
   └─ WAL Position: 0/2A1B2C3 (current)
      └─ New changes written here

2. DEBEZIUM REPLICATION SLOT
   └─ Slot Name: {pipeline}_slot
   └─ confirmed_flush_lsn: 0/2A0F000 (CDC position)
      └─ This is where CDC is currently reading from

3. LAG CALCULATION
   └─ Gap = 0/2A1B2C3 - 0/2A0F000 = 12,288 bytes
      └─ This is the replication lag
```

### Real-Time Updates

1. **Source WAL Advances**: As new transactions occur, `pg_current_wal_lsn()` increases
2. **CDC Processes Changes**: Debezium reads from replication slot
3. **Slot Position Updates**: `confirmed_flush_lsn` advances as CDC confirms processing
4. **Lag Calculated**: Difference between source and CDC LSN = lag

## Code Implementation

### 1. Getting Source LSN (Current WAL)

**File**: `ingestion/connectors/postgresql.py` line 559

```python
def extract_lsn_offset(self, database):
    # Get current WAL LSN (source position)
    cursor.execute("SELECT pg_current_wal_lsn() AS current_lsn")
    current_lsn = result["current_lsn"]  # e.g., "0/2A1B2C3"
    return {"lsn": current_lsn, ...}
```

### 2. Getting CDC LSN (Replication Slot Position)

**File**: `ingestion/connectors/postgresql.py` line 585-603

```python
# Get replication slots information
cursor.execute("""
    SELECT 
        slot_name,
        slot_type,
        active,
        confirmed_flush_lsn,  -- This is the CDC LSN!
        pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) AS lag_bytes
    FROM pg_replication_slots
""")
replication_slots = cursor.fetchall()
```

**Key Field**: `confirmed_flush_lsn` = Current CDC LSN position

### 3. Lag Monitoring

**File**: `ingestion/lag_monitor.py` line 25-76

```python
def calculate_lag(self, source_connection_id, target_connection_id):
    # Get source LSN (current WAL)
    source_lsn_info = self._get_source_lsn(source_connection_id)
    source_lsn = source_lsn_info.get("lsn")  # e.g., "0/2A1B2C3"
    
    # Get CDC LSN (from replication slot)
    # This is done via extract_lsn_offset which queries pg_replication_slots
    
    # Calculate gap
    gap_bytes = pg_wal_lsn_diff(source_lsn, cdc_lsn)
```

## API Endpoints for CDC LSN

### 1. Get LSN Latency

**Endpoint**: `GET /api/v1/monitoring/pipelines/{pipeline_id}/lag`

**Returns**:
```json
{
  "source_lsn": "0/2A1B2C3",      // Current WAL position
  "processed_lsn": "0/2A0F000",    // CDC LSN (from replication slot)
  "lag_bytes": 12288,              // Gap in bytes
  "lag_seconds": 0.5,               // Time-based lag
  "lag_status": "normal"
}
```

**Code**: `ingestion/api.py` - `get_pipeline_lag()` endpoint

### 2. Frontend Display

**File**: `frontend/app/analytics/page.tsx` line 115

```typescript
const currentLsn = await apiClient.getLsnLatency(pipelineId);
// Returns: { sourceLsn, processedLsn, gapBytes, gapMB }
```

## CDC LSN vs Full Load LSN

| Aspect | Full Load LSN | CDC LSN |
|--------|---------------|---------|
| **Stored Where** | `pipelines.full_load_lsn` (database) | `pg_replication_slots.confirmed_flush_lsn` (PostgreSQL) |
| **When Set** | Once, after full load | Continuously updated during CDC |
| **Purpose** | Starting point for CDC | Current processing position |
| **Static/Dynamic** | Static (doesn't change) | Dynamic (always advancing) |
| **Example** | `"0/28F5168"` | `"0/2A0F000"` → `"0/2A1B2C3"` → ... |

## How to Check CDC LSN

### Method 1: Direct SQL Query

```sql
-- Connect to source PostgreSQL database
SELECT 
    slot_name,
    confirmed_flush_lsn AS cdc_lsn,
    pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) AS lag_bytes,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn)) AS lag_size,
    active
FROM pg_replication_slots
WHERE slot_name LIKE '%{pipeline_name}%';
```

### Method 2: API Endpoint

```bash
curl "http://localhost:8000/api/v1/monitoring/pipelines/{pipeline_id}/lag"
```

### Method 3: Frontend Analytics Page

- Navigate to Analytics page
- Select a pipeline
- View "LSN Latency" section
- Shows: Source LSN, Processed LSN, Gap

## Important Notes

### 1. CDC LSN is NOT Stored in Application Database

- CDC LSN is managed by PostgreSQL replication slots
- Application only reads it for monitoring
- Replication slot is the source of truth

### 2. Replication Slot Persistence

- Replication slot persists across CDC restarts
- If CDC stops, slot position is preserved
- When CDC resumes, it continues from slot position

### 3. Lag Calculation

```
Lag = Source LSN - CDC LSN
     = pg_current_wal_lsn() - confirmed_flush_lsn
```

- **Low Lag** (< 1MB): CDC is keeping up
- **Medium Lag** (1-10MB): Some delay, but acceptable
- **High Lag** (> 10MB): CDC is falling behind

## Summary

**CDC LSN** is the current LSN position that CDC is processing, stored in PostgreSQL replication slots as `confirmed_flush_lsn`. It's different from `full_load_lsn` which is a static starting point. CDC LSN continuously advances as CDC processes changes, and the gap between source LSN and CDC LSN represents replication lag.

**Key Takeaway**: CDC LSN is managed by PostgreSQL replication slots, not stored in the application database. The application reads it for monitoring purposes only.


