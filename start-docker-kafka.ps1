# PowerShell script to start Kafka with Docker

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Kafka with Docker" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Docker is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "ERROR: Docker is not running" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again" -ForegroundColor Yellow
    exit 1
}

Write-Host "Docker is installed and running" -ForegroundColor Green
Write-Host ""

# Start services
Write-Host "Starting Kafka services with Docker Compose..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Services started! Waiting for them to be ready..." -ForegroundColor Green
    Start-Sleep -Seconds 30
    
    Write-Host ""
    Write-Host "Checking services..." -ForegroundColor Yellow
    
    # Check Zookeeper
    try {
        $zk = docker ps --filter "name=zookeeper" --format "{{.Status}}"
        if ($zk) {
            Write-Host "  [OK] Zookeeper: $zk" -ForegroundColor Green
        }
    } catch {
        Write-Host "  [ ] Zookeeper: Not running" -ForegroundColor Red
    }
    
    # Check Kafka
    try {
        $kafka = docker ps --filter "name=kafka" --format "{{.Status}}"
        if ($kafka) {
            Write-Host "  [OK] Kafka: $kafka" -ForegroundColor Green
        }
    } catch {
        Write-Host "  [ ] Kafka: Not running" -ForegroundColor Red
    }
    
    # Check Kafka Connect
    Write-Host "  Checking Kafka Connect..." -ForegroundColor Gray
    Start-Sleep -Seconds 15
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8083" -TimeoutSec 10 -ErrorAction Stop
        Write-Host "  [OK] Kafka Connect: Ready!" -ForegroundColor Green
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "All services are ready!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Kafka Connect: http://localhost:8083" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Next step: Run the CDC pipeline:" -ForegroundColor Yellow
        Write-Host "  python start_cdc_after_kafka.py" -ForegroundColor White
        Write-Host ""
    } catch {
        Write-Host "  [ ] Kafka Connect: Still starting (wait 30-60 more seconds)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  Verify manually: http://localhost:8083" -ForegroundColor White
        Write-Host "  Then run: python start_cdc_after_kafka.py" -ForegroundColor White
    }
} else {
    Write-Host ""
    Write-Host "ERROR: Failed to start services" -ForegroundColor Red
    Write-Host "Check logs with: docker-compose logs" -ForegroundColor Yellow
    exit 1
}




