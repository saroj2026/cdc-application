# PowerShell commands to run on VPS server (if using Windows on VPS, otherwise use bash script)
# Note: These are for reference - VPS is likely Linux, use .sh version instead

Write-Host "=== DOCKER CONTAINERS ==="
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

Write-Host "`n=== KAFKA CONNECT CONTAINER ==="
$kafkaConnectContainer = docker ps --filter "name=kafka-connect" --format "{{.Names}}" | Select-Object -First 1
if ($kafkaConnectContainer) {
    Write-Host "Kafka Connect container: $kafkaConnectContainer"
    Write-Host "`nKafka Connect environment variables:"
    docker exec $kafkaConnectContainer env | Select-String -Pattern "KAFKA|BOOTSTRAP"
}

