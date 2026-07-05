@echo off
REM Genesis Voice & Chat Server v2.0 - Windows Launcher
REM Fast Hybrid Architecture: Cloud AI + Rule-based fallback
REM 
REM Usage: Double-click this file or run from command prompt
REM
REM Prerequisites:
REM   1. Python 3.11+ installed
REM   2. Dependencies installed (run install-dependencies.bat first)
REM   3. Optional: ANTHROPIC_API_KEY set for AI conversations

title Genesis Voice ^& Chat Server v2.0

echo ==================================
echo Genesis Voice ^& Chat Server v2.0
echo Fast Hybrid Architecture
echo ==================================
echo.

REM Change to the directory where this batch file is located
cd /d "%~dp0"

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3 not found!
    echo.
    echo Please install Python 3.11 or later from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [OK] Python installed
python --version
echo.

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import fastapi, uvicorn, websockets, requests" >nul 2>&1
if errorlevel 1 (
    echo [WARN] Dependencies not found!
    echo.
    echo Please run install-dependencies.bat first, or install manually:
    echo   pip install fastapi uvicorn websockets requests anthropic openai
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)
echo [OK] All dependencies installed
echo.

REM Check AI configuration
echo AI Provider Configuration:
if not "%ANTHROPIC_API_KEY%"=="" (
    echo [OK] Anthropic API key found (Claude - FAST)
) else if not "%OPENAI_API_KEY%"=="" (
    echo [OK] OpenAI API key found (GPT - FAST)
) else (
    echo [INFO] No API key found - running in RULE-BASED MODE only
    echo        Commands will work instantly, but no AI conversation.
)
echo.

REM Check ARC HTTP Server
echo Checking ARC HTTP Server...
curl -s http://localhost:8080/get.html?var=$Genesis_Status >nul 2>&1
if errorlevel 1 (
    echo [WARN] ARC HTTP Server not responding on port 8080
    echo        Robot commands will be logged but not executed.
    echo        Make sure Synthiam ARC is running with HTTP Server Custom skill.
) else (
    echo [OK] ARC HTTP Server detected on port 8080
)
echo.

REM Start server
echo ==================================
echo Starting Genesis Voice ^& Chat Server v2.0...
echo.
echo   Web Interface: http://localhost:5001
echo   WebSocket: ws://localhost:5001/ws/chat
echo.
echo Press Ctrl+C to stop
echo ==================================
echo.

REM Run voice-chat-server-v2.py from same directory
python voice-chat-server-v2.py
if errorlevel 1 (
    echo.
    echo Server exited with error.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)
