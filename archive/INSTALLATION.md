# Installation Guide

## Quick Start

### Prerequisites

1. **Windows 10/11** with WSL2 installed
2. **Synthiam ARC** v4.2.1 or later
3. **Python 3.11+** (Windows and WSL)
4. **Ollama** (for AI chat)

### Step 1: Clone Repository

```bash
git clone https://github.com/bffrobots/genesis-mission-control.git
cd genesis-mission-control
```

### Step 2: Install Dependencies

**Windows (Servo Backend):**
```cmd
cd genesis-mission-control
pip install -r requirements.txt
```

**WSL (Voice & Chat):**
```bash
cd genesis-mission-control
pip install -r requirements.txt
```

**Ollama (WSL or Windows):**
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull model
ollama pull llama3.1
```

### Step 3: Configure ARC

1. **Open ARC** (Synthiam application)
2. **Add these skills:**
   - HTTP Server Custom (port 8080)
   - Camera Device (your USB camera)
   - Live Stream Broadcast (port 8097)
   - Auto Position (for servo control)
3. **Configure HTTP Server Custom:**
   - Root Directory: `[Your choice]`
   - Port: 8080
   - Enable: ✓

### Step 4: Deploy Web Interface

Copy web interface to ARC HTTP Server Root:

```bash
cp web/index.html "/mnt/c/Users/YOUR_USERNAME/Documents/ARC/HTTP Server Root/index.html"
```

### Step 5: Start Services

**Terminal 1 - Windows (Servo Backend):**
```cmd
cd genesis-mission-control
scripts\start_genesis.bat
```

**Terminal 2 - WSL (Voice & Chat):**
```bash
cd genesis-mission-control
./scripts/start_genesis.sh
```

**In ARC:**
- Ensure HTTP Server Custom is running (port 8080)
- Ensure Live Stream Broadcast is running (port 8097)

### Step 6: Access Web Interface

Open browser: **http://localhost:8080**

You should see Genesis Mission Control with all tabs functional.

---

## Manual Setup (Alternative)

### Windows Backend

```cmd
cd genesis-mission-control
python scripts/main.py
```

Expected output:
```
================================
Genesis Motor Control Backend
Mini BFF Genesis (18 DOF)
================================
Starting HTTP server...
Listening on http://localhost:5000
```

### WSL Voice & Chat

```bash
cd genesis-mission-control
python scripts/voice-chat-server.py
```

Expected output:
```
🚀 Genesis Voice & Chat Server
Listening on http://localhost:5001
Ollama: http://localhost:11434
```

---

## Verification

### Check All Services

```bash
# Run diagnostic script
./scripts/diagnose.sh
```

Or manually check each service:

**1. HTTP Server (8080):**
```bash
curl -I http://localhost:8080
# Should return: HTTP/1.1 200 OK
```

**2. Camera Stream (8097):**
```bash
curl -I http://localhost:8097/live
# Should return: HTTP/1.1 200 OK
```

**3. Servo Backend (5000):**
```bash
curl http://localhost:5000/status
# Should return: {"status": "ok"}
```

**4. Voice Chat (5001):**
```bash
curl http://localhost:5001/status
# Should return: {"status": "ok", "ollama": {...}}
```

**5. Ollama (11434):**
```bash
curl http://localhost:11434/api/tags
# Should return list of models
```

---

## Troubleshooting Installation

### Python Not Found

**Windows:**
```cmd
# Install Python 3.11+
# Download from https://python.org
# During install, check "Add Python to PATH"
```

**WSL:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### Port Already in Use

```bash
# Check what's using the port
netstat -tlnp | grep 5000

# Kill the process
kill <PID>
```

### Ollama Connection Refused

```bash
# Start Ollama service
ollama serve

# In WSL, ensure Windows Ollama is accessible
# May need to configure WSL networking
```

### Web Interface Not Loading

1. Verify HTTP Server Custom is running in ARC
2. Check `index.html` is in correct directory
3. Test direct: `http://localhost:8080`
4. Clear browser cache (Ctrl+Shift+R)

---

## Environment Variables (Optional)

Create `.env` file for configuration:

```bash
# Ollama configuration
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
OLLAMA_MODEL=llama3.1

# Server configuration
SERVO_BACKEND_PORT=5000
VOICE_CHAT_PORT=5001

# ARC configuration
ARC_HTTP_PORT=8080
ARC_CAMERA_PORT=8097
```

---

## Next Steps

After installation:
1. Test all tabs in web interface
2. Configure servo ports for your robot
3. Test camera feed
4. Test voice chat
5. Read [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common issues

---

**Last Updated:** June 30, 2026  
**Version:** 1.0.0
