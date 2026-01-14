# PowerShell script to stop Kafka Docker services

Write-Host "Stopping Kafka Docker services..." -ForegroundColor Yellow
docker-compose down
Write-Host "Services stopped" -ForegroundColor Green




