# Check connector status via SSH using PowerShell
$VPS_HOST = "72.61.233.209"
$VPS_USER = "root"
$VPS_PASS = "segmbp@1100"
$CONNECTOR_NAME = "sink-as400-s3_p-s3-dbo"

Write-Host "======================================================================"
Write-Host "Checking Connector Status via SSH"
Write-Host "======================================================================"

# Create SSH session
$sshSession = New-SSHSession -ComputerName $VPS_HOST -Username $VPS_USER -Password $VPS_PASS -AcceptKey 2>$null

if (-not $sshSession) {
    Write-Host "`nTrying alternative method..."
    
    # Alternative: Use plink or direct SSH command
    $command = "docker exec kafka-connect-cdc curl -s http://localhost:8083/connectors/$CONNECTOR_NAME/status"
    
    # Try using ssh with password (requires ssh client)
    $sshCmd = "echo '$VPS_PASS' | ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST `"$command`""
    
    Write-Host "`nPlease run this command manually on your VPS or use an SSH client:"
    Write-Host "  ssh root@72.61.233.209"
    Write-Host "  docker exec kafka-connect-cdc curl -s http://localhost:8083/connectors/$CONNECTOR_NAME/status"
    
    exit
}

# Execute command
$result = Invoke-SSHCommand -SessionId $sshSession.SessionId -Command "docker exec kafka-connect-cdc curl -s http://localhost:8083/connectors/$CONNECTOR_NAME/status"

Write-Host "`nConnector Status:"
Write-Host $result.Output

Remove-SSHSession -SessionId $sshSession.SessionId | Out-Null



