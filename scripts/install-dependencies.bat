@echo off
REM Genesis Mission Control - Windows Dependency Installer
REM Installs all required Python packages for both backends:
REM   - Servo Backend (Port 5000): Flask, flask-cors
REM   - Voice & Chat Server (Port 5001): FastAPI, uvicorn, etc.
REM
REM Usage: Double-click this file or run from command prompt
REM Administrator privileges may be required

title Install Genesis Mission Control Dependencies

echo ==================================
echo Genesis Mission Control v2.0
echo Dependency Installer
echo ==================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3 not found!
    echo.
    echo Please install Python 3.11 or later from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

REM Check if running as administrator (needed for system-wide install)
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running as administrator
    set INSTALL_MODE=--break-system-packages
) else (
    echo [INFO] Not running as administrator
    echo        If installation fails, right-click this file and "Run as administrator"
    echo.
    set INSTALL_MODE=--break-system-packages
)

REM Upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
echo [OK] pip upgraded
echo.

REM Install all dependencies
echo Installing dependencies...
echo This may take a few minutes...
echo.

pip install flask flask-cors fastapi uvicorn websockets requests %INSTALL_MODE% --quiet
if errorlevel 1 (
    echo ERROR: Failed to install core dependencies
    pause
    exit /b 1
)
echo [OK] Core dependencies installed (Flask, FastAPI, etc.)

pip install anthropic openai %INSTALL_MODE% --quiet
if errorlevel 1 (
    echo [WARN] Failed to install AI libraries (anthropic, openai)
    echo        Server will run in rule-based mode only
    echo        To enable AI, install manually: pip install anthropic openai
) else (
    echo [OK] AI libraries installed (anthropic, openai)
)

echo.
echo ==================================
echo Installation Complete!
echo ==================================
echo.
echo Next steps:
echo   1. (Optional) Set AI API key for conversation capability:
echo      setx ANTHROPIC_API_KEY "sk-ant-..."
echo.
echo   2. Start both backends:
echo      start-all.bat
echo.
echo   3. Or start individually:
echo      start-servo-backend.bat   (Port 5000 - Motion control)
echo      start.bat                 (Port 5001 - Voice ^& Chat)
echo.
echo   4. Open browser to:
echo      http://localhost:8080
echo.
echo ==================================
echo.
pause
