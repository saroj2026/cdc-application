# Restart Backend and Test Full Load Flow

## ✅ Fixes Applied

All fixes have been implemented in `ingestion/cdc_manager.py`:
- Schema creation now fails fast (raises error instead of continuing)
- Enhanced logging with "Step 0", "Step 1", "Step 2" prefixes
- Better error handling with `FullLoadError`
- Status persistence at each critical point

## 🔄 Restart Backend

**IMPORTANT**: The backend needs to be restarted to load the new code changes.

### Steps:

1. **Stop the current backend** (if running):
   - Press `Ctrl+C` in the terminal where backend is running
   - Or kill the process

2. **Start the backend**:
   ```bash
   cd seg-cdc-application
   python -m uvicorn ingestion.api:app --host 0.0.0.0 --port 8000
   ```

3. **Verify backend is running**:
   - Check http://localhost:8000/health
   - Should return `{"status": "healthy"}`

## 🧪 Test the Pipeline

### Option 1: Use the UI
1. Open the frontend (usually http://localhost:3000)
2. Navigate to Pipelines
3. Find your pipeline (e.g., `final_test2` or `final_test`)
4. Click "Stop" if it's running
5. Click "Start" to start the pipeline
6. Monitor the logs in the backend terminal

### Option 2: Use API directly
```bash
# List pipelines
curl http://localhost:8000/api/pipelines

# Stop pipeline (replace PIPELINE_ID)
curl -X POST http://localhost:8000/api/pipelines/PIPELINE_ID/stop

# Start pipeline (replace PIPELINE_ID)
curl -X POST http://localhost:8000/api/pipelines/PIPELINE_ID/start
```

### Option 3: Use the test script
```bash
cd seg-cdc-application
python test_full_load_flow.py
```

## 📋 What to Look For

### In Backend Logs:

You should see clear step-by-step progress:

```
Step 0: Auto-creating target schema/tables for pipeline: final_test2
Creating target schema: dbo in database: cdctest
✓ Created target schema: dbo
Creating target table: projects_simple (from source: projects_simple)
✓ Created target table: projects_simple
✓ Schema creation completed: 1 tables ready, 0 failed
Step 0: Target schema/tables created successfully

Step 1: Starting full load for pipeline: final_test2 (mode: full_load_and_cdc)
Step 1: Source: cdctest.public, Tables: ['projects_simple']
Step 1: Target: cdctest.dbo
Step 1: Full load status set to IN_PROGRESS and persisted to database
Initializing data transfer...
Transferring 1 table(s): ['projects_simple']
Transfer settings: schema=True, data=True, batch_size=10000
Transfer completed: 1 successful, 0 failed
Step 1: Full load completed successfully!
Step 1: Tables transferred: 1, Total rows: X, LSN: ...
Step 1: Full load status set to COMPLETED and persisted to database

Step 2: Starting CDC setup for pipeline: final_test2 (mode: full_load_and_cdc)
Step 2: Full load completed, now setting up CDC connectors
...
```

### In Database:

Check the `pipelines` table in PostgreSQL (`cdctest` database):

```sql
SELECT 
    name,
    status,
    full_load_status,
    cdc_status,
    full_load_completed_at,
    updated_at
FROM pipelines
WHERE name = 'final_test2';
```

Expected progression:
- `full_load_status`: `NOT_STARTED` → `IN_PROGRESS` → `COMPLETED`
- `cdc_status`: `NOT_STARTED` → `STARTING` → `RUNNING` (if CDC enabled)
- `full_load_completed_at`: Should be set when full load completes

## ✅ Success Criteria

1. **Schema Creation**:
   - ✓ Schema and tables created in target database
   - ✓ No errors in logs
   - ✓ Clear "Step 0" completion message

2. **Full Load**:
   - ✓ Data transferred successfully
   - ✓ Row counts match between source and target
   - ✓ Status updated to `COMPLETED` in database
   - ✓ `full_load_completed_at` timestamp set

3. **CDC** (if enabled):
   - ✓ CDC starts only after full load completes
   - ✓ Debezium connector created
   - ✓ Sink connector created
   - ✓ CDC status set to `RUNNING`

## 🐛 Troubleshooting

### If schema creation fails:
- Check target database connection
- Verify target database user has CREATE permissions
- Check logs for specific error message

### If full load fails:
- Check source database has data
- Verify schema matches between source and target
- Check logs for transfer errors
- Verify target table was created correctly

### If status not updating in database:
- Verify backend was restarted after code changes
- Check database connection in backend logs
- Verify `_persist_pipeline_status` is being called (check logs)

## 📝 Notes

- The backend must be restarted for changes to take effect
- Schema creation now fails fast - pipeline will stop if schema creation fails
- Full load will only proceed if schema creation succeeds
- CDC will only start if full load completes successfully
- All status updates are persisted to database at each step


## ✅ Fixes Applied

All fixes have been implemented in `ingestion/cdc_manager.py`:
- Schema creation now fails fast (raises error instead of continuing)
- Enhanced logging with "Step 0", "Step 1", "Step 2" prefixes
- Better error handling with `FullLoadError`
- Status persistence at each critical point

## 🔄 Restart Backend

**IMPORTANT**: The backend needs to be restarted to load the new code changes.

### Steps:

1. **Stop the current backend** (if running):
   - Press `Ctrl+C` in the terminal where backend is running
   - Or kill the process

2. **Start the backend**:
   ```bash
   cd seg-cdc-application
   python -m uvicorn ingestion.api:app --host 0.0.0.0 --port 8000
   ```

3. **Verify backend is running**:
   - Check http://localhost:8000/health
   - Should return `{"status": "healthy"}`

## 🧪 Test the Pipeline

### Option 1: Use the UI
1. Open the frontend (usually http://localhost:3000)
2. Navigate to Pipelines
3. Find your pipeline (e.g., `final_test2` or `final_test`)
4. Click "Stop" if it's running
5. Click "Start" to start the pipeline
6. Monitor the logs in the backend terminal

### Option 2: Use API directly
```bash
# List pipelines
curl http://localhost:8000/api/pipelines

# Stop pipeline (replace PIPELINE_ID)
curl -X POST http://localhost:8000/api/pipelines/PIPELINE_ID/stop

# Start pipeline (replace PIPELINE_ID)
curl -X POST http://localhost:8000/api/pipelines/PIPELINE_ID/start
```

### Option 3: Use the test script
```bash
cd seg-cdc-application
python test_full_load_flow.py
```

## 📋 What to Look For

### In Backend Logs:

You should see clear step-by-step progress:

```
Step 0: Auto-creating target schema/tables for pipeline: final_test2
Creating target schema: dbo in database: cdctest
✓ Created target schema: dbo
Creating target table: projects_simple (from source: projects_simple)
✓ Created target table: projects_simple
✓ Schema creation completed: 1 tables ready, 0 failed
Step 0: Target schema/tables created successfully

Step 1: Starting full load for pipeline: final_test2 (mode: full_load_and_cdc)
Step 1: Source: cdctest.public, Tables: ['projects_simple']
Step 1: Target: cdctest.dbo
Step 1: Full load status set to IN_PROGRESS and persisted to database
Initializing data transfer...
Transferring 1 table(s): ['projects_simple']
Transfer settings: schema=True, data=True, batch_size=10000
Transfer completed: 1 successful, 0 failed
Step 1: Full load completed successfully!
Step 1: Tables transferred: 1, Total rows: X, LSN: ...
Step 1: Full load status set to COMPLETED and persisted to database

Step 2: Starting CDC setup for pipeline: final_test2 (mode: full_load_and_cdc)
Step 2: Full load completed, now setting up CDC connectors
...
```

### In Database:

Check the `pipelines` table in PostgreSQL (`cdctest` database):

```sql
SELECT 
    name,
    status,
    full_load_status,
    cdc_status,
    full_load_completed_at,
    updated_at
FROM pipelines
WHERE name = 'final_test2';
```

Expected progression:
- `full_load_status`: `NOT_STARTED` → `IN_PROGRESS` → `COMPLETED`
- `cdc_status`: `NOT_STARTED` → `STARTING` → `RUNNING` (if CDC enabled)
- `full_load_completed_at`: Should be set when full load completes

## ✅ Success Criteria

1. **Schema Creation**:
   - ✓ Schema and tables created in target database
   - ✓ No errors in logs
   - ✓ Clear "Step 0" completion message

2. **Full Load**:
   - ✓ Data transferred successfully
   - ✓ Row counts match between source and target
   - ✓ Status updated to `COMPLETED` in database
   - ✓ `full_load_completed_at` timestamp set

3. **CDC** (if enabled):
   - ✓ CDC starts only after full load completes
   - ✓ Debezium connector created
   - ✓ Sink connector created
   - ✓ CDC status set to `RUNNING`

## 🐛 Troubleshooting

### If schema creation fails:
- Check target database connection
- Verify target database user has CREATE permissions
- Check logs for specific error message

### If full load fails:
- Check source database has data
- Verify schema matches between source and target
- Check logs for transfer errors
- Verify target table was created correctly

### If status not updating in database:
- Verify backend was restarted after code changes
- Check database connection in backend logs
- Verify `_persist_pipeline_status` is being called (check logs)

## 📝 Notes

- The backend must be restarted for changes to take effect
- Schema creation now fails fast - pipeline will stop if schema creation fails
- Full load will only proceed if schema creation succeeds
- CDC will only start if full load completes successfully
- All status updates are persisted to database at each step

