# Quick Restart Guide

## One-Line Restart (Windows)

```powershell
powershell -ExecutionPolicy Bypass -File restart_backend_clean.ps1
```

## One-Line Restart (Linux/Mac)

```bash
./restart_backend_clean.sh
```

## Manual Restart

1. Stop backend:
   ```powershell
   Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process -Force
   ```

2. Wait 3 seconds

3. Start backend:
   ```powershell
   $env:DATABASE_URL="postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest"
   $env:KAFKA_CONNECT_URL="http://72.61.233.209:8083"
   Start-Process python -ArgumentList "-m", "ingestion.api" -WindowStyle Hidden
   ```

4. Test:
   ```bash
   python test_pipeline_after_restart.py
   ```

## Why Restart?

- Clears in-memory state
- Loads fresh from database
- Fixes pipeline "not found" issues
- Ensures clean environment


## One-Line Restart (Windows)

```powershell
powershell -ExecutionPolicy Bypass -File restart_backend_clean.ps1
```

## One-Line Restart (Linux/Mac)

```bash
./restart_backend_clean.sh
```

## Manual Restart

1. Stop backend:
   ```powershell
   Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process -Force
   ```

2. Wait 3 seconds

3. Start backend:
   ```powershell
   $env:DATABASE_URL="postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest"
   $env:KAFKA_CONNECT_URL="http://72.61.233.209:8083"
   Start-Process python -ArgumentList "-m", "ingestion.api" -WindowStyle Hidden
   ```

4. Test:
   ```bash
   python test_pipeline_after_restart.py
   ```

## Why Restart?

- Clears in-memory state
- Loads fresh from database
- Fixes pipeline "not found" issues
- Ensures clean environment

