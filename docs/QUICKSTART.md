# 🚀 Quick Start Guide

**Get Genesis Mission Control running in 5 minutes!**

---

## Prerequisites

- ✅ Windows 10/11
- ✅ Python 3.11+ ([Download](https://www.python.org/downloads/))
- ✅ Synthiam ARC installed (for robot control)

---

## Step 1: Install Dependencies (2 minutes)

**Option A: Double-click**
```
src/windows/install-dependencies.bat
```

**Option B: Command line**
```cmd
cd src/windows
pip install fastapi uvicorn websockets requests anthropic openai
```

✅ **Done!** Dependencies installed.

---

## Step 2: (Optional) Enable AI Conversations (30 seconds)

**Skip this step if you only need robot commands** (commands work WITHOUT AI!)

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

## Step 3: Start Server (10 seconds)

**Option A: Double-click**
```
src/windows/start.bat
```

**Option B: Command line**
```cmd
cd src/windows
python voice-chat-server-v2.py
```

✅ **Done!** Server running on http://localhost:5001

---

## Step 4: Test It! (30 seconds)

### Test 1: Health Check

**Browser:** http://localhost:5001/status

**Or Command Prompt:**
```cmd
curl http://localhost:5001/status
```

**Expected:**
```json
{
  "status": "ok",
  "robot": "Genesis",
  "ai": {
    "provider": "anthropic",
    "available": true
  }
}
```

### Test 2: Commands (<1ms!)

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

### Test 3: Conversation (1-2s with AI)

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

### Open Web Interface

**Browser:** http://localhost:8080 (ARC HTTP Server)

Or use the included web interface:
```
web/interface-index.html
```

### Test Voice & Chat

1. Go to Voice & Chat tab
2. Type: "stand up"
3. Press Enter
4. Verify response in <1ms
5. Robot should execute command (if ARC connected)

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

---

## Troubleshooting

### Problem: "Python not found"

**Solution:**
1. Download Python 3.11+ from https://www.python.org/downloads/
2. During installation, check **"Add Python to PATH"**
3. Restart Command Prompt
4. Run: `python --version` to verify

### Problem: "Port 5001 already in use"

**Solution:**
```cmd
REM Find what's using port 5001
netstat -ano | findstr :5001

REM Kill the process (replace PID with actual number)
taskkill /PID <PID> /F

REM Restart server
```

### Problem: "Dependencies not installed"

**Solution:**
1. Right-click `install-dependencies.bat`
2. Select **"Run as administrator"**
3. Wait for installation to complete

### Problem: "ARC HTTP Server not responding"

**Solution:**
1. Open Synthiam ARC
2. Add **HTTP Server Custom** skill
3. Configure port 8080
4. Enable the skill
5. Restart voice chat server

### Problem: Commands work but robot doesn't move

**Check:**
1. ARC is running
2. HTTP Server Custom skill is enabled (port 8080)
3. Auto Position skill is active
4. Variable `$Genesis_Command` is being set (use Variable Watch skill)

---

## Next Steps

✅ Server is running  
✅ Commands work (<1ms)  
✅ Optional: AI conversations work (1-2s)

**Now:**
1. Configure ARC integration (see README.md)
2. Deploy web interface to ARC HTTP Server
3. Test with your robot!

---

## Need Help?

- **Full Documentation:** See `README.md`
- **Troubleshooting:** See `docs/TROUBLESHOOTING.md`
- **Run Diagnostics:** `scripts/diagnose.sh`
- **Open Issue:** GitHub Issues

---

**You're all set!** 🎉  
Commands respond in <1ms - no more 10-20 second timeouts!
