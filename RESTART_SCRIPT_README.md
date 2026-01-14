# Backend Restart Script - Clean State

## Overview

This script restarts the backend server with a clean state, ensuring that:
- All existing processes are stopped
- Port 8000 is released
- Environment variables are set correctly
- Server starts fresh and loads pipelines from database

## Usage

### Windows (PowerShell)
```powershell
powershell -ExecutionPolicy Bypass -File restart_backend_clean.ps1
```

Or simply:
```powershell
.\restart_backend_clean.ps1
```

### Linux/Mac (Bash)
```bash
chmod +x restart_backend_clean.sh
./restart_backend_clean.sh
```

## What It Does

1. **Stops existing backend processes** - Kills any running Python processes running the API
2. **Waits for port release** - Ensures port 8000 is available
3. **Sets environment variables**:
   - `DATABASE_URL` - PostgreSQL connection
   - `KAFKA_CONNECT_URL` - Kafka Connect endpoint
   - `API_HOST`, `API_PORT`, `API_RELOAD`
4. **Starts backend server** - Launches the API in background
5. **Waits for readiness** - Checks if server is responding
6. **Tests server** - Verifies connections and pipelines are accessible

## Testing After Restart

After restarting, test with:
```bash
python test_pipeline_after_restart.py
```

This will:
- Create a fresh pipeline
- Start it immediately (while state is clean)
- Show full load and CDC connector status

## Troubleshooting

### Server Not Starting
- Check if port 8000 is in use: `netstat -ano | findstr :8000` (Windows)
- Check backend logs for errors
- Ensure Python and dependencies are installed

### Pipelines Not Found
- After restart, pipelines exist in database but not in memory
- They will be loaded when you start them via API
- The `start_pipeline` endpoint loads from database automatically

### Kafka Connect Errors
- Verify Kafka Connect is running: `curl http://72.61.233.209:8083/connectors`
- Check if S3 connector is installed
- Review Kafka Connect logs on VPS

## Notes

- The script uses a unique pipeline name with timestamp to avoid conflicts
- Pipelines are persisted in database, so they survive restarts
- In-memory state is cleared on restart, but pipelines are reloaded from DB when started

## Files

- `restart_backend_clean.ps1` - PowerShell script for Windows
- `restart_backend_clean.sh` - Bash script for Linux/Mac
- `test_pipeline_after_restart.py` - Test script to verify after restart


## Overview

This script restarts the backend server with a clean state, ensuring that:
- All existing processes are stopped
- Port 8000 is released
- Environment variables are set correctly
- Server starts fresh and loads pipelines from database

## Usage

### Windows (PowerShell)
```powershell
powershell -ExecutionPolicy Bypass -File restart_backend_clean.ps1
```

Or simply:
```powershell
.\restart_backend_clean.ps1
```

### Linux/Mac (Bash)
```bash
chmod +x restart_backend_clean.sh
./restart_backend_clean.sh
```

## What It Does

1. **Stops existing backend processes** - Kills any running Python processes running the API
2. **Waits for port release** - Ensures port 8000 is available
3. **Sets environment variables**:
   - `DATABASE_URL` - PostgreSQL connection
   - `KAFKA_CONNECT_URL` - Kafka Connect endpoint
   - `API_HOST`, `API_PORT`, `API_RELOAD`
4. **Starts backend server** - Launches the API in background
5. **Waits for readiness** - Checks if server is responding
6. **Tests server** - Verifies connections and pipelines are accessible

## Testing After Restart

After restarting, test with:
```bash
python test_pipeline_after_restart.py
```

This will:
- Create a fresh pipeline
- Start it immediately (while state is clean)
- Show full load and CDC connector status

## Troubleshooting

### Server Not Starting
- Check if port 8000 is in use: `netstat -ano | findstr :8000` (Windows)
- Check backend logs for errors
- Ensure Python and dependencies are installed

### Pipelines Not Found
- After restart, pipelines exist in database but not in memory
- They will be loaded when you start them via API
- The `start_pipeline` endpoint loads from database automatically

### Kafka Connect Errors
- Verify Kafka Connect is running: `curl http://72.61.233.209:8083/connectors`
- Check if S3 connector is installed
- Review Kafka Connect logs on VPS

## Notes

- The script uses a unique pipeline name with timestamp to avoid conflicts
- Pipelines are persisted in database, so they survive restarts
- In-memory state is cleared on restart, but pipelines are reloaded from DB when started

## Files

- `restart_backend_clean.ps1` - PowerShell script for Windows
- `restart_backend_clean.sh` - Bash script for Linux/Mac
- `test_pipeline_after_restart.py` - Test script to verify after restart

