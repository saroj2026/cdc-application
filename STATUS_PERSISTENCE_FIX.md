# Pipeline Status Persistence Fix

## Problem
The `public.pipelines` table columns (especially `full_load_status`) were not being updated in the database even though the in-memory pipeline object was being updated correctly.

## Root Cause
The status update in `api.py` was happening immediately after `start_pipeline()` returned, but:
1. The status update tried to read from the in-memory pipeline object
2. The full load was still running, so the status might not be updated yet
3. The status was only being persisted once at the end, not during the full load process

## Solution
Added a `_persist_pipeline_status()` method to `CDCManager` that:
1. Persists pipeline status to the database at key points:
   - When full load starts (IN_PROGRESS)
   - When full load completes (COMPLETED)
   - When full load fails (FAILED)
2. Uses a database session factory set from `api.py`
3. Properly handles enum conversions and error cases

## Changes Made

### 1. `ingestion/cdc_manager.py`
- Added global `_db_session_factory` variable
- Added `set_db_session_factory()` function
- Added `_persist_pipeline_status()` method
- Called `_persist_pipeline_status()` at key points:
  - After setting `full_load_status = IN_PROGRESS`
  - After setting `full_load_status = COMPLETED`
  - After setting `full_load_status = FAILED`

### 2. `ingestion/api.py`
- Set the database session factory: `set_db_session_factory(get_db)`
- This allows `cdc_manager` to persist status to the database

## How It Works

1. When pipeline starts, `start_pipeline()` is called
2. Full load status is set to `IN_PROGRESS` and persisted to DB
3. Full load runs
4. When complete, status is set to `COMPLETED` and persisted to DB
5. If it fails, status is set to `FAILED` and persisted to DB

## Testing

After restarting the backend:
1. Start a pipeline
2. Check the database - `full_load_status` should update:
   - `NOT_STARTED` → `IN_PROGRESS` → `COMPLETED` (or `FAILED`)
3. The `updated_at` timestamp should also update

## Benefits

- ✅ Real-time status updates in database
- ✅ Status persists even if backend restarts
- ✅ Better visibility into pipeline progress
- ✅ Status updates happen at key milestones, not just at the end


## Problem
The `public.pipelines` table columns (especially `full_load_status`) were not being updated in the database even though the in-memory pipeline object was being updated correctly.

## Root Cause
The status update in `api.py` was happening immediately after `start_pipeline()` returned, but:
1. The status update tried to read from the in-memory pipeline object
2. The full load was still running, so the status might not be updated yet
3. The status was only being persisted once at the end, not during the full load process

## Solution
Added a `_persist_pipeline_status()` method to `CDCManager` that:
1. Persists pipeline status to the database at key points:
   - When full load starts (IN_PROGRESS)
   - When full load completes (COMPLETED)
   - When full load fails (FAILED)
2. Uses a database session factory set from `api.py`
3. Properly handles enum conversions and error cases

## Changes Made

### 1. `ingestion/cdc_manager.py`
- Added global `_db_session_factory` variable
- Added `set_db_session_factory()` function
- Added `_persist_pipeline_status()` method
- Called `_persist_pipeline_status()` at key points:
  - After setting `full_load_status = IN_PROGRESS`
  - After setting `full_load_status = COMPLETED`
  - After setting `full_load_status = FAILED`

### 2. `ingestion/api.py`
- Set the database session factory: `set_db_session_factory(get_db)`
- This allows `cdc_manager` to persist status to the database

## How It Works

1. When pipeline starts, `start_pipeline()` is called
2. Full load status is set to `IN_PROGRESS` and persisted to DB
3. Full load runs
4. When complete, status is set to `COMPLETED` and persisted to DB
5. If it fails, status is set to `FAILED` and persisted to DB

## Testing

After restarting the backend:
1. Start a pipeline
2. Check the database - `full_load_status` should update:
   - `NOT_STARTED` → `IN_PROGRESS` → `COMPLETED` (or `FAILED`)
3. The `updated_at` timestamp should also update

## Benefits

- ✅ Real-time status updates in database
- ✅ Status persists even if backend restarts
- ✅ Better visibility into pipeline progress
- ✅ Status updates happen at key milestones, not just at the end

