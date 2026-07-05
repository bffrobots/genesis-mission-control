@echo off
REM Genesis Mission Control - Complete Startup (Both Backends)
REM Starts:
REM   - Servo Backend (Port 5000) - Motion Control
REM   - Voice & Chat Server (Port 5001) - AI and commands
REM
REM Usage: Double-click this file or run from command prompt

title Genesis Mission Control - Complete

echo ==================================
echo Genesis Mission Control v2.0
echo Complete Startup
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
    pause
    exit /b 1
)

echo [OK] Python installed
python --version
echo.

REM Check dependencies for both backends
echo Checking dependencies...
python -c "import flask, flask_cors, fastapi, uvicorn, websockets, requests" >nul 2>&1
if errorlevel 1 (
    echo [WARN] Dependencies not found!
    echo.
    echo Please run install-dependencies.bat first, or install manually:
    echo   pip install flask flask-cors fastapi uvicorn websockets requests anthropic openai
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

echo ==================================
echo Starting Both Backends...
echo ==================================
echo.
echo Backend 1: Motion Control (Port 5000)
echo Backend 2: Voice ^& Chat (Port 5001)
echo.
echo Web Interface: http://localhost:8080
echo.
echo Opening two terminal windows...
echo Press Ctrl+C in each window to stop
echo ==================================
echo.

REM Start Motion Control (Servo Backend) in new window
start "Genesis Motion Control - Port 5000" cmd /c "cd /d %~dp0 && call start-genesis.bat"

REM Wait a moment for first server to start
timeout /t 2 /nobreak >nul

REM Start Voice & Chat in new window
start "Genesis Voice ^& Chat - Port 5001" cmd /c "cd /d %~dp0 && call start.bat"

echo.
echo ✅ Both backends started!
echo.
echo   Window 1: Motion Control (Port 5000)
echo   Window 2: Voice ^& Chat (Port 5001)
echo.
echo Close these windows to stop the servers.
echo.
echo Press any key to close this launcher window...
pause >nul
exit
