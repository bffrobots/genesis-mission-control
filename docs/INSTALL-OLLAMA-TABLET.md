# Install Ollama on Windows Surface Tablet

Complete guide for installing Ollama and running Genesis Mission Control with full AI conversation.

---

## Prerequisites

- **Windows 10/11** (Surface tablet or any Windows PC)
- **8GB RAM minimum** (16GB recommended for better performance)
- **Python 3.11+** installed
- **Internet connection** (for downloading Ollama and models)

---

## Step 1: Install Ollama

### Option A: Automatic Installer (Recommended)

1. **Download Ollama:**
   - Go to: https://ollama.com/download
   - Click "Download for Windows"
   - File: `OllamaSetup.exe` (~150MB)

2. **Run Installer:**
   - Double-click `OllamaSetup.exe`
   - Click "Install"
   - Wait for installation (~2-3 minutes)
   - Ollama will start automatically in system tray

3. **Verify Installation:**
   ```cmd
   ollama --version
   ```
   Should show version number (e.g., `ollama version 0.1.45`)

### Option B: Using Script

```cmd
cd genesis-mission-control
scripts\INSTALL_OLLAMA_WINDOWS.bat
```

---

## Step 2: Pull llama3.1 Model

**Open Command Prompt:**

```cmd
ollama pull llama3.1
```

**Expected Output:**
```
pulling manifest
pulling llama3.1... [====================] 100%
success
```

**Download Size:** ~4.7GB  
**Time:** 5-20 minutes (depends on internet speed)

**Alternative Models (smaller, faster for tablets):**

```cmd
# Smaller model (2.3GB, faster)
ollama pull llama3.2:1b

# Medium model (4GB, good balance)
ollama pull llama3.2:3b

# Recommended for tablets with 8GB RAM
ollama pull llama3.2
```

---

## Step 3: Verify Ollama is Running

**Check System Tray:**
- Look for Ollama icon (llama head) in system tray
- Right-click → "Show Ollama" to open status window

**Test in Command Prompt:**
```cmd
ollama list
```

**Expected Output:**
```
NAME          ID           SIZE
llama3.1      46e0c10c039e  4.7 GB
```

**Test Connection:**
```cmd
curl http://localhost:11434/api/tags
```

**Expected Output:**
```json
{"models":[{"name":"llama3.1","size":4700000000}]}
```

---

## Step 4: Install Python Dependencies

```cmd
cd genesis-mission-control
pip install -r requirements.txt
```

**Required Packages:**
- `fastapi` - API framework
- `uvicorn` - ASGI server
- `requests` - HTTP client
- `flask` - Web server (servo backend)
- `websockets` - WebSocket support

---

## Step 5: Start Genesis Services

### Terminal 1 - Servo Backend

```cmd
scripts\start_genesis.bat
```

**Expected Output:**
```
================================
Genesis Motor Control Backend
Mini BFF Genesis (18 DOF)
================================
Listening on http://localhost:5000
```

### Terminal 2 - Voice & Chat

```cmd
scripts\start_voice_chat.bat
```

**Expected Output:**
```
============================================================
🚀 Genesis Voice & Chat Server
Optimized for Tablet PC
============================================================
✅ Ollama detected: http://localhost:11434
📦 Model loaded: llama3.1
⏱️  Ollama Timeout: 120s (connect: 10s)
...
Listening on http://0.0.0.0:5001
```

---

## Step 6: Test AI Conversation

### Open Web Interface

```
http://localhost:8080
```

### Test Commands

**1. Rule-Based (Instant Response):**
```
Type: "stand"
Response: "Executing stand..."
Robot: STANDS ✅
```

**2. AI Conversation (5-30 seconds on tablet):**
```
Type: "What can you do?"
Response: "I'm Genesis, a humanoid robot. I can stand, sit, wave, dance, bow, and walk. I can also move individual servos and navigate to different locations. How can I help you today?"
```

**3. Navigation:**
```
Type: "Navigate to the kitchen"
Response: "Navigating to kitchen"
Robot: Starts walking ✅
```

---

## Troubleshooting

### Ollama Not Running

**Symptom:** "Ollama not available" error

**Fix:**
```cmd
# Start Ollama manually
ollama serve

# Or restart from system tray
# Right-click Ollama icon → Quit
# Then open Ollama from Start Menu
```

### Model Not Found

**Symptom:** "model 'llama3.1' not found"

**Fix:**
```cmd
ollama pull llama3.1
```

### Timeout Errors

**Symptom:** "Response taking too long"

**Fix:**
1. Use smaller model:
   ```cmd
   ollama pull llama3.2:1b
   ```

2. Increase timeout (edit `.env`):
   ```
   OLLAMA_TIMEOUT=180
   ```

3. Close other applications (free up RAM)

### Out of Memory

**Symptom:** Ollama crashes or system slows down

**Fix:**
1. Use smaller model:
   ```cmd
   ollama pull llama3.2:1b  # Only 1.3GB
   ```

2. Close browser tabs and other apps

3. Restart Ollama:
   ```cmd
   # In system tray: Right-click Ollama → Quit
   ollama serve
   ```

### Slow Response Times

**Normal for Tablets:**
- llama3.1 (4.7GB): 10-30 seconds
- llama3.2:3b (4GB): 5-15 seconds
- llama3.2:1b (1.3GB): 2-8 seconds

**To Improve Speed:**
1. Use smaller model
2. Close other applications
3. Plug in charger (tablets throttle on battery)
4. Set power mode to "Best Performance"

---

## Performance Tips for Surface Tablet

### Recommended Settings

| Surface Model | RAM | Recommended Model | Expected Response |
|---------------|-----|-------------------|-------------------|
| Surface Go | 8GB | llama3.2:1b | 5-10 seconds |
| Surface Pro 7 | 8GB | llama3.2:1b | 3-8 seconds |
| Surface Pro 8 | 16GB | llama3.2:3b | 3-6 seconds |
| Surface Pro 9 | 16GB+ | llama3.1 | 5-10 seconds |

### Power Settings

1. **Plug in charger** - AI inference drains battery fast
2. **Set power mode:** Settings → System → Power → Best Performance
3. **Close background apps** - Free up RAM for Ollama

### Thermal Management

Surface tablets can throttle under load:
- Use on hard surface (not on lap/blanket)
- Consider cooling pad for extended use
- Take breaks between heavy AI sessions

---

## Environment Variables (Optional)

Create `.env` file in `genesis-mission-control` folder:

```bash
# Ollama Configuration
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
OLLAMA_TIMEOUT=120
OLLAMA_CONNECT_TIMEOUT=10

# Server Configuration
VOICE_CHAT_PORT=5001
SERVO_BACKEND_PORT=5000
ARC_HTTP_URL=http://localhost:8080
```

---

## Quick Reference

### Start Everything

```cmd
# Terminal 1
scripts\start_genesis.bat

# Terminal 2
scripts\start_voice_chat.bat

# Browser
http://localhost:8080
```

### Test Commands

```cmd
# Check Ollama
ollama list

# Check connections
curl http://localhost:5001/status

# Test chat
curl -X POST http://localhost:5001/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"hello\"}"
```

### Stop Everything

```cmd
# In each terminal: Ctrl+C

# Stop Ollama
# System tray → Right-click Ollama → Quit
```

---

## Next Steps

After successful installation:

1. ✅ Test all robot commands
2. ✅ Try AI conversation
3. ✅ Test voice chat via web interface
4. ✅ Deploy to GitHub
5. ✅ Share with community

---

## Resources

- **Ollama Download:** https://ollama.com/download
- **Ollama Models:** https://ollama.com/library
- **Genesis GitHub:** https://github.com/bffrobots/genesis-mission-control
- **Support:** https://github.com/bffrobots/genesis-mission-control/issues

---

**Last Updated:** June 30, 2026  
**Version:** 1.0.0
