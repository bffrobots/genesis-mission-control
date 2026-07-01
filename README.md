# Genesis Mission Control

**Autonomous Humanoid Robot Control System**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20+%20WSL-lightgrey)]()
[![ARC Version](https://img.shields.io/badge/ARC-v4.2.1-orange)](https://synthiam.com)

## Quick Start

### 1. Install Dependencies

```bash
# Clone repository
git clone https://github.com/bffrobots/genesis-mission-control.git
cd genesis-mission-control

# Install Python packages
pip install -r requirements.txt

# Install Ollama (for AI chat)
curl https://ollama.ai/install.sh | sh
ollama pull llama3.1
```

### 2. Configure ARC

1. Open **Synthiam ARC**
2. Add skills:
   - **HTTP Server Custom** (port 8080)
   - **Camera Device** (USB camera)
   - **Live Stream Broadcast** (port 8097)
   - **Auto Position** (servo control)
3. Copy web interface:
   ```bash
   cp web/index.html "/mnt/c/Users/YOUR_USERNAME/Documents/ARC/HTTP Server Root/index.html"
   ```

### 3. Start Services

**Windows Terminal (Servo Backend):**
```cmd
scripts\start_genesis.bat
```

**WSL Terminal (Voice & Chat):**
```bash
./scripts/start_genesis.sh
```

### 4. Access Web Interface

Open browser: **http://localhost:8080**

## Features

- 🎯 **18 DOF Motion Control** - Precise servo control via web interface
- 📹 **Live Camera Feed** - HLS streaming from robot camera
- 🎤 **Voice Commands** - Natural language control via Whisper + Ollama
- 🧠 **Autonomous AI** - Genesis AI brain for decision making
- 🎨 **Modern Web UI** - Orbital command design system

## Documentation

| Guide | Description |
|-------|-------------|
| [Installation](docs/INSTALLATION.md) | Complete setup guide |
| [Camera Integration](docs/CAMERA-INTEGRATION.md) | Live stream setup |
| [Servo Control](docs/SERVO-CONTROL.md) | Motion control backend |
| [Voice Chat](docs/VOICE-CHAT.md) | AI conversation system |
| [ARC Setup](docs/ARC-SETUP.md) | Synthiam ARC configuration |
| [Hardware Setup](docs/HARDWARE-SETUP.md) | Mini BFF Genesis build |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues & fixes |
| [Agentic Integration](docs/AGENTIC-INTEGRATION.md) | AI platform integration |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Web Browser (http://localhost:8080)                        │
│  - Motion Control (18 DOF sliders)                          │
│  - Camera & Vision (Live Stream)                            │
│  - Voice & Chat (AI conversation)                           │
└──────────────┬──────────────────────────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌─────────┐         ┌─────────────┐
│ ARC     │         │ WSL Backend │
│ HTTP    │         │ Port 5001   │
│ Server  │         │             │
│ 8080    │         │ - AI Chat   │
│         │         │ - TTS/STT   │
└────┬────┘         └──────┬──────┘
     │                     │
     │                ┌────▼──────┐
     │                │ Windows   │
     │                │ Backend   │
     │                │ Port 5000 │
     │                │           │
     │                │ - Servos  │
     │                │ - ARC Var │
     └────────────────┼───────────┘
                      │
                 ┌────▼──────┐
                 │ ARC       │
                 │ Software  │
                 └────┬──────┘
                      │ USB/WiFi
                 ┌────▼───────┐
                 │ Mini BFF   │
                 │ Genesis    │
                 │ (18 DOF)   │
                 └────────────┘
```

## Agentic AI Integration

Genesis Mission Control supports integration with AI agent platforms:

- **Hermes Agent**: Native skill integration (`skill_view("genesis-mission-control")`)
- **LangChain**: Custom tool wrappers for servo/camera/voice
- **AutoGen**: Multi-agent robot control ready
- **CrewAI**: Role-based agent tasks

See [docs/AGENTIC-INTEGRATION.md](docs/AGENTIC-INTEGRATION.md) for detailed guides.

## Security

- ✅ Localhost-only by default (no external exposure)
- ✅ No hardcoded credentials
- ✅ Input validation on servo commands (0-180° range)
- ✅ CORS restrictions enforced

See [SECURITY.md](SECURITY.md) for full audit report.

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| OS | Windows 10 + WSL | Windows 11 + WSL2 |
| CPU | Intel i5 / Ryzen 5 | Intel i7 / Ryzen 7 |
| RAM | 8 GB | 16 GB |
| ARC | v4.2.1 | Latest |
| Python | 3.11 | 3.11+ |

## Ports Used

| Port | Service | Access |
|------|---------|--------|
| 8080 | HTTP Server Custom (Web UI) | Local only |
| 8097 | Live Stream Broadcast (Camera) | Local only |
| 5000 | Servo Backend (Windows) | Local only |
| 5001 | Voice & Chat (WSL) | Local only |

## Quick Diagnostic

Run diagnostic script to check all services:

```bash
./scripts/diagnose.sh
```

Expected output:
```
Checking HTTP Server (8080)... ✅ OK
Checking Camera Stream (8097)... ✅ OK
Checking Servo Backend (5000)... ✅ OK
Checking Voice Chat (5001)... ✅ OK
Checking Ollama (11434)... ✅ OK
```

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Built with ❤️ by BFF Robots** | [www.bffrobots.com](https://www.bffrobots.com)
