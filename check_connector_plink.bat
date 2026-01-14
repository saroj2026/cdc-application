@echo off
REM Check Debezium connector using plink (Windows)
REM Make sure plink.exe is in your PATH or provide full path

set SERVER=72.61.233.209
set USER=root
set PASSWORD=segmbp@1100

echo ================================================================================
echo Checking Debezium Connector at /usr/share/java/plugins
echo ================================================================================
echo.

REM Check if plink is available
where plink >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: plink.exe not found in PATH
    echo Please install PuTTY or add plink.exe to your PATH
    echo Download from: https://www.chiark.greenend.org.uk/~sgtatham/putty/
    pause
    exit /b 1
)

echo Connecting to %USER%@%SERVER%...
echo.

REM Run commands on remote server
plink -ssh %USER%@%SERVER% -pw %PASSWORD% -batch ^
    "CONTAINER=$(docker ps | grep -i connect | awk '{print $1}' | head -1);" ^
    "echo Container: $CONTAINER;" ^
    "echo.;" ^
    "echo Checking /usr/share/java/plugins...;" ^
    "docker exec $CONTAINER ls -la /usr/share/java/plugins 2>&1 | head -20;" ^
    "echo.;" ^
    "echo Finding AS400/DB2 connector...;" ^
    "docker exec $CONTAINER find /usr/share/java/plugins -type d -name '*ibmi*' -o -name '*db2as400*' -o -name '*as400*' -o -name '*db2*' 2>/dev/null;" ^
    "echo.;" ^
    "echo Checking if plugin is loaded...;" ^
    "curl -s http://localhost:8083/connector-plugins | grep -i 'As400RpcConnector\|db2as400\|Db2Connector' || echo 'Connector not found in loaded plugins';" ^
    "echo.;" ^
    "echo Summary:;" ^
    "if docker exec $CONTAINER test -d '/usr/share/java/plugins' 2>/dev/null; then echo 'Directory exists'; else echo 'Directory NOT found'; fi"

echo.
echo ================================================================================
echo Done!
echo ================================================================================
pause


