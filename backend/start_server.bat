@echo off
echo Starting CDC Pipeline API Server...
echo.

cd /d %~dp0

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Start the server
echo Starting server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
python start_server.py

pause

