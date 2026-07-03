@echo off
REM Genesis Mission Control - Voice & Chat Server (Windows)
REM Runs on Windows with Ollama installed natively

echo ================================
echo Genesis Voice ^& Chat Server
echo Windows Native Version
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

echo Python found!
python --version
echo.

REM Check if Ollama is running
echo Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Ollama is not running!
    echo.
    echo To start Ollama:
    echo   1. Open Ollama application
    echo   2. Or run: ollama serve
    echo.
    echo Starting anyway...
    echo.
) else (
    echo Ollama is running
    echo.
)

REM Change to script directory
cd /d "%~dp0.."

REM Start the voice chat server
echo Starting voice-chat-server.py...
echo Listening on: http://localhost:5001
echo Ollama: http://localhost:11434
echo.

python scripts/voice-chat-server.py

pause
