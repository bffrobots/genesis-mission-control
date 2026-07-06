# 🚀 Quick Start Guide

**Get Genesis Mission Control running in 5 minutes!**

---

## Prerequisites

- ✅ Windows 10/11
- ✅ Python 3.11+ ([Download](https://www.python.org/downloads/))
- ✅ Synthiam ARC installed (for robot control)

---

## Step 1: Install Dependencies (2 minutes)

**Double-click:**
```
scripts/install-dependencies.bat
```

**Or command line:**
```cmd
cd scripts
pip install -r ../requirements.txt
```

✅ **Done!** Dependencies installed.

---

## Step 2: (Optional) Enable AI Conversations (30 seconds)

**Skip this step if you only need robot commands** (commands work WITHOUT this!)

### Get API Key

1. Go to: https://console.anthropic.com/
2. Sign up / Login
3. Create API key
4. Copy the key (starts with `sk-ant-`)

### Set API Key

**Temporary (current session):**
```cmd
set ANTHROPIC_API_KEY=sk-ant-...
```

**Permanent:**
```cmd
setx ANTHROPIC_API_KEY "sk-ant-..."
```

✅ **Done!** AI conversations enabled.

**Without API key:** Server runs in rule-based mode (FREE, all commands work).

---

## Step 3: Start Services (10 seconds)

### Option A: Start Everything (Recommended)

**Double-click:**
```
scripts/start-all.bat
```

This opens **two windows**:
- Window 1: **Motion Control** (Port 5000) - Servo control
- Window 2: **Voice & Chat** (Port 5001) - AI and commands

### Option B: Start Individually

**Terminal 1 - Motion Control:**
```cmd
cd scripts
start-genesis.bat
```

**Terminal 2 - Voice & Chat:**
```cmd
cd scripts
start.bat
```

✅ **Done!** Both services running.

---

## Step 4: Test It! (30 seconds)

### Test 1: Health Checks

**Motion Control (Port 5000):**
```cmd
curl http://localhost:5000/status
```

**Voice & Chat (Port 5001):**
```cmd
curl http://localhost:5001/status
```

**Expected:** Both return `{"status": "ok", ...}`

### Test 2: Voice Commands (<1ms!)

**Command Prompt:**
```cmd
curl -X POST http://localhost:5001/chat -H "Content-Type: application/json" -d "{\"message\": \"stand up\"}"
```

**Expected (<1ms):**
```json
{
  "response": "Standing up",
  "action": "STAND",
  "latency_ms": 0.1,
  "source": "rule-based"
}
```

### Test 3: AI Conversation (1-2s with API key)

**Command Prompt:**
```cmd
curl -X POST http://localhost:5001/chat -H "Content-Type: application/json" -d "{\"message\": \"What can you do?\"}"
```

**Expected (1-2 seconds):**
```json
{
  "response": "I'm Genesis, a Mini BFF Genesis robot with 18 DOF...",
  "latency_ms": 1847.5,
  "source": "cloud-ai"
}
```

✅ **All tests passed!** 🎉

---

## Step 5: Use with Web Interface

### Deploy Web Interface (One Time)

```cmd
copy web\interface-index.html "%USERPROFILE%\Documents\ARC\HTTP Server Root\index.html"
```

### Open Web Interface

**Browser:** http://localhost:8080

### Test Voice & Chat

1. Go to **Voice & Chat** tab
2. Type: "stand up"
3. Press Enter
4. Verify response in <1ms
5. Robot should execute command (if ARC connected)

### Test Motion Control

1. Go to **Motion Control** tab
2. Move a servo slider
3. Verify robot servo moves
4. Try "Reset All" button

✅ **Working!**

---

## Common Commands

| Say This | Robot Does | Response Time |
|----------|------------|---------------|
| "stand up" | Stands | <1ms ⚡ |
| "sit down" | Sits | <1ms ⚡ |
| "wave hello" | Waves | <1ms ⚡ |
| "do a dance" | Dances | <1ms ⚡ |
| "bow" | Bows | <1ms ⚡ |
| "stop" | Stops all motion | <1ms ⚡ |
| "move servo D0 to 90" | Moves servo | <1ms ⚡ |
| "What can you do?" | AI responds | 1-2s 🤖 |

---

## Troubleshooting

### Problem: "Python not found"

**Solution:**
1. Download Python 3.11+ from https://www.python.org/downloads/
2. During installation, check **"Add Python to PATH"**
3. Restart Command Prompt
4. Run: `python --version` to verify

### Problem: "Port 5000 already in use"

**Solution:**
```cmd
REM Find what's using port 5000
netstat -ano | findstr :5000

REM Kill the process (replace PID with actual number)
taskkill /F /PID <PID>

REM Restart
cd scripts
start-genesis.bat
```

### Problem: "Port 5001 already in use"

**Solution:**
```cmd
REM Find what's using port 5001
netstat -ano | findstr :5001

REM Kill the process
taskkill /F /PID <PID>

REM Restart
cd scripts
start.bat
```

### Problem: "Dependencies not installed"

**Solution:**
1. Right-click `scripts/install-dependencies.bat`
2. Select **"Run as administrator"**
3. Wait for installation to complete

### Problem: "ARC HTTP Server not responding"

**Solution:**
1. Open Synthiam ARC
2. Add **HTTP Server Custom** skill
3. Configure port 8080
4. Enable the skill
5. Restart services

### Problem: Commands work but robot doesn't move

**Check:**
1. ARC is running
2. HTTP Server Custom skill is enabled (port 8080)
3. Auto Position skill is active
4. Variable `$Genesis_Command` is being set (use Variable Watch skill)
5. Servo files exist: `dir "%USERPROFILE%\Documents\ARC\HTTP Server Root\Servo_D*.txt"`

### Problem: AI not working

**Check:**
1. API key is set: `echo %ANTHROPIC_API_KEY%`
2. Internet connection is working
3. API key has quota remaining
4. Commands still work <1ms even without AI (rule-based mode)

---

## Next Steps

✅ Server is running  
✅ Commands work (<1ms)  
✅ Optional: AI conversations work (1-2s)

**Now:**
1. Configure ARC integration (see README.md)
2. Test all motion control features
3. Try voice commands
4. Explore web interface features

---

## Need Help?

- **Full Documentation:** See [README.md](../README.md)
- **Troubleshooting:** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Run Diagnostics:** `scripts/diagnose.sh`
- **Open Issue:** GitHub Issues

---

**You're all set!** 🎉  
Commands respond in <1ms - no more 10-20 second timeouts!
