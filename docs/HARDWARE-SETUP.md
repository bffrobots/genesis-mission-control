# Mini BFF Genesis - ARC Setup Guide

## Robot Configuration
- **Model**: Mini BFF Genesis Humanoid (18 DOF test platform)
- **Controller**: EZ-B v4 + SSC-32 (UART TTL)
- **Project**: Genesis_Mission_Control
- **Date**: April 15, 2026

---

## Servo Configuration

### Physical Servos (EZ-B v4) - 18 DOF

| DOF | Function | Port | Min | Max | Center | Notes |
|-----|----------|------|-----|-----|--------|-------|
| 1 | Head Tilt | D0 | 60 | 120 | 90 | Pitch up/down |
| 2 | Head Pan | D1 | 45 | 135 | 90 | Yaw left/right |
| 3 | Right Shoulder Pan | D2 | 45 | 135 | 90 | Arm rotation |
| 4 | Right Shoulder Tilt | D3 | 45 | 135 | 90 | Arm lift |
| 5 | Right Elbow | D4 | 0 | 135 | 45 | Elbow bend |
| 6 | Left Shoulder Pan | D5 | 45 | 135 | 90 | Arm rotation |
| 7 | Left Shoulder Tilt | D6 | 45 | 135 | 90 | Arm lift |
| 8 | Left Elbow | D7 | 0 | 135 | 45 | Elbow bend |
| 9 | Right Hip Pan | D8 | 45 | 135 | 90 | Leg rotation |
| 10 | Right Hip Tilt | D9 | 45 | 135 | 90 | Leg forward/back |
| 11 | Right Hip Roll | D10 | 45 | 135 | 90 | Leg side-to-side |
| 12 | Right Knee | D11 | 0 | 135 | 45 | Knee bend |
| 13 | Right Foot Tilt | D12 | 60 | 120 | 90 | Ankle balance |
| 14 | Left Hip Pan | D13 | 45 | 135 | 90 | Leg rotation |
| 15 | Left Hip Tilt | D14 | 45 | 135 | 90 | Leg forward/back |
| 16 | Left Hip Roll | D15 | 45 | 135 | 90 | Leg side-to-side |
| 17 | Left Knee | D16 | 0 | 135 | 45 | Knee bend |
| 18 | Left Foot Tilt | D17 | 60 | 120 | 90 | Ankle balance |

### Virtual Servos (SSC-32) - Future Hands

| Channel | Function | Port | Min | Max | Center | Notes |
|---------|----------|------|-----|-----|--------|-------|
| 0 | Right Wrist Tilt | V0 | 60 | 120 | 90 | Wrist pitch |
| 1 | Right Finger 1 | V1 | 0 | 90 | 45 | Thumb |
| 2 | Right Finger 2 | V2 | 0 | 90 | 45 | Index |
| 3 | Right Finger 3 | V3 | 0 | 90 | 45 | Middle |
| 4 | Right Finger 4 | V4 | 0 | 90 | 45 | Ring |
| 5 | Right Finger 5 | V5 | 0 | 90 | 45 | Pinky |
| 6 | Left Wrist Tilt | V6 | 60 | 120 | 90 | Wrist pitch |
| 7 | Left Finger 1 | V7 | 0 | 90 | 45 | Thumb |
| 8 | Left Finger 2 | V8 | 0 | 90 | 45 | Index |
| 9 | Left Finger 3 | V9 | 0 | 90 | 45 | Middle |
| 10 | Left Finger 4 | V10 | 0 | 90 | 45 | Ring |
| 11 | Left Finger 5 | V11 | 0 | 90 | 45 | Pinky |

---

## ARC Skills Setup Checklist

### Required Skills (Install from Skill Store)

- [ ] **Camera Device** (ID: 16120)
  - Configure: USB Camera, 640x480, 30fps
  
- [ ] **Darknet YOLO** (ID: 19863)
  - ⚠️ **CRITICAL**: Download `yolov3-tiny.weights` from https://pjreddie.com/media/files/yolov3-tiny.weights
  - Copy to: `C:\ProgramData\ARC\Plugins\d1db5da7-8805-41eb-8a65-a548e2fe60f6\`
  
- [ ] **Auto Position (Gait)** (ID: 16057)
  - Create frames: NEUTRAL, STAND, SIT, ARMS_UP, WAVE
  
- [ ] **HTTP Server** (ID: 16082)
  - Port: 8080
  - CORS: Enabled
  - Auth: Disabled (for local dev)
  
- [ ] **Script Collection** (ID: 16045)
  - Name it: "Script Manager"
  - Add GenesisBridge.js script
  
- [ ] **Script (JavaScript)** (ID: 16089)
  - For testing individual scripts
  
- [ ] **3-In-1 IMU** (ID: 19886)
  - I2C Port: I2C-0
  - Update Rate: 100Hz
  
- [ ] **SSC-32 Servo Controller** (ID: 16180)
  - Connection: UART TTL (configure COM port)
  - Creates virtual ports V0-V31
  
- [ ] **Variable Watch** (ID: 16056)
  - Add variables for debugging
  
- [ ] **Servo Configuration** (Built-in)
  - Configure all 18 physical servos (D0-D17)
  - Configure 12 virtual servos (V0-V11)

### Optional Skills

- [ ] **DepthSensor** (ID: 15873) - If you have Kinect/RealSense
- [ ] **The Better Navigator** (ID: 20956) - For autonomous navigation
- [ ] **Speech Recognition** (Built-in) - For voice commands

---

## SSC-32 Configuration

### Connection Setup

**Option 1: Direct PC Connection**
```
PC (USB) → USB-to-TTL Adapter → SSC-32 RX/TX
```
- Windows assigns COM port (e.g., COM3)
- Configure in SSC-32 skill settings

**Option 2: Via EZ-B v4 (Recommended for wireless)**
```
PC → EZ-B v4 (WiFi) → UART TX/RX → SSC-32
```
- EZ-B acts as serial bridge
- Configure UART in EZ-B connection settings

### SSC-32 Skill Configuration
1. Add SSC-32 Servo Controller skill to project
2. Click **Configuration**
3. Select connection type:
   - **COM Port**: Choose assigned COM port (e.g., COM3)
   - **UART via EZ-B**: Select EZ-B connection
4. Set baud rate: 115200 (default)
5. Test connection
6. Virtual ports V0-V31 should appear in servo configuration

---

## GenesisBridge.js Installation

### Step 1: Copy Script
1. Open `GenesisBridge.js` file (created in skill references)
2. Copy entire contents (34KB)

### Step 2: Add to Script Collection
1. In ARC, open **Script Collection** skill (named "Script Manager")
2. Click **Add Script**
3. Name: `GenesisBridge`
4. Language: **JavaScript**
5. Paste entire script content
6. Click **Save**

### Step 3: Configure HTTP Server
1. Open **HTTP Server** skill
2. Settings:
   ```
   Port: 8080
   Enable Authentication: No
   CORS Enabled: Yes
   Allowed Origins: *
   ```
3. Note: You'll need to create a simple HTTP endpoint handler
   - See "HTTP Server Endpoint Setup" below

### Step 4: Test Initialization
1. Start the GenesisBridge script:
   ```javascript
   controlCommand("Script Manager", "ScriptStart", "GenesisBridge");
   ```
2. Check console output:
   ```
   🤖 Genesis Bridge - Mini BFF Genesis
   🤖 18 DOF + SSC-32 Virtual Ports (V0-V11)
   ✓ Genesis Bridge initialized successfully
   ```

---

## HTTP Server Endpoint Setup

The HTTP Server skill needs a script to handle incoming Genesis commands.

### Create HTTP Handler Script

**Add to Script Collection** as `HTTPHandler.js`:

```javascript
// HTTP Server endpoint handler for Genesis commands
// This script receives POST requests and calls ReceiveFromGenesis()

// Note: The HTTP Server skill in ARC automatically handles POST requests
// You need to configure the endpoint in HTTP Server skill settings

// Endpoint: POST /genesis/command
// Body: JSON command from Genesis

function HandleGenesisCommand(requestBody) {
    // Parse command
    var cmd = JSON.parse(requestBody);
    
    // Call ReceiveFromGenesis function from GenesisBridge
    // This assumes GenesisBridge.js is loaded in same project
    ReceiveFromGenesis(requestBody);
    
    // Return response
    return JSON.stringify({
        success: true,
        timestamp: new Date().toISOString()
    });
}
```

### Configure HTTP Server Endpoints

1. Open **HTTP Server** skill
2. Go to **Endpoints** tab
3. Add new endpoint:
   ```
   Path: /genesis/command
   Method: POST
   Script: HTTPHandler
   Function: HandleGenesisCommand
   ```
4. Add status endpoint:
   ```
   Path: /status
   Method: GET
   Response: {"status": "ok", "robot": "mini-bff-genesis"}
   ```
5. Add event endpoint:
   ```
   Path: /event
   Method: POST
   Script: HTTPHandler
   Function: HandleGenesisEvent
   ```

**Alternative**: If HTTP Server skill doesn't support custom endpoints, use the built-in ARC HTTP server variables and handle commands via global variables that GenesisBridge polls.

---

## Testing Procedures

### Test 1: Servo Movement
```javascript
// Test individual servo
MoveServo("D0", 90, 50);  // Head Tilt to center
Sleep(1000);
MoveServo("D0", 100, 50); // Tilt up
Sleep(1000);
MoveServo("D0", 80, 50);  // Tilt down
Sleep(1000);
MoveServo("D0", 90, 50);  // Return to center
```

### Test 2: Named Positions
```javascript
// Test predefined positions
MoveToPosition("STAND", 50);
Sleep(2000);
MoveToPosition("SIT", 50);
Sleep(2000);
MoveToPosition("ARMS_UP", 50);
Sleep(2000);
MoveToPosition("NEUTRAL", 50);
```

### Test 3: SSC-32 Virtual Servos
```javascript
// Test right hand (when installed)
MoveRightHand({
    "wrist": 90,
    "finger1": 45,
    "finger2": 45,
    "finger3": 45,
    "finger4": 45,
    "finger5": 45
});

// Grasp test
RightHandGrasp(90);  // Close
Sleep(2000);
RightHandGrasp(0);   // Open
```

### Test 4: IMU Monitoring
```javascript
// Check IMU variables
var tiltX = getVar('$IMU_GyroscopeX');
var tiltY = getVar('$IMU_GyroscopeY');
console.log("Tilt: X=" + tiltX + ", Y=" + tiltY);
```

### Test 5: Object Detection
```javascript
// Run YOLO detection
controlCommand("Darknet YOLO", "Run");
Sleep(1000);

// Check results
var count = getVar('$YOLONumberOfRegions');
var classes = getVar('$YOLOClasses');
console.log("Detected " + count + " objects");
for (var i = 0; i < count; i++) {
    console.log("  - " + classes[i]);
}
```

### Test 6: Genesis Communication
```bash
# From Python (Genesis side), test connection:
curl -X POST http://localhost:8080/genesis/command \
  -H "Content-Type: application/json" \
  -d '{"type":"servo_move","port":"D0","position":90,"speed":50}'
```

Expected response: Head Tilt servo moves to 90°

### Test 7: Emergency Stop
```javascript
// Trigger emergency stop
TriggerEmergencyStop("Testing emergency stop");

// Verify:
// - All servos disabled
// - Speech alert (if enabled)
// - Genesis notified

// Reset
ResetEmergencyStop();
```

---

## Troubleshooting

### Servos Not Moving
- [ ] Check servo power supply (6V, adequate current)
- [ ] Verify servo ports in Servo Configuration skill
- [ ] Test with manual servo control in ARC
- [ ] Check servo horn alignment (not binding)

### SSC-32 Not Responding
- [ ] Verify COM port assignment in Windows Device Manager
- [ ] Check TX/RX wiring (crossed: TX→RX, RX→TX)
- [ ] Verify baud rate matches (115200 default)
- [ ] Test with SSC-32 terminal software

### HTTP Server Not Responding
- [ ] Check Windows Firewall allows port 8080
- [ ] Verify no other application using port 8080
- [ ] Test with: `curl http://localhost:8080/status`
- [ ] Check HTTP Server skill is enabled

### IMU Variables Zero
- [ ] Verify I2C connection to EZ-B v4
- [ ] Check 3-In-1 IMU skill configuration
- [ ] Test with Variable Watch skill
- [ ] Ensure IMU is powered (3.3V or 5V)

### YOLO Not Detecting
- [ ] Verify `yolov3-tiny.weights` file in plugin folder
- [ ] Check Camera skill is streaming
- [ ] Ensure adequate lighting
- [ ] Test with known COCO objects (person, cup, chair)

### GenesisBridge Not Starting
- [ ] Check Script Collection is named "Script Manager"
- [ ] Verify GenesisBridge.js script saved correctly
- [ ] Check console for error messages
- [ ] Ensure all required skills are added to project

---

## Python Requirements (Genesis Side)

Install these in your Genesis Python environment:

```bash
pip install numpy opencv-python pyyaml aiohttp websockets
pip install openai-whisper sounddevice TTS
pip install ultralytics transformers segment-anything
pip install requests chromadb sqlalchemy
```

---

## Next Steps

After Phase 1 setup complete:

1. **Test all 18 DOF servos** individually
2. **Verify Genesis ↔ ARC communication** bidirectional
3. **Test sensor streaming** (IMU, camera, objects)
4. **Create Auto Position frames** for your robot
5. **Implement basic autonomous behaviors**
6. **Document any hardware-specific adjustments**

---

## Resources

- **GenesisBridge.js**: `/home/genesis/.hermes/skills/robotics/genesis-mission-control/references/GenesisBridge.js`
- **Phase 1 Plan**: `/home/genesis/.hermes/skills/robotics/genesis-mission-control/references/phase1-implementation-plan.md`
- **ARC Skills Reference**: `/home/genesis/.hermes/skills/robotics/genesis-mission-control/references/arc-skills-reference.md`
- **Synthiam Support**: https://synthiam.com/Support
- **SSC-32 Manual**: https://www.lynxmotion.com/p-98-ssc-32-servo-controller.aspx

---

**Version**: 0.1.0  
**Created**: April 15, 2026  
**For**: Mini BFF Genesis Humanoid (18 DOF + SSC-32)  
**Author**: Genesis AI for Roberto Cardenas @ BFF Robots
