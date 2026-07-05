# Genesis ↔ ARC Communication Setup

## Problem
ARC's HTTP Server skill does **NOT** support custom REST endpoints like:
- ❌ POST /genesis/command
- ❌ POST /genesis/event

It only exposes basic variable read/write via query parameters.

## ✅ Working Solution

### Architecture

```
┌─────────────────┐                    ┌─────────────────┐
│   GENESIS       │                    │      ARC        │
│   (Python)      │                    │   (JavaScript)  │
│                 │                    │                 │
│  HTTP Server    │◄──── POST ──────── │  HTTP.Post()    │
│  Port: 8080     │                    │                 │
│                 │                    │                 │
│  HTTP Client    │──── GET ──────────►│  HTTP Server    │
│                 │    (variables)     │  (variables)    │
└─────────────────┘                    └─────────────────┘
```

### Direction 1: ARC → Genesis (Commands)

ARC makes HTTP POST requests to Genesis's Python server:

**ARC Side** (GenesisBridge.js):
```javascript
function SendCommandToGenesis(commandType, data) {
    var payload = JSON.stringify({
        type: commandType,
        data: data,
        timestamp: new Date().toISOString()
    });
    
    HTTP.Post("http://localhost:8080/arc/command", payload);
}
```

**Genesis Side** (Python FastAPI):
```python
@app.post("/arc/command")
async def receive_arc_command(command: dict):
    # Process command from ARC
    print(f"Received from ARC: {command}")
    return {"status": "ok"}
```

### Direction 2: Genesis → ARC (Commands)

Genesis writes to ARC HTTP Server variables, ARC script polls them:

**Genesis Side** (Python):
```python
import requests

def send_command_to_arc(command_type, **kwargs):
    # Write to ARC HTTP Server variable
    cmd = {
        "type": command_type,
        **kwargs
    }
    
    # ARC HTTP Server exposes variables via /set.html
    requests.get(
        "http://localhost:8080/set.html",
        params={
            "var": "$Genesis_Command",
            "val": json.dumps(cmd)
        }
    )
```

**ARC Side** (GenesisBridge.js):
```javascript
// Poll for commands from Genesis (every 500ms)
setInterval(function() {
    var commandJson = getVar('$Genesis_Command');
    if (commandJson && commandJson !== "") {
        try {
            var cmd = JSON.parse(commandJson);
            ReceiveFromGenesis(cmd);  // Process command
            
            // Clear the variable after processing
            setVar('$Genesis_Command', "");
        } catch (e) {
            LogError("Invalid command JSON: " + e.message);
        }
    }
}, 500);
```

---

## Setup Instructions

### Step 1: Genesis Python HTTP Server

Create `genesis/server.py`:

```python
#!/usr/bin/env python3
"""
Genesis Mission Control - HTTP Server for ARC Communication
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import json
from datetime import datetime

app = FastAPI(title="Genesis Mission Control")

class ARCCommand(BaseModel):
    type: str
    data: dict = {}
    timestamp: str = None

@app.get("/status")
async def get_status():
    """Health check endpoint"""
    return {
        "status": "ok",
        "robot": "mini-bff-genesis",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/arc/command")
async def receive_arc_command(command: ARCCommand):
    """Receive commands/events from ARC"""
    print(f"📥 ARC Command: {command.type}")
    print(f"   Data: {command.data}")
    
    # Process command here
    # - Sensor data (IMU, camera, objects, etc.)
    # - Status updates
    # - Emergency alerts
    
    # TODO: Add to Genesis decision queue
    # genesis.decision.queue_command(command)
    
    return {"status": "received", "type": command.type}

@app.post("/arc/event")
async def receive_arc_event(event: dict):
    """Receive sensor events from ARC"""
    event_type = event.get("type", "unknown")
    data = event.get("data", {})
    
    print(f"📊 ARC Event: {event_type}")
    # TODO: Process sensor data
    # genesis.perception.update(event_type, data)
    
    return {"status": "received"}

if __name__ == "__main__":
    print("🚀 Genesis HTTP Server starting...")
    print("🌐 Listening on http://localhost:8080")
    print("📡 Endpoints:")
    print("   GET  /status - Health check")
    print("   POST /arc/command - Receive ARC commands")
    print("   POST /arc/event - Receive ARC events")
    print("")
    
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

**Install requirements**:
```bash
pip install fastapi uvicorn pydantic requests
```

**Run the server**:
```bash
cd genesis
python3 server.py
```

---

### Step 2: Update GenesisBridge.js for ARC

Replace the HTTP communication section in GenesisBridge.js:

```javascript
// ============================================================================
// COMMUNICATION WITH GENESIS
// ============================================================================

// Send sensor data/events to Genesis
function SendToGenesis(eventType, data) {
    var payload = JSON.stringify({
        type: eventType,
        data: data,
        timestamp: new Date().toISOString(),
        robotId: GENESIS_CONFIG.robotId
    });
    
    try {
        HTTP.Post(GENESIS_CONFIG.apiHost + "/arc/event", payload);
    } catch (e) {
        LogWarning("Failed to send to Genesis: " + e.message);
        genesisState.isConnected = false;
    }
}

// Poll for commands from Genesis (called every 500ms)
function PollGenesisCommands() {
    try {
        var commandJson = getVar('$Genesis_Command');
        
        if (commandJson && commandJson !== "" && commandJson !== "null") {
            try {
                var cmd = JSON.parse(commandJson);
                LogCommand("Received: " + cmd.type);
                ReceiveFromGenesis(cmd);
                
                // Clear the variable after processing
                setVar('$Genesis_Command', "");
            } catch (e) {
                LogError("Invalid command JSON: " + e.message);
                setVar('$Genesis_Command', "");  // Clear bad data
            }
        }
    } catch (e) {
        // Variable may not exist yet
    }
}

// Send heartbeat to Genesis
function SendHeartbeat() {
    genesisState.uptime = Date.now() - genesisState.startTime;
    var batteryVoltage = getVar('$BatteryVoltage') || 0;
    
    // Test connection
    try {
        var response = HTTP.Get(GENESIS_CONFIG.apiHost + "/status");
        if (response.statusCode === 200) {
            if (!genesisState.isConnected) {
                LogSuccess("Genesis API connected");
            }
            genesisState.isConnected = true;
        } else {
            genesisState.isConnected = false;
        }
    } catch (e) {
        genesisState.isConnected = false;
    }
    
    // Send heartbeat if connected
    if (genesisState.isConnected) {
        SendToGenesis("heartbeat", {
            status: "online",
            uptime: genesisState.uptime,
            battery: batteryVoltage,
            emergencyStop: genesisState.emergencyStop
        });
    }
}

// Receive and process commands from Genesis
function ReceiveFromGenesis(cmd) {
    // cmd is already parsed JSON object
    
    switch(cmd.type) {
        case "servo_move":
            MoveServo(cmd.port, cmd.position, cmd.speed);
            break;
            
        case "servo_enable":
            EZB.Servo.Enable(cmd.port);
            LogSuccess("Enabled servo " + cmd.port);
            break;
            
        case "servo_disable":
            EZB.Servo.Disable(cmd.port);
            LogSuccess("Disabled servo " + cmd.port);
            break;
            
        case "servo_disable_all":
            EZB.Servo.DisableAll();
            LogSuccess("Disabled ALL servos");
            break;
            
        case "move_to_position":
            MoveToPosition(cmd.positionName, cmd.speed);
            break;
            
        case "auto_position_action":
            controlCommand("Auto Position", "AutoPositionAction", cmd.actionName);
            break;
            
        case "auto_position_frame":
            var delay = cmd.delay || 1000;
            var steps = cmd.steps || 50;
            var speed = cmd.speed || 50;
            controlCommand("Auto Position", "AutoPositionFrame", cmd.frameName, delay, steps, speed);
            break;
            
        case "move_base":
            ExecuteMovement(cmd.command, cmd.duration);
            break;
            
        case "speak":
            EZB.Speech.Speak(cmd.text);
            Log("Speaking: " + cmd.text);
            break;
            
        case "camera_start":
            controlCommand("Camera", "CameraStart");
            Log("Camera started");
            break;
            
        case "camera_stop":
            controlCommand("Camera", "CameraStop");
            Log("Camera stopped");
            break;
            
        case "emergency_stop":
            TriggerEmergencyStop(cmd.reason || "Genesis emergency stop");
            break;
            
        case "reset_emergency":
            ResetEmergencyStop();
            break;
            
        case "run_script":
            controlCommand("Script Manager", "ScriptStart", cmd.scriptName);
            Log("Running script: " + cmd.scriptName);
            break;
            
        default:
            LogWarning("Unknown command: " + cmd.type);
    }
}
```

**Add polling to SetupSensorEvents()**:
```javascript
function SetupSensorEvents() {
    Log("Setting up sensor monitoring...");
    
    // Poll for Genesis commands (500ms)
    setInterval(PollGenesisCommands, 500);
    Log("Genesis command polling: 2Hz");
    
    // ... rest of sensor setup ...
}
```

---

### Step 3: Genesis Python Client for ARC

Create `genesis/arc_bridge.py`:

```python
#!/usr/bin/env python3
"""
Genesis → ARC Communication Bridge
Sends commands to ARC via HTTP Server variables
"""

import requests
import json
import time

class ARCBridge:
    def __init__(self, arc_host="localhost", arc_port=8080):
        self.arc_host = arc_host
        self.arc_port = arc_port
        self.base_url = f"http://{arc_host}:{arc_port}"
        
    def send_command(self, command_type, **kwargs):
        """Send command to ARC via HTTP Server variable"""
        cmd = {
            "type": command_type,
            **kwargs
        }
        
        try:
            # ARC HTTP Server exposes variable setting via /set.html
            response = requests.get(
                f"{self.base_url}/set.html",
                params={
                    "var": "$Genesis_Command",
                    "val": json.dumps(cmd)
                },
                timeout=2
            )
            
            if response.status_code == 200:
                print(f"✅ Sent to ARC: {command_type}")
                return True
            else:
                print(f"⚠️ ARC HTTP error: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to send to ARC: {e}")
            return False
    
    # Convenience methods
    def move_servo(self, port, position, speed=50):
        return self.send_command("servo_move", port=port, position=position, speed=speed)
    
    def speak(self, text):
        return self.send_command("speak", text=text)
    
    def move_to_position(self, position_name, speed=50):
        return self.send_command("move_to_position", positionName=position_name, speed=speed)
    
    def emergency_stop(self, reason="Emergency stop"):
        return self.send_command("emergency_stop", reason=reason)
    
    def camera_start(self):
        return self.send_command("camera_start")
    
    def camera_stop(self):
        return self.send_command("camera_stop")
    
    def test_connection(self):
        """Test if ARC HTTP Server is reachable"""
        try:
            response = requests.get(f"{self.base_url}/status.html", timeout=2)
            return response.status_code == 200
        except:
            return False

# Example usage
if __name__ == "__main__":
    arc = ARCBridge()
    
    print("Testing ARC connection...")
    if arc.test_connection():
        print("✅ ARC connected")
        
        # Test commands
        arc.move_servo("D0", 90, 50)  # Head Tilt
        time.sleep(1)
        arc.speak("Hello from Genesis!")
        time.sleep(2)
        arc.move_to_position("STAND", 50)
    else:
        print("❌ ARC not connected")
        print("   Make sure ARC HTTP Server skill is running on port 8080")
```

---

### Step 4: Configure ARC HTTP Server Skill

1. **Add HTTP Server skill** to ARC project (if not already added)

2. **Configure settings**:
   ```
   Port: 8080
   Enable Authentication: No (for local dev)
   CORS Enabled: Yes
   ```

3. **Enable variable access**:
   - The HTTP Server skill automatically exposes variables via:
     - `GET /get.html?var=$VariableName` - Read variable
     - `GET /set.html?var=$VariableName&val=value` - Write variable

4. **Test variable access**:
   ```bash
   # From terminal, test reading/writing variables
   curl "http://localhost:8080/get.html?var=\$BatteryVoltage"
   curl "http://localhost:8080/set.html?var=\$TestVar&val=hello"
   ```

---

### Step 5: Test Communication

**Test 1: Start Genesis Server**
```bash
cd genesis
python3 server.py
```

Should see:
```
🚀 Genesis HTTP Server starting...
🌐 Listening on http://localhost:8080
```

**Test 2: Test ARC → Genesis**
In ARC Script Console:
```javascript
var payload = JSON.stringify({
    type: "test_event",
    data: { message: "Hello from ARC" }
});
HTTP.Post("http://localhost:8080/arc/event", payload);
```

Should see in Genesis server logs:
```
📊 ARC Event: test_event
```

**Test 3: Test Genesis → ARC**
In Python:
```python
from genesis.arc_bridge import ARCBridge

arc = ARCBridge()
arc.speak("Hello from Genesis!")
arc.move_servo("D0", 90, 50)
```

Should see in ARC (Variable Watch for `$Genesis_Command`):
```
{"type": "speak", "text": "Hello from Genesis!"}
```

And robot should speak!

---

## ✅ Complete Communication Flow

```
1. ARC Sensor Data → Genesis
   ───────────────────────────
   ARC: SendToGenesis("imu_data", {...})
   ↓ HTTP POST
   Genesis: @app.post("/arc/event")
   
   
2. Genesis Commands → ARC
   ───────────────────────────
   Genesis: arc.send_command("speak", text="Hello")
   ↓ HTTP GET /set.html
   ARC Variable: $Genesis_Command
   ↓ Poll (500ms)
   ARC: ReceiveFromGenesis(cmd)
   ↓ Execute
   EZB.Speech.Speak("Hello")
```

---

## 📋 Requirements

**Genesis (Python)**:
```bash
pip install fastapi uvicorn pydantic requests
```

**ARC Skills**:
- HTTP Server (built-in)
- Script Collection (for GenesisBridge.js)
- Variable Watch (for debugging)

---

## 🔍 Troubleshooting

**ARC can't reach Genesis**:
- Check Genesis server is running: `curl http://localhost:8080/status`
- Check firewall allows port 8080
- Verify no other service using port 8080

**Genesis can't reach ARC**:
- Check HTTP Server skill is enabled in ARC
- Test: `curl "http://localhost:8080/get.html?var=\$BatteryVoltage"`
- Verify ARC project is running (not paused)

**Commands not executing in ARC**:
- Check Variable Watch for `$Genesis_Command`
- Verify JSON is valid
- Check GenesisBridge.js is running (Script Collection)
- Look for errors in `$GenesisBridge_Log`

---

## Next Steps

1. **Start Genesis HTTP Server**
2. **Update GenesisBridge.js** with new communication code
3. **Test bidirectional communication**
4. **Implement Genesis decision loop**

Would you like me to create the complete Genesis Python application with the HTTP server and ARC bridge integrated?
