# Start Frontend Server
# This script starts the Next.js frontend development server

Write-Host "Starting Frontend Server..." -ForegroundColor Green

# Change to frontend directory
Set-Location "$PSScriptRoot\frontend"

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Start the development server
Write-Host "Starting Next.js dev server on port 3000..." -ForegroundColor Green
npm run dev

