# Restart Backend Server with Clean State
# This ensures pipelines are loaded fresh from the database

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Restarting Backend with Clean State" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Stop existing backend processes
Write-Host "1. Stopping existing backend processes..." -ForegroundColor Yellow
$processes = Get-Process | Where-Object {$_.ProcessName -eq "python" -and $_.CommandLine -like "*ingestion.api*"}
if ($processes) {
    foreach ($proc in $processes) {
        Write-Host "   Stopping process: $($proc.Id)" -ForegroundColor Gray
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "   [OK] Stopped existing processes" -ForegroundColor Green
} else {
    Write-Host "   [OK] No existing processes found" -ForegroundColor Green
}

# Step 2: Wait for processes to fully terminate
Write-Host ""
Write-Host "2. Waiting for processes to terminate..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Step 3: Check if port 8000 is still in use
Write-Host ""
Write-Host "3. Checking if port 8000 is available..." -ForegroundColor Yellow
$portInUse = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "   [WARNING] Port 8000 is still in use" -ForegroundColor Yellow
    Write-Host "   Waiting additional 5 seconds..." -ForegroundColor Gray
    Start-Sleep -Seconds 5
} else {
    Write-Host "   [OK] Port 8000 is available" -ForegroundColor Green
}

# Step 4: Set environment variables
Write-Host ""
Write-Host "4. Setting environment variables..." -ForegroundColor Yellow
$env:DATABASE_URL = "postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest"
$env:KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
$env:API_HOST = "0.0.0.0"
$env:API_PORT = "8000"
$env:API_RELOAD = "True"
Write-Host "   [OK] Environment variables set" -ForegroundColor Green
Write-Host "      DATABASE_URL: $env:DATABASE_URL" -ForegroundColor Gray
Write-Host "      KAFKA_CONNECT_URL: $env:KAFKA_CONNECT_URL" -ForegroundColor Gray

# Step 5: Start backend server
Write-Host ""
Write-Host "5. Starting backend server..." -ForegroundColor Yellow
$backendProcess = Start-Process python -ArgumentList "-m", "ingestion.api" -WindowStyle Hidden -PassThru
Write-Host "   [OK] Backend process started (PID: $($backendProcess.Id))" -ForegroundColor Green

# Step 6: Wait for server to be ready
Write-Host ""
Write-Host "6. Waiting for server to be ready..." -ForegroundColor Yellow
$maxWait = 30
$waited = 0
$ready = $false

while ($waited -lt $maxWait -and -not $ready) {
    Start-Sleep -Seconds 2
    $waited += 2
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/connections" -TimeoutSec 2 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $ready = $true
        }
    } catch {
        Write-Host "   Waiting... ($waited/$maxWait seconds)" -ForegroundColor Gray
    }
}

if ($ready) {
    Write-Host "   [OK] Server is ready!" -ForegroundColor Green
} else {
    Write-Host "   [WARNING] Server may not be fully ready yet" -ForegroundColor Yellow
    Write-Host "   Check logs or wait a bit longer" -ForegroundColor Gray
}

# Step 7: Test server
Write-Host ""
Write-Host "7. Testing server..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/connections" -TimeoutSec 5
    Write-Host "   [OK] Server check passed" -ForegroundColor Green
    
    $connectionsResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/connections" -TimeoutSec 5
    $connections = ($connectionsResponse.Content | ConvertFrom-Json)
    Write-Host "   [OK] Found $($connections.Count) connections" -ForegroundColor Green
    
    $pipelinesResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/pipelines" -TimeoutSec 5
    $pipelines = ($pipelinesResponse.Content | ConvertFrom-Json)
    Write-Host "   [OK] Found $($pipelines.Count) pipelines in database" -ForegroundColor Green
    
} catch {
    Write-Host "   [ERROR] Server test failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Backend Restarted Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server is running at: http://localhost:8000" -ForegroundColor White
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Note: Pipelines will be loaded from database when you start them." -ForegroundColor Yellow
Write-Host ""



Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Restarting Backend with Clean State" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Stop existing backend processes
Write-Host "1. Stopping existing backend processes..." -ForegroundColor Yellow
$processes = Get-Process | Where-Object {$_.ProcessName -eq "python" -and $_.CommandLine -like "*ingestion.api*"}
if ($processes) {
    foreach ($proc in $processes) {
        Write-Host "   Stopping process: $($proc.Id)" -ForegroundColor Gray
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "   [OK] Stopped existing processes" -ForegroundColor Green
} else {
    Write-Host "   [OK] No existing processes found" -ForegroundColor Green
}

# Step 2: Wait for processes to fully terminate
Write-Host ""
Write-Host "2. Waiting for processes to terminate..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Step 3: Check if port 8000 is still in use
Write-Host ""
Write-Host "3. Checking if port 8000 is available..." -ForegroundColor Yellow
$portInUse = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "   [WARNING] Port 8000 is still in use" -ForegroundColor Yellow
    Write-Host "   Waiting additional 5 seconds..." -ForegroundColor Gray
    Start-Sleep -Seconds 5
} else {
    Write-Host "   [OK] Port 8000 is available" -ForegroundColor Green
}

# Step 4: Set environment variables
Write-Host ""
Write-Host "4. Setting environment variables..." -ForegroundColor Yellow
$env:DATABASE_URL = "postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest"
$env:KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
$env:API_HOST = "0.0.0.0"
$env:API_PORT = "8000"
$env:API_RELOAD = "True"
Write-Host "   [OK] Environment variables set" -ForegroundColor Green
Write-Host "      DATABASE_URL: $env:DATABASE_URL" -ForegroundColor Gray
Write-Host "      KAFKA_CONNECT_URL: $env:KAFKA_CONNECT_URL" -ForegroundColor Gray

# Step 5: Start backend server
Write-Host ""
Write-Host "5. Starting backend server..." -ForegroundColor Yellow
$backendProcess = Start-Process python -ArgumentList "-m", "ingestion.api" -WindowStyle Hidden -PassThru
Write-Host "   [OK] Backend process started (PID: $($backendProcess.Id))" -ForegroundColor Green

# Step 6: Wait for server to be ready
Write-Host ""
Write-Host "6. Waiting for server to be ready..." -ForegroundColor Yellow
$maxWait = 30
$waited = 0
$ready = $false

while ($waited -lt $maxWait -and -not $ready) {
    Start-Sleep -Seconds 2
    $waited += 2
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/connections" -TimeoutSec 2 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $ready = $true
        }
    } catch {
        Write-Host "   Waiting... ($waited/$maxWait seconds)" -ForegroundColor Gray
    }
}

if ($ready) {
    Write-Host "   [OK] Server is ready!" -ForegroundColor Green
} else {
    Write-Host "   [WARNING] Server may not be fully ready yet" -ForegroundColor Yellow
    Write-Host "   Check logs or wait a bit longer" -ForegroundColor Gray
}

# Step 7: Test server
Write-Host ""
Write-Host "7. Testing server..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/connections" -TimeoutSec 5
    Write-Host "   [OK] Server check passed" -ForegroundColor Green
    
    $connectionsResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/connections" -TimeoutSec 5
    $connections = ($connectionsResponse.Content | ConvertFrom-Json)
    Write-Host "   [OK] Found $($connections.Count) connections" -ForegroundColor Green
    
    $pipelinesResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/pipelines" -TimeoutSec 5
    $pipelines = ($pipelinesResponse.Content | ConvertFrom-Json)
    Write-Host "   [OK] Found $($pipelines.Count) pipelines in database" -ForegroundColor Green
    
} catch {
    Write-Host "   [ERROR] Server test failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Backend Restarted Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server is running at: http://localhost:8000" -ForegroundColor White
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Note: Pipelines will be loaded from database when you start them." -ForegroundColor Yellow
Write-Host ""

