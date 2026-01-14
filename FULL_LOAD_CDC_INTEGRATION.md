# Full Load + CDC Integration Analysis

## Your Question

**"Will it work for full load + CDC?"**

You created:
1. **Full load system** - Copies all existing data
2. **CDC system** - Captures real-time changes
3. **Full load notes the LSN** - Captures WAL position after full load

**Question**: Will they work together to avoid duplicates?

## Current Implementation Flow

### Step-by-Step Process

```
1. User creates pipeline with enable_full_load=True
   ↓
2. CDC Manager starts pipeline
   ↓
3. FULL LOAD PHASE:
   - Copies all data from source to target
   - Creates schemas in target
   - Transfers all rows
   ↓
4. LSN CAPTURE:
   - After full load completes
   - Captures current WAL LSN: pipeline.full_load_lsn
   - This is the position AFTER all full load data was written
   ↓
5. CDC CONNECTOR CREATION:
   - snapshot_mode = "initial_only" (if full_load_lsn exists)
   - This tells Debezium: "Only capture schema, skip data"
   - Creates replication slot (if new) or uses existing
   ↓
6. CDC STARTS:
   - Debezium starts from replication slot position
   - Slot position = Current WAL position (when slot created)
   - Since slot created AFTER full load, it's at the right position
   ↓
7. REAL-TIME REPLICATION:
   - Only NEW changes (after full load LSN) are captured
   - No duplicates from full load data
```

## How It Works

### 1. Full Load Phase

**Code**: `ingestion/cdc_manager.py` lines 124-142

```python
if pipeline.enable_full_load:
    # Run full load
    full_load_result = self._run_full_load(...)
    
    # Capture LSN AFTER full load
    pipeline.full_load_lsn = full_load_result.get("lsn")
```

**What happens**:
- All existing data is copied
- Schemas are created
- After completion, current WAL LSN is captured
- This LSN represents the position AFTER all full load writes

### 2. LSN Capture

**Code**: `ingestion/connectors/postgresql.py` lines 532-645

```python
def extract_lsn_offset(self, database):
    # Gets current WAL LSN
    cursor.execute("SELECT pg_current_wal_lsn() AS current_lsn")
    current_lsn = result["current_lsn"]
    return {"lsn": current_lsn, ...}
```

**What it captures**:
- Current Write-Ahead Log position
- This is the position AFTER full load completed
- All full load data is BEFORE this LSN

### 3. CDC Configuration

**Code**: `ingestion/cdc_manager.py` lines 147-158

```python
# Set snapshot mode based on full load
snapshot_mode = "schema_only" if pipeline.full_load_lsn else "initial"
```

**Code**: `ingestion/debezium_config.py` lines 107-108

```python
# For PostgreSQL, fix snapshot mode
if snapshot_mode in ["schema_only", "never"] and full_load_lsn:
    snapshot_mode = "initial_only"  # Only schema, skip data
```

**What this means**:
- `snapshot.mode = "initial_only"` tells Debezium:
  - ✅ Capture schema (table structure)
  - ❌ Skip data (already loaded via full load)
  - ✅ Start streaming from current position

### 4. Replication Slot Behavior

**How PostgreSQL Replication Slots Work**:

1. **New Slot**:
   - Created at current WAL position
   - Since created AFTER full load, position is correct
   - Starts streaming from this position

2. **Existing Slot**:
   - Uses existing slot position
   - If slot was created before full load, might be at wrong position
   - **Potential issue here!**

## Current Status: ✅ Mostly Works, But...

### ✅ What Works

1. **Full load captures LSN** - ✅ Working
2. **CDC uses `initial_only` mode** - ✅ Working (skips data)
3. **New replication slots** - ✅ Work correctly (created after full load)
4. **No duplicates for new slots** - ✅ Working

### ⚠️ Potential Issue

**Existing Replication Slots**:

If a replication slot already exists (from a previous run):
- Slot position might be BEFORE full load LSN
- This could cause:
  - Duplicate data (if slot position < full load LSN)
  - Or missed data (if slot position > full load LSN)

**Current code doesn't handle this case explicitly.**

## How to Ensure It Works Correctly

### Option 1: Delete and Recreate Slot (Recommended)

Before starting CDC, if full load was done:
1. Delete existing replication slot
2. Create new slot (will be at current position = after full load)
3. Start CDC

**This ensures slot is at the correct position.**

### Option 2: Use LSN to Set Slot Position

PostgreSQL doesn't directly support setting slot position, but:
1. Capture full load LSN
2. Create slot AFTER full load
3. Slot automatically starts from current position (correct)

**This is what current code does, but only for NEW slots.**

### Option 3: Verify Slot Position

Before starting CDC:
1. Check if slot exists
2. If exists, check slot position vs full_load_lsn
3. If position < full_load_lsn, delete and recreate slot

## Recommended Fix

Add slot management to ensure correct position:

```python
def _ensure_slot_position(self, pipeline, source_connection, full_load_lsn):
    """Ensure replication slot is at correct position after full load."""
    slot_name = f"{pipeline.name.lower()}_slot"
    
    # Check if slot exists
    if slot_exists(slot_name):
        slot_position = get_slot_position(slot_name)
        
        # If slot position is before full load LSN, recreate slot
        if slot_position < full_load_lsn:
            logger.warning(f"Slot {slot_name} position is before full load LSN. Recreating...")
            delete_slot(slot_name)
            # New slot will be created at current position (after full load)
```

## Answer to Your Question

### ✅ YES, It Works (with caveat)

**Current Implementation**:
- ✅ Full load captures LSN correctly
- ✅ CDC uses `initial_only` mode (skips data)
- ✅ New slots work correctly
- ⚠️ Existing slots might cause issues

**For New Pipelines**: ✅ Works perfectly
- Full load → Capture LSN → Create slot → Start CDC
- No duplicates, no missed data

**For Existing Pipelines**: ⚠️ Might have issues
- If slot exists from before, position might be wrong
- Need to handle slot recreation

## Recommendation

**Add slot management** to ensure slots are at correct position:

1. After full load, check slot position
2. If slot exists and position < full_load_lsn, delete and recreate
3. This ensures CDC starts from correct position

**Would you like me to implement this fix?**


