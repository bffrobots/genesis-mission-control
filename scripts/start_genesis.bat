@echo off
REM Genesis Mission Control - Startup Script (Windows)
REM Runs servo control backend

echo ================================
echo Genesis Mission Control
echo Servo Backend (Windows)
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

echo Starting servo backend...
echo Listening on: http://localhost:5000
echo ARC HTTP Server: http://localhost:8080
echo.

REM Change to script directory
cd /d "%~dp0"

REM Start the backend
python main.py

pause
