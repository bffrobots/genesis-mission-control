@echo off
REM Genesis Mission Control - Install Ollama on Windows
REM Downloads and installs Ollama for Windows

echo ================================
echo Install Ollama for Windows
echo ================================
echo.

REM Check if Ollama is already installed
where ollama >nul 2>&1
if not errorlevel 1 (
    echo Ollama is already installed!
    ollama --version
    echo.
    echo To pull llama3.1 model:
    echo   ollama pull llama3.1
    echo.
    pause
    exit /b 0
)

echo Ollama not found. Downloading...
echo.

REM Download Ollama installer
echo Downloading Ollama installer...
curl -L -o "%TEMP%\ollama-setup.exe" https://ollama.com/download/OllamaSetup.exe

if errorlevel 1 (
    echo.
    echo ERROR: Failed to download Ollama
    echo Download manually from: https://ollama.com/download
    pause
    exit /b 1
)

echo.
echo Download complete!
echo.
echo Running installer...
echo.

REM Run installer silently
"%TEMP%\ollama-setup.exe" /SILENT

REM Wait for installation
timeout /t 5 /nobreak >nul

REM Clean up
del "%TEMP%\ollama-setup.exe"

echo.
echo ================================
echo Installation Complete!
echo ================================
echo.
echo Next steps:
echo   1. Ollama should be running in system tray
echo   2. Open Command Prompt and run:
echo      ollama pull llama3.1
echo.
echo Then you can run: start_voice_chat.bat
echo.
pause
