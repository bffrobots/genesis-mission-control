# Genesis Mission Control
**Autonomous Humanoid Robot Control System**  
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE) [![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-lightgrey)]() [![ARC Version](https://img.shields.io/badge/ARC-v4.2.1-orange)](https://synthiam.com?r=15c7e8c1) [![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## 🤖 Overview
Control system for the **Mini BFF Genesis (18 DOF)** humanoid robot. Features precise servo control, live camera streaming, and autonomous AI decision-making via natural language.

### Key Features
- 🎯 **18 DOF Motion Control:** Precise servo control via web interface.
- 📹 **Live Camera Feed:** HLS streaming from robot camera.
- 🎤 **Voice Commands:** Natural language control via **Cloud AI (Anthropic/OpenAI)** - <1ms response!
- 🧠 **Autonomous AI:** Genesis AI brain for decision making.
- 🎨 **Modern Web UI:** Orbital command design system.
- ⚡ **Fast Hybrid Architecture:** Cloud AI for conversation (1-2s), rule-based for commands (<1ms).

---

## 🖥️ System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Windows 10 | Windows 11 |
| **CPU** | Intel i5 / Ryzen 5 | Intel i7 / Ryzen 7 |
| **RAM** | 8 GB | 16 GB |
| **ARC** | v4.2.1 | Latest |
| **Python** | 3.11 | 3.11+ |
| **Platform** | Native Windows | Native Windows |

**Note:** v2.0 runs natively on Windows - no WSL required!

---

## 🏗️ Architecture & Ports

### System Flow
```
Web Browser (localhost:8080) ──┬── ARC HTTP Server (8080)
                               │
                               ├── Voice & Chat Server (Port 5001) ── AI Chat, Commands
                               │
                               └── Motion Control Backend (Port 5000) ── Servos, ARC Variables
                                    │
                                    ▼
                                 ARC Software ──(USB/WiFi)──> Mini BFF Genesis (18 DOF)
```

### Port Configuration
| Port | Service | Access |
|------|---------|--------|
| **8080** | HTTP Server Custom (Web UI) | Local only |
| **8097** | Live Stream Broadcast (Camera) | Local only |
| **5000** | Motion Control Backend (Windows) - Servo control | Local only |
| **5001** | Voice & Chat Server (Windows) - AI & Commands | Local only |

**Note:** Port 11434 (Ollama) removed in v2.0 - replaced with Cloud AI (Anthropic/OpenAI)

---

## 🚀 Installation & Setup

### Prerequisites
1.  **Python 3.11+**: [https://python.org](https://python.org)
2.  **Synthiam ARC**: [Download App](https://synthiam.com/Community/Apps/Genesis_Mission_Control-23372)
3.  **Optional: AI API Key**: [Anthropic](https://console.anthropic.com/) or [OpenAI](https://platform.openai.com/api-keys)

### Step 1: Clone & Dependencies
```bash
# Clone repository
git clone https://github.com/bffrobots/genesis-mission-control.git
cd genesis-mission-control

# Install Python packages
pip install -r requirements.txt
# Or double-click: scripts/install-dependencies.bat
```

### Step 2: Configure ARC
1.  Open **Synthiam ARC**.
2.  **Download App:** Go to [Genesis Mission Control App](https://synthiam.com/Community/Apps/Genesis_Mission_Control-23372), click "Download App", open the `.ezb` file.
3.  **Deploy Web Interface:**
    ```cmd
    # Windows Command Prompt
    copy web\interface-index.html "%USERPROFILE%\Documents\ARC\HTTP Server Root\index.html"
    ```
    *Note: The ARC App handles all ARC-side configuration automatically.*

### Step 3: (Optional) Set AI API Key
For AI conversation capability (commands work WITHOUT this):

```cmd
setx ANTHROPIC_API_KEY "sk-ant-..."
```

**Without API key:** Server runs in rule-based mode (FREE, all commands work instantly).

### Step 4: Start Voice & Chat Services

**Option A: Start All Services (Recommended)**
```cmd
# Double-click: scripts/start-all.bat
# Opens two terminal windows:
#   - Motion Control (Port 5000)
#   - Voice & Chat (Port 5001)
```

**Option B: Start Voice & Chat Only**
```cmd
# Double-click: scripts/start.bat
# Or command line:
cd scripts
python voice-chat-server-v2.py
```

This starts the Voice & Chat server on port 5001 with:
- Cloud AI conversations (1-2s response with API key)
- Rule-based commands (<1ms, works without API key)
- WebSocket support for real-time chat

### Step 5: Start Motion Control Services

**Option A: Start All Services (Recommended)**
```cmd
# Double-click: scripts/start-all.bat
# Automatically starts both backends
```

**Option B: Start Motion Control Only**
```cmd
# Double-click: scripts/start-genesis.bat
# Or command line:
cd scripts
python main.py
```

This starts the Motion Control backend on port 5000 with:
- Servo control via web interface
- File-based ARC integration
- Pose management
- Emergency stop

### Step 6: Access Interface
Open browser: **http://localhost:8080/index.html**

---

## 🎤 Voice & Chat v2.0 - Fast Hybrid Architecture

### Performance Comparison

| Metric | v1.0 (Ollama) | v2.0 (Cloud AI) | Improvement |
|--------|---------------|-----------------|-------------|
| **Commands** | 500-1000ms | **<1ms** | **1000x faster** ⚡ |
| **Conversation** | 10-20 seconds | **1-2 seconds** | **10x faster** 🚀 |
| **Timeout Errors** | Frequent | **Zero** | **100% eliminated** ✅ |
| **GPU Required** | Yes | **No** | N/A |
| **Platform** | WSL/Linux | **Native Windows** | Much easier |

### Architecture

```
User Input
    ↓
Rule-Based Parser (<1ms) ──[Command Detected?]──YES──→ Execute Action → Response
    ↓ NO
Check AI Provider
    ├─ Cloud AI (Anthropic/OpenAI) → 1-2s → Response
    └─ No AI → Fallback Message → Response
```

### Supported Commands (All <1ms)

| Command | Action | Example Phrases |
|---------|--------|----------------|
| `stand` | STAND | "stand up", "please stand" |
| `sit` | SIT | "sit down", "have a seat" |
| `wave` | WAVE | "wave hello", "wave at me" |
| `dance` | DANCE | "do a dance", "dance for me" |
| `bow` | BOW | "bow to the audience" |
| `stop` | STOP | "stop moving", "freeze" |
| `reset` | RESET | "reset position" |
| `walk` | WALK_FORWARD | "walk forward" |
| `backward` | WALK_BACKWARD | "walk backward" |
| `left` | TURN_LEFT | "turn left" |
| `right` | TURN_RIGHT | "turn right" |
| `servo D# to #` | SERVO_MOVE | "move servo D0 to 90 degrees" |

### Testing Voice & Chat

```bash
# Health check
curl http://localhost:5001/status

# Test command (<1ms response)
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "stand up"}'

# Expected response:
# {
#   "response": "Standing up",
#   "action": "STAND",
#   "latency_ms": 0.1,
#   "source": "rule-based"
# }
```

### Cost Analysis

- **Rule-Based Mode:** FREE (all commands work instantly)
- **Cloud AI:** ~$0.003 per conversation
  - Light use (10/day): ~$0.90/month
  - Medium use (50/day): ~$4.50/month
  - Heavy use (200/day): ~$18/month

**Recommendation:** Start with rule-based mode (FREE). Add cloud AI when you need conversation capability.

---

## 🎯 Motion Control (Port 5000)

### Servo Backend API

The motion control backend handles all servo control via the web interface:

```bash
# Health check
curl http://localhost:5000/status

# Move single servo
curl -X POST http://localhost:5000/api/servo \
  -H "Content-Type: application/json" \
  -d '{"servo_id": 0, "position": 90, "port": "D0"}'

# Move all servos (pose)
curl -X POST http://localhost:5000/api/servo/all \
  -H "Content-Type: application/json" \
  -d '{"servos": {"D0": 90, "D1": 45, "D2": 120}}'

# Emergency stop
curl -X POST http://localhost:5000/api/estop
```

### How It Works

1. Web interface sends servo positions to `localhost:5000/api/servo`
2. Backend writes position to file: `Servo_D0.txt` in ARC HTTP Server Root
3. ARC HTTP Server Custom serves the file at `http://localhost:8080/Servo_D0.txt`
4. ARC EZ-Script reads the file via `HTTPGet()` and executes `Servo(port, position)`

**Result:** Smooth, real-time servo control from the web interface!

---

## 🧠 AI & Agentic Integration
Supports integration with multiple AI agent platforms. See [docs/AGENTIC-INTEGRATION.md](docs/AGENTIC-INTEGRATION.md).

| Platform | Status | Documentation |
|----------|--------|---------------|
| **Hermes Agent** | ✅ Native | `skill_view("genesis-mission-control")` |
| **LangChain** | ✅ Tools | Custom tool wrappers for servo/camera/voice |
| **AutoGen** | ✅ Ready | Multi-agent robot control |
| **CrewAI** | ✅ Ready | Role-based agent tasks |
| **OpenClaw** | ✅ Bridge | [docs/OPENCLAW-INTEGRATION.md](docs/OPENCLAW-INTEGRATION.md) |
| **Claude Code** | ✅ CLI | [docs/CLAUDE-CODE-INTEGRATION.md](docs/CLAUDE-CODE-INTEGRATION.md) |

---

## 🔒 Security
- ✅ **Localhost-only** by default (no external exposure).
- ✅ **No hardcoded credentials**.
- ✅ **API keys via environment variables only**.
- ✅ **Input validation** on servo commands (0-180° range).
- ✅ **CORS restrictions** enforced.
- *Full audit report:* [SECURITY.md](SECURITY.md)

---

## 🛠️ Troubleshooting & Diagnostics

### Quick Diagnostic
Run script to check all services:
```bash
./scripts/diagnose.sh
```

**Expected Output:**
```
Checking HTTP Server (8080)... ✅ OK
Checking Camera Stream (8097)... ✅ OK
Checking Motion Control (5000)... ✅ OK
Checking Voice & Chat (5001)... ✅ OK
```

### Common Issues

| Issue | Solution |
|-------|----------|
| **Python not found** | Install Python 3.11+ from python.org, check "Add to PATH" |
| **Port 5000 already in use** | Close other instances, restart computer, or use different port |
| **Port 5001 already in use** | Close other instances, restart computer, or use different port |
| **Dependencies not installed** | Run `scripts/install-dependencies.bat` as administrator |
| **ARC HTTP Server not responding** | Open ARC, add HTTP Server Custom skill, enable on port 8080 |
| **Commands work but robot doesn't move** | Check ARC Variable Watch for `$Genesis_Command`, verify Auto Position skill is active |
| **Motion control not working** | Verify `start-genesis.bat` is running on port 5000, check servo files in HTTP Server Root |
| **AI not available** | Set `ANTHROPIC_API_KEY` environment variable (commands still work without it) |
| **High latency (>5 seconds)** | Test network: `curl -w "Time: %{time_total}s" https://api.anthropic.com`. Commands still work <1ms even if AI is slow |

### Motion Control Troubleshooting

**Problem:** Web interface sliders move but robot doesn't respond

**Solutions:**
1. Verify `start-genesis.bat` is running (Port 5000)
2. Check servo files exist: `dir "%USERPROFILE%\Documents\ARC\HTTP Server Root\Servo_D*.txt"`
3. Verify ARC HTTP Server Custom is enabled on port 8080
4. Check ARC script is reading servo files via HTTPGet()
5. Test API: `curl http://localhost:5000/status`

### Performance Issues

**Problem:** Voice & Chat responses are slow

**Solutions:**
1. Commands should always be <1ms (rule-based, no AI needed)
2. If AI conversation is slow, check network connection to cloud API
3. Verify API key is valid and has quota remaining
4. Consider using rule-based mode for time-critical operations

---

## 📁 Project Structure

```
genesis-mission-control/
├── scripts/
│   ├── main.py                        # Motion control backend (Port 5000)
│   ├── voice-chat-server-v2.py        # Voice & Chat server (Port 5001)
│   ├── start-genesis.bat              # Start motion control
│   ├── start.bat                      # Start voice & chat
│   ├── start-all.bat                  # Start both backends
│   ├── install-dependencies.bat       # Install all dependencies
│   ├── diagnose.sh                    # Diagnostic script
│   └── TEST_CONNECTIONS.bat           # Connection tests
├── web/
│   ├── interface-index.html           # Main web interface
│   └── voice-chat-integration.js      # Frontend integration
├── docs/                              # Documentation
│   └── QUICKSTART.md                  # 5-minute setup guide
├── archive/                           # Historical documentation
├── .gitignore
├── LICENSE
├── README.md                          # This file
└── requirements.txt                   # Python dependencies
```

---

## 📖 Documentation

### Core Guides
- **[QUICKSTART](docs/QUICKSTART.md)** - 5-minute setup guide
- **[Installation](docs/INSTALLATION.md)** - Detailed setup instructions
- **[ARC Setup](docs/ARC-SETUP.md)** - Configure Synthiam ARC
- **[Hardware Setup](docs/HARDWARE-SETUP.md)** - Robot configuration
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

### Integration Guides
- **[Camera Integration](docs/CAMERA-INTEGRATION.md)** - Live video feed setup
- **[OpenClaw Integration](docs/OPENCLAW-INTEGRATION.md)** - Agentic AI platform
- **[Claude Code Integration](docs/CLAUDE-CODE-INTEGRATION.md)** - Autonomous coding
- **[Agentic Integration](docs/AGENTIC-INTEGRATION.md)** - AI agent platforms

### Architecture
- **[Communication Architecture](docs/COMMUNICATION-ARCHITECTURE.md)** - System design
- **[Voice & Chat v2.0](#-voice--chat-v20---fast-hybrid-architecture)** - Cloud AI integration
- **[Motion Control](#-motion-control-port-5000)** - Servo backend

**Historical docs:** See `archive/` folder for previous versions

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Synthiam ARC** - Robot control platform ([https://synthiam.com](https://synthiam.com))
- **Anthropic** - Claude AI for conversations ([https://anthropic.com](https://anthropic.com))
- **OpenAI** - GPT models for AI responses ([https://openai.com](https://openai.com))
- **FastAPI** - High-performance web framework ([https://fastapi.tiangolo.com](https://fastapi.tiangolo.com))
- **Flask** - Web framework for motion control backend ([https://flask.palletsprojects.com](https://flask.palletsprojects.com))

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/bffrobots/genesis-mission-control/issues)
- **Documentation:** See `docs/` folder
- **Quick Help:** Run `scripts/diagnose.sh`
- **Quick Start:** See [docs/QUICKSTART.md](docs/QUICKSTART.md)

---

**Version:** 2.0.0  
**Last Updated:** July 5, 2026  
**Status:** ✅ Production Ready  
**Performance:** Commands <1ms, Zero timeouts 🎉
