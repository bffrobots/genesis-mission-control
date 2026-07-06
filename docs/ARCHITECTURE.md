# System Architecture

**Genesis Mission Control v2.0 - Complete System Design**

---

## 🏗️ Overview

Genesis Mission Control is a hybrid robot control system combining:
- **Motion Control Backend** (Port 5000) - Servo control via file-based ARC integration
- **Voice & Chat Server** (Port 5001) - Cloud AI + rule-based command parsing
- **Web Interface** (Port 8080) - Modern UI served by ARC HTTP Server Custom

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  Windows Tablet/Laptop                                              │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Web Browser                                                 │   │
│  │  http://localhost:8080                                       │   │
│  │                                                              │   │
│  │  - Motion Control UI (sliders, poses)                       │   │
│  │  - Voice & Chat UI (chat, voice input)                      │   │
│  │  - Camera Feed (live stream)                                │   │
│  └───────────────────┬─────────────────────────────────────────┘   │
│                      │                                               │
│         ┌────────────┴────────────┐                                 │
│         │                         │                                 │
│         ▼                         ▼                                 │
│  ┌─────────────┐           ┌─────────────┐                         │
│  │ Motion      │           │ Voice &     │                         │
│  │ Control     │           │ Chat        │                         │
│  │ Backend     │           │ Server      │                         │
│  │ Port: 5000  │           │ Port: 5001  │                         │
│  │             │           │             │                         │
│  │ Flask       │           │ FastAPI     │                         │
│  │ - Servo API │           │ - AI Chat   │                         │
│  │ - Pose Mgr  │           │ - Commands  │                         │
│  │ - E-STOP    │           │ - TTS/STT   │                         │
│  └──────┬──────┘           └──────┬──────┘                         │
│         │                         │                                 │
│         │                         │                                 │
│         └────────────┬────────────┘                                 │
│                      │                                              │
│               ┌──────▼──────┐                                       │
│               │   ARC       │                                       │
│               │  HTTP       │                                       │
│               │  Server     │                                       │
│               │  Port: 8080 │                                       │
│               │             │                                       │
│               │ - Serves    │                                       │
│               │   web UI    │                                       │
│               │ - Serves    │                                       │
│               │   .txt vars │                                       │
│               └──────┬──────┘                                       │
│                      │                                              │
│               ┌──────▼──────┐                                       │
│               │   ARC       │                                       │
│               │  Software   │                                       │
│               │  (Windows)  │                                       │
│               │             │                                       │
│               │ - HTTP      │                                       │
│               │   Server    │                                       │
│               │ - Auto      │                                       │
│               │   Position  │                                       │
│               │ - Camera    │                                       │
│               │ - Scripts   │                                       │
│               └──────┬──────┘                                       │
└──────────────────────┼──────────────────────────────────────────────┘
                       │ USB/WiFi
                       ▼
             ┌─────────────────┐
             │ Mini BFF        │
             │ Genesis         │
             │ (18 DOF Robot)  │
             └─────────────────┘
```

---

## 🔌 Port Configuration

| Port | Service | Technology | Purpose |
|------|---------|------------|---------|
| **8080** | ARC HTTP Server Custom | HTTP | Web UI, variable files |
| **8097** | Live Stream Broadcast | HTTP (HLS) | Camera streaming |
| **5000** | Motion Control Backend | Flask (Python) | Servo control API |
| **5001** | Voice & Chat Server | FastAPI (Python) | AI chat, commands |

**All services run locally on Windows - no external exposure.**

---

## 🔄 Data Flow

### Motion Control Flow

```
1. User moves slider in web interface
   ↓
2. JavaScript sends POST to localhost:5000/api/servo
   ↓
3. Flask backend writes position to Servo_D0.txt
   ↓
4. ARC HTTP Server serves file at localhost:8080/Servo_D0.txt
   ↓
5. ARC script reads file via HTTPGet()
   ↓
6. ARC executes Servo(D0, position)
   ↓
7. Robot servo moves
```

**File-Based Communication:**
- Motion control → ARC: `.txt` files in HTTP Server Root
- ARC reads files via `HTTPGet("http://localhost:8080/Servo_D0.txt")`
- No direct API calls to ARC (simpler, no CORS issues)

### Voice & Chat Flow

```
1. User types "stand up" in chat
   ↓
2. JavaScript sends POST to localhost:5001/chat
   ↓
3. FastAPI server parses command (rule-based, <1ms)
   ↓
4. If command detected:
   - Set ARC variable $Genesis_Command via HTTP
   - Return response immediately
   ↓
5. If conversation (no command):
   - Call Cloud AI (Anthropic/OpenAI, 1-2s)
   - Return AI response
   ↓
6. ARC script polls $Genesis_Command
   ↓
7. ARC executes command (STAND, WAVE, etc.)
```

**Hybrid Architecture:**
- **Rule-based:** Commands parsed instantly (<1ms), no AI needed
- **Cloud AI:** Conversations via Anthropic/OpenAI (1-2s)
- **Fallback:** Works without AI (rule-based mode)

---

## 📁 File Structure

```
genesis-mission-control/
├── scripts/
│   ├── main.py                        # Motion Control Backend (Flask)
│   ├── voice-chat-server-v2.py        # Voice & Chat Server (FastAPI)
│   ├── start-genesis.bat              # Start motion control
│   ├── start.bat                      # Start voice & chat
│   ├── start-all.bat                  # Start both
│   ├── install-dependencies.bat       # Install dependencies
│   ├── diagnose.sh                    # Diagnostic script
│   └── TEST_CONNECTIONS.bat           # Connection tests
│
├── web/
│   ├── interface-index.html           # Main web interface
│   └── voice-chat-integration-v2.js   # Voice & Chat frontend
│
├── docs/
│   ├── QUICKSTART.md                  # 5-minute setup
│   ├── TROUBLESHOOTING.md             # Common issues
│   ├── ARCHITECTURE.md                # This file
│   └── ...                            # Other guides
│
├── archive/                           # Historical docs
├── README.md                          # Main documentation
├── requirements.txt                   # Python dependencies
└── LICENSE                            # MIT License
```

---

## 🔧 Component Details

### Motion Control Backend (Port 5000)

**Technology:** Flask (Python)

**Purpose:** Handle all servo control from web interface

**Endpoints:**
```python
POST /api/servo      # Move single servo
POST /api/servo/all  # Move all servos (pose)
POST /api/estop      # Emergency stop
POST /api/pose       # Execute named pose
GET  /status         # Health check
GET  /api/servos     # Get current positions
```

**File-Based ARC Integration:**
```python
# Write servo position to file
with open("Servo_D0.txt", "w") as f:
    f.write("90")

# ARC reads via HTTP:
# http://localhost:8080/Servo_D0.txt
```

**Key Features:**
- Validates servo positions (0-180°)
- Writes to ARC HTTP Server Root
- Maintains servo state cache
- Emergency stop support

---

### Voice & Chat Server (Port 5001)

**Technology:** FastAPI (Python)

**Purpose:** Handle voice commands and AI conversations

**Endpoints:**
```python
POST /chat           # Chat message (commands + conversation)
GET  /status         # Health check
GET  /commands       # List supported commands
WS   /ws/chat        # WebSocket for real-time chat
```

**Hybrid Architecture:**
```python
# Rule-based parser (<1ms)
if "stand" in message:
    return {"action": "STAND", "latency_ms": 0.1}

# Cloud AI (1-2s, optional)
if AI_AVAILABLE:
    response = await anthropic.chat(message)
else:
    response = "AI not available"
```

**ARC Integration:**
```python
# Set ARC variable via HTTP
requests.get(
    "http://localhost:8080/set.html",
    params={"var": "$Genesis_Command", "val": json.dumps(cmd)}
)
```

**Key Features:**
- Rule-based command parsing (<1ms)
- Cloud AI conversations (1-2s)
- WebSocket support
- Works without AI (rule-based mode)

---

### Web Interface (Port 8080)

**Technology:** HTML/CSS/JavaScript (served by ARC)

**Purpose:** User interface for robot control

**Tabs:**
- **Dashboard:** Status, battery, quick actions
- **Motion Control:** Servo sliders, pose library
- **Voice & Chat:** Chat interface, voice input
- **Camera:** Live video feed
- **Navigation:** SLAM, waypoints (future)
- **System:** Logs, diagnostics

**Key Integration:**
```javascript
// Motion control - send to backend
fetch('http://localhost:5000/api/servo', {
  method: 'POST',
  body: JSON.stringify({servo_id: 0, position: 90})
});

// Voice & Chat - send to FastAPI
fetch('http://localhost:5001/chat', {
  method: 'POST',
  body: JSON.stringify({message: "stand up"})
});
```

---

### ARC Integration

**Skills Required:**
- HTTP Server Custom (port 8080)
- Auto Position (servo control)
- Camera Device (camera feed)
- Live Stream Broadcast (camera streaming)
- Variable Watch (debugging)
- Script Collection (automation)

**ARC JavaScript (Servo Control):**
```javascript
// Poll servo files every 100ms
setInterval(function() {
    var pos0 = HTTPGet("http://localhost:8080/Servo_D0.txt");
    if (pos0) {
        Servo(D0, parseInt(pos0));
    }
}, 100);
```

**ARC JavaScript (Voice Commands):**
```javascript
// Poll Genesis command variable
setInterval(function() {
    var cmd = getVar('$Genesis_Command');
    if (cmd) {
        var parsed = JSON.parse(cmd);
        if (parsed.action === 'STAND') {
            controlCommand("Auto Position", "AutoPositionFrame", "STAND");
        }
        setVar('$Genesis_Command', '');  // Clear
    }
}, 500);
```

---

## 🔒 Security

### Localhost-Only

All services bind to `0.0.0.0` but are only accessible from localhost:
- No external network exposure
- No port forwarding required
- Safe for public WiFi

### CORS Configuration

```python
# Flask (Motion Control)
CORS(app)  # Enable CORS for web interface

# FastAPI (Voice & Chat)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Localhost only
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Keys

**Never hardcoded:**
```python
# Read from environment variable
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
```

**Set via environment:**
```cmd
setx ANTHROPIC_API_KEY "sk-ant-..."
```

---

## 📈 Performance

### Benchmarks

| Operation | Latency | Notes |
|-----------|---------|-------|
| **Motion Command** | <1ms | Rule-based parsing |
| **Voice Command** | <1ms | Rule-based parsing |
| **AI Conversation** | 1-2s | Cloud API call |
| **Servo Update** | 100ms | File-based polling |
| **Camera Stream** | 1-2s | HLS latency |

### Optimization Strategies

**Motion Control:**
- File-based communication (fast, simple)
- 100ms polling interval (10Hz update rate)
- Direct servo API calls

**Voice & Chat:**
- Rule-based parsing first (<1ms)
- Cloud AI only for conversation (1-2s)
- WebSocket for real-time chat

**Camera:**
- HLS streaming (efficient)
- Iframe embedding (bypasses CORS)
- Separate port (8097, no interference)

---

## 🔄 Future Enhancements

### Planned Improvements

1. **WebSocket Servo Control:**
   - Replace file-based with WebSocket
   - Real-time bidirectional communication
   - Lower latency (<50ms)

2. **Local AI (Optional):**
   - Add Ollama support for offline AI
   - User choice: Cloud vs Local AI
   - Hybrid fallback (cloud → local → rule-based)

3. **Mobile App:**
   - React Native app
   - Same API endpoints
   - Bluetooth/WiFi control

4. **Cloud Dashboard:**
   - Remote monitoring
   - Analytics and logs
   - Multi-robot support

5. **Advanced Navigation:**
   - SLAM integration
   - Path planning
   - Obstacle avoidance

---

## 📞 Support

- **Documentation:** See `docs/` folder
- **Issues:** GitHub Issues
- **Architecture Questions:** See [COMMUNICATION-ARCHITECTURE.md](archive/COMMUNICATION-ARCHITECTURE.md) (historical)

---

**Last Updated:** July 5, 2026  
**Version:** 2.0.0  
**Status:** Production Ready
