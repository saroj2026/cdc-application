@echo off
REM Copy Debezium connector using plink (Windows)
REM Make sure plink.exe is in your PATH or provide full path

set SERVER=72.61.233.209
set USER=root
set PASSWORD=segmbp@1100

echo ================================================================================
echo Copying Debezium Connector to Container
echo ================================================================================
echo.

REM Check if plink is available
where plink >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: plink.exe not found in PATH
    echo Please install PuTTY or add plink.exe to your PATH
    pause
    exit /b 1
)

echo Connecting to %USER%@%SERVER%...
echo.

REM Run copy script on remote server
plink -ssh %USER%@%SERVER% -pw %PASSWORD% -batch ^
    "CONTAINER=$(docker ps | grep -i connect | awk '{print $1}' | head -1);" ^
    "echo Container: $CONTAINER;" ^
    "echo.;" ^
    "echo Finding connector on host...;" ^
    "CONNECTOR_PATH=$(find /opt/cdc3/connect-plugins -type d -name '*ibmi*' -o -name '*db2*' 2>/dev/null | head -1);" ^
    "if [ -z \"$CONNECTOR_PATH\" ]; then echo 'ERROR: Connector not found at /opt/cdc3/connect-plugins'; exit 1; fi;" ^
    "echo Found: $CONNECTOR_PATH;" ^
    "CONNECTOR_NAME=$(basename $CONNECTOR_PATH);" ^
    "echo Connector name: $CONNECTOR_NAME;" ^
    "echo.;" ^
    "echo Copying to container...;" ^
    "docker cp $CONNECTOR_PATH $CONTAINER:/usr/share/java/plugins/$CONNECTOR_NAME;" ^
    "if [ $? -eq 0 ]; then echo 'Copy successful'; else echo 'Copy failed'; exit 1; fi;" ^
    "echo.;" ^
    "echo Restarting Kafka Connect...;" ^
    "docker restart $CONTAINER;" ^
    "echo Waiting 30 seconds...;" ^
    "sleep 30;" ^
    "echo.;" ^
    "echo Verifying...;" ^
    "curl -s http://localhost:8083/connector-plugins | grep -i 'As400RpcConnector\|Db2Connector' && echo 'SUCCESS: Connector is loaded!' || echo 'WARNING: Connector not found in plugins'"

echo.
echo ================================================================================
echo Done!
echo ================================================================================
pause


