@echo off
REM Genesis Mission Control - Test All Connections
REM Checks ARC, Servo Backend, Ollama, and Voice Chat

echo ================================
echo Connection Test
echo ================================
echo.

REM Test ARC (8080)
echo Testing ARC HTTP Server (8080)...
curl -s http://localhost:8080 >nul 2>&1
if errorlevel 1 (
    echo ❌ ARC: NOT RUNNING
    echo    Start HTTP Server Custom skill in ARC
) else (
    echo ✅ ARC: OK
)

REM Test Camera Stream (8097)
echo Testing Camera Stream (8097)...
curl -s http://localhost:8097/live >nul 2>&1
if errorlevel 1 (
    echo ❌ Camera: NOT RUNNING
    echo    Start Live Stream Broadcast in ARC
) else (
    echo ✅ Camera: OK
)

REM Test Servo Backend (5000)
echo Testing Servo Backend (5000)...
curl -s http://localhost:5000/status >nul 2>&1
if errorlevel 1 (
    echo ❌ Servo Backend: NOT RUNNING
    echo    Run: scripts\start_genesis.bat
) else (
    echo ✅ Servo Backend: OK
)

REM Test Voice Chat (5001)
echo Testing Voice Chat (5001)...
curl -s http://localhost:5001/status >nul 2>&1
if errorlevel 1 (
    echo ❌ Voice Chat: NOT RUNNING
    echo    Run: scripts\start_voice_chat.bat
) else (
    echo ✅ Voice Chat: OK
)

REM Test Ollama (11434)
echo Testing Ollama (11434)...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama: NOT RUNNING
    echo    Start Ollama or run: ollama serve
) else (
    echo ✅ Ollama: OK
)

echo.
echo ================================
echo Full Status:
curl -s http://localhost:5001/status | python -m json.tool 2>nul
echo ================================
echo.
pause
