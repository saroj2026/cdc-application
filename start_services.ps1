# PowerShell script to start both backend and frontend

Write-Host "🚀 Starting CDC Application Services..." -ForegroundColor Cyan
Write-Host ""

# Check if backend is already running
Write-Host "1. Checking backend status..." -ForegroundColor Yellow
$backendRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Backend is already running" -ForegroundColor Green
        $backendRunning = $true
    }
} catch {
    Write-Host "   ⚠️  Backend is not running" -ForegroundColor Yellow
}

# Start backend if not running
if (-not $backendRunning) {
    Write-Host ""
    Write-Host "2. Starting backend server..." -ForegroundColor Yellow
    Write-Host "   Command: python -m uvicorn ingestion.api:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Gray
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python -m uvicorn ingestion.api:app --reload --host 0.0.0.0 --port 8000"
    
    Write-Host "   ✅ Backend started in new window" -ForegroundColor Green
    Write-Host "   ⏳ Waiting 5 seconds for backend to initialize..." -ForegroundColor Gray
    Start-Sleep -Seconds 5
} else {
    Write-Host "   ℹ️  Backend already running, skipping..." -ForegroundColor Gray
}

# Check if frontend is already running
Write-Host ""
Write-Host "3. Checking frontend status..." -ForegroundColor Yellow
$frontendRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Frontend is already running" -ForegroundColor Green
        $frontendRunning = $true
    }
} catch {
    Write-Host "   ⚠️  Frontend is not running" -ForegroundColor Yellow
}

# Check if Node.js is available
Write-Host ""
Write-Host "4. Checking Node.js..." -ForegroundColor Yellow
$nodeAvailable = $false
try {
    $nodeVersion = node --version 2>$null
    if ($nodeVersion) {
        Write-Host "   ✅ Node.js found: $nodeVersion" -ForegroundColor Green
        $nodeAvailable = $true
    }
} catch {
    Write-Host "   ❌ Node.js not found" -ForegroundColor Red
}

# Start frontend if not running
if (-not $frontendRunning) {
    if ($nodeAvailable) {
        Write-Host ""
        Write-Host "5. Starting frontend server..." -ForegroundColor Yellow
        Write-Host "   Command: cd frontend; npm run dev" -ForegroundColor Gray
        
        # Check if node_modules exists
        if (-not (Test-Path "frontend\node_modules")) {
            Write-Host "   📦 Installing frontend dependencies (this may take a few minutes)..." -ForegroundColor Yellow
            Push-Location frontend
            npm install
            Pop-Location
        }
        
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run dev"
        
        Write-Host "   ✅ Frontend started in new window" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "   ❌ Cannot start frontend: Node.js is not installed" -ForegroundColor Red
        Write-Host "   Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ℹ️  Frontend already running, skipping..." -ForegroundColor Gray
}

Write-Host ""
Write-Host "✅ Services started!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Access URLs:" -ForegroundColor Cyan
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   Frontend UI: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "💡 Both services are running in separate windows." -ForegroundColor Gray
Write-Host "   Close those windows to stop the services." -ForegroundColor Gray
