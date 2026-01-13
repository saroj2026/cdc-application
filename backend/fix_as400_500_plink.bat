@echo off
REM Fix Kafka Connect 500 errors using plink (Windows)
REM Run this on Windows with plink installed

echo ================================================================================
echo Fixing Kafka Connect 500 Errors for AS400
echo ================================================================================
echo.

set VPS_HOST=72.61.233.209
set VPS_USER=root
set VPS_PASSWORD=segmbp@1100

echo Step 1: Finding Kafka Connect container...
plink -ssh %VPS_USER%@%VPS_HOST% -pw %VPS_PASSWORD% "docker ps | grep -i connect | awk '{print $1}' | head -1" > container_id.txt
set /p CONTAINER=<container_id.txt
del container_id.txt

if "%CONTAINER%"=="" (
    echo ERROR: Kafka Connect container not found!
    plink -ssh %VPS_USER%@%VPS_HOST% -pw %VPS_PASSWORD% "docker ps"
    pause
    exit /b 1
)

echo Found container: %CONTAINER%
echo.

echo Step 2: Checking for AS400 connector...
plink -ssh %VPS_USER%@%VPS_HOST% -pw %VPS_PASSWORD% "docker exec %CONTAINER% find /usr/share/java/plugins -type d -name '*ibmi*' -o -name '*db2as400*' 2>nul | head -1" > connector_check.txt
set /p CONNECTOR=<connector_check.txt
del connector_check.txt

if "%CONNECTOR%"=="" (
    echo AS400 connector not found in container
    echo.
    echo Step 3: Checking host path...
    plink -ssh %VPS_USER%@%VPS_HOST% -pw %VPS_PASSWORD% "find /opt/cdc3/connect-plugins -type d -name '*ibmi*' -o -name '*db2as400*' 2>nul | head -1" > host_connector.txt
    set /p HOST_CONNECTOR=<host_connector.txt
    del host_connector.txt
    
    if "%HOST_CONNECTOR%"=="" (
        echo ERROR: Connector not found on host either!
        echo Please download debezium-connector-ibmi first
        pause
        exit /b 1
    )
    
    echo Found connector on host: %HOST_CONNECTOR%
    echo.
    echo Step 4: Copying to container...
    for /f "tokens=*" %%i in ('echo %HOST_CONNECTOR%') do set HOST_PATH=%%i
    for /f %%i in ('echo %HOST_CONNECTOR%') do for %%j in ("%%~ni") do set CONNECTOR_NAME=%%~nj
    
    plink -ssh %VPS_USER%@%VPS_HOST% -pw %VPS_PASSWORD% "docker cp %HOST_CONNECTOR% %CONTAINER%:/usr/share/java/plugins/%CONNECTOR_NAME%"
    
    if errorlevel 1 (
        echo ERROR: Failed to copy connector
        pause
        exit /b 1
    )
    
    echo Copy successful
) else (
    echo AS400 connector found: %CONNECTOR%
)

echo.
echo Step 5: Restarting Kafka Connect...
plink -ssh %VPS_USER%@%VPS_HOST% -pw %VPS_PASSWORD% "docker restart %CONTAINER%"

echo.
echo Waiting 30 seconds for restart...
timeout /t 30 /nobreak >nul

echo.
echo Step 6: Verifying connector is loaded...
plink -ssh %VPS_USER%@%VPS_HOST% -pw %VPS_PASSWORD% "curl -s http://localhost:8083/connector-plugins | grep -i 'As400RpcConnector\|db2as400'"

if errorlevel 1 (
    echo WARNING: Connector may need more time to load
) else (
    echo SUCCESS: Connector is loaded!
)

echo.
echo ================================================================================
echo Done! Try starting the pipeline again: ./quick_start_as400.sh
echo ================================================================================
pause

