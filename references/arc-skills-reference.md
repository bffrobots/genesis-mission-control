# ARC Skills Quick Reference Guide

## Core Skills for Genesis Mission Control

This reference documents all Synthiam ARC skills used in Genesis Mission Control, including configuration, variables, and control commands.

---

## 1. Camera Device

**Skill ID**: 16120  
**Category**: Camera  
**URL**: https://synthiam.com/Support/Skills/Camera/Camera-Device?id=16120

### Configuration
```
Camera Source: USB Camera or EZ-B Camera
Resolution: 640x480 (recommended for Genesis bridge)
FPS: 30
Tracking Modes: Object Detection, Color, Face, etc.
```

### Control Commands
```javascript
// Start/Stop Camera
controlCommand("Camera", "CameraStart");
controlCommand("Camera", "CameraStart", 0);  // By device index
controlCommand("Camera", "CameraStop");

// Check Status
var isActive = controlCommand("Camera", "IsCameraActive");

// Pause Processing
controlCommand("Camera", "PauseOn");
controlCommand("Camera", "PauseOff");
controlCommand("Camera", "PauseToggle");

// Tracking Modes
controlCommand("Camera", "CameraDisableTracking");  // Disable all
controlCommand("Camera", "CameraAutoTracking");     // Enable all
controlCommand("Camera", "CameraObjectTrackingEnable");
controlCommand("Camera", "CameraObjectTrackingDisable");
controlCommand("Camera", "CameraFaceTrackingEnable");
controlCommand("Camera", "CameraQRCodeTrackingEnable");

// Recording
controlCommand("Camera", "CameraRecordStart");
controlCommand("Camera", "CameraRecordStop");
controlCommand("Camera", "CameraSnapshot");  // Auto filename
controlCommand("Camera", "CameraSnapshot", "custom.jpg");
```

### Variables (Exposed to Scripts)
```javascript
// Object Tracking
$Camera_Object_X      // Horizontal position (0-1)
$Camera_Object_Y      // Vertical position (0-1)
$Camera_Object_Width  // Object width
$Camera_Object_Height // Object height

// Multiple objects add suffix: $Camera_Object_1_X, $Camera_Object_2_X, etc.

// Face Tracking
$Camera_Face_X
$Camera_Face_Y
$Camera_Face_Width
$Camera_Face_Height

// QR Code
$Camera_QRCode        // Decoded QR text

// Motion Detection
$Camera_Motion        // Motion detected (true/false)
```

### Event Handlers
```javascript
// Camera frame capture
EZB.Camera.OnFrame = function(frame) {
    console.log("Frame received: " + frame.width + "x" + frame.height);
    // Send to Genesis
    SendToGenesis("vision_frame", { frame: frame });
};
```

---

## 2. Darknet YOLO (Object Detection)

**Skill ID**: 19863  
**Category**: Camera  
**URL**: https://synthiam.com/Support/Skills/Camera/Darknet-YOLO-Obj-Detection?id=19863

### Installation (CRITICAL)
```bash
# Download weights file (required!)
wget https://pjreddie.com/media/files/yolov3-tiny.weights

# Copy to plugin folder
copy yolov3-tiny.weights "C:\ProgramData\ARC\Plugins\d1db5da7-8805-41eb-8a65-a548e2fe60f6\"
```

### Configuration
```
Mode: Continuous (auto-detect) or On-Demand
Model: Tiny COCO (35MB, included)
On Changes Script: (optional script to run when detection changes)
```

### Control Commands
```javascript
// Run detection (on-demand mode)
controlCommand("Darknet YOLO", "Run");
```

### Variables
```javascript
$YOLONumberOfRegions  // Number of detected objects
$YOLOClasses          // Array of class names (e.g., ["person", "cup"])
$YOLOScores           // Array of confidence scores (0-1)
```

### Example Usage
```javascript
// Check for objects
var count = getVar('$YOLONumberOfRegions');

if (count > 0) {
    var classes = getVar('$YOLOClasses');
    var scores = getVar('$YOLOScores');
    
    for (var i = 0; i < count; i++) {
        console.log("Found " + classes[i] + " (" + (scores[i] * 100) + "%)");
    }
    
    // Send to Genesis
    SendToGenesis("object_detection", {
        objects: classes.map(function(cls, i) {
            return { class: cls, confidence: scores[i] };
        }),
        count: count
    });
}
```

### Performance Notes
- **CPU Only**: No CUDA support
- **Speed**: ~30 FPS on modern CPU (Tiny model)
- **Accuracy**: Good for 90 COCO categories (people, animals, vehicles, household items)
- **Full Model**: 250MB, ~50 seconds per image (not recommended for real-time)

---

## 3. DepthSensor (Kinect/RealSense)

**Skill ID**: 15873  
**Category**: Misc  
**URL**: https://synthiam.com/Support/Skills/Misc/DepthSensor?id=15873

### Supported Hardware
| Device | Required Runtime |
|--------|-----------------|
| Kinect Xbox 360 | Kinect for Windows Runtime 1.8 |
| Kinect One | Kinect for Windows Runtime 2.0 |
| Asus Xtion Pro | OpenNI 2 + NITE 2 |

### Configuration (Asus Xtion Pro)
**Environment Variables** (Windows System Properties):
```
OPENNI2_REDIST=C:\Program Files (x86)\OpenNI2\Redist\
NITE2_REDIST=C:\Program Files (x86)\PrimeSense\NiTE2\Redist\
PATH=...;C:\Program Files (x86)\PrimeSense\NiTE2\Redist\;C:\Program Files (x86)\OpenNI2\Redist\;
```

**NITE.INI** (create in ARC folder):
```ini
[General]
DataDir=C:\Program Files (x86)\PrimeSense\NiTE2\Redist\NiTE2
[Log]
Verbosity=0
LogToConsole=1
LogToFile=1
```

### Variables (Skeleton Joints)
Each joint has Position (Vector3) and Rotation (Quaternion):

```javascript
// Position (meters from sensor)
$SpineBase_X, $SpineBase_Y, $SpineBase_Z
$SpineMid_X, $SpineMid_Y, $SpineMid_Z
$Neck_X, $Neck_Y, $Neck_Z
$Head_X, $Head_Y, $Head_Z
$ShoulderLeft_X, $ShoulderLeft_Y, $ShoulderLeft_Z
$ShoulderRight_X, $ShoulderRight_Y, $ShoulderRight_Z
$ElbowLeft_X, $ElbowLeft_Y, $ElbowLeft_Z
$ElbowRight_X, $ElbowRight_Y, $ElbowRight_Z
$WristLeft_X, $WristLeft_Y, $WristLeft_Z
$WristRight_X, $WristRight_Y, $WristRight_Z
$HandLeft_X, $HandLeft_Y, $HandLeft_Z
$HandRight_X, $HandRight_Y, $HandRight_Z
$HipLeft_X, $HipLeft_Y, $HipLeft_Z
$HipRight_X, $HipRight_Y, $HipRight_Z
$KneeLeft_X, $KneeLeft_Y, $KneeLeft_Z
$KneeRight_X, $KneeRight_Y, $KneeRight_Z
$AnkleLeft_X, $AnkleLeft_Y, $AnkleLeft_Z
$AnkleRight_X, $AnkleRight_Y, $AnkleRight_Z
$FootLeft_X, $FootLeft_Y, $FootLeft_Z
$FootRight_X, $FootRight_Y, $FootRight_Z

// Rotation (Quaternions)
$QSpineBase_X, $QSpineBase_Y, $QSpineBase_Z, $QSpineBase_W
$QHead_X, $QHead_Y, $QHead_Z, $QHead_W
// ... (same pattern for all joints)
```

### Expression Functions (for Mocap Mapping)
```javascript
// Vector operations
Vector2 ToVector2(double x, double y)
Vector3 ToVector3(double x, double y, double z)
Quaternion ToQuaternion(double x, double y, double z, double w)
Vector3 GetEuler(Quaternion q)  // Convert quaternion to Euler angles

// Angle calculations
double AngleBetween(Vector2 v1, Vector2 v2)
double AngleBetween(Vector3 v1, Vector3 v2)
double Normalize(double value, double start = 0, double end = 360)

// Math functions
Abs, Min, Max, Pow, Sqrt
Cos, Sin, Tan, Cosh, Sinh, Tanh, Acos, Asin, Atan, Atan2
```

### Example: Map Arm Motion to Robot
```javascript
// Calculate arm angle from shoulder to elbow
var shoulderX = getVar('$ShoulderRight_X');
var shoulderY = getVar('$ShoulderRight_Y');
var elbowX = getVar('$ElbowRight_X');
var elbowY = getVar('$ElbowRight_Y');

// Calculate angle
var angle = Math.atan2(elbowY - shoulderY, elbowX - shoulderX) * 180 / Math.PI;

// Map to robot servo (0-180 degrees)
var servoAngle = Normalize(angle + 90, 0, 180);

// Control robot arm
EZB.Servo.SetPosition(3, servoAngle, 50);
```

---

## 4. Auto Position (Gait)

**Skill ID**: 16057  
**Category**: Movement Panels  
**URL**: https://synthiam.com/Support/Skills/Movement-Panels/Auto-Position-Movement-Panel-Gait?id=16057

### Key Concepts
- **Frame**: A pose (snapshot of all servo positions)
- **Action**: A sequence of frames played in order
- **Movement Panel**: Directional controls (Forward, Reverse, Left, Right, Stop)

### Configuration
```
Transition Steps: 50 (smaller = smoother, more updates)
Transition Delay: 100ms (lower = faster)
Software Acceleration: 0 (disabled) or 1-100 (smoothing)
```

### Control Commands
```javascript
// Movement Panel Commands
controlCommand("Auto Position", "Forward");
controlCommand("Auto Position", "Reverse");
controlCommand("Auto Position", "Left");
controlCommand("Auto Position", "Right");
controlCommand("Auto Position", "Stop");

// Frame Control
controlCommand("Auto Position", "AutoPositionFrame", "STAND");
controlCommand("Auto Position", "AutoPositionFrame", "STAND", delay, steps, speed);
controlCommand("Auto Position", "AutoPositionFrameJump", "STAND");  // Instant jump

// Action Control
controlCommand("Auto Position", "AutoPositionAction", "WALK_FORWARD");

// Stop All
controlCommand("Auto Position", "AutoPositionStop");

// Show Current Pose
controlCommand("Auto Position", "ShowAutoPositionPose");

// Add Frame to Action
controlCommand("Auto Position", "AddFrameToAction", "ActionName");
controlCommand("Auto Position", "AddFrameToAction", delay, steps, speed, "ActionName");

// Add Pause to Action
controlCommand("Auto Position", "AddPauseToAction", delay_ms, "ActionName");
```

### Creating Frames
1. Open Auto Position skill
2. Go to **Frames** tab
3. Adjust servo positions manually (robot moves in real-time)
4. Click **Add Frame** and name it (e.g., "STAND", "SIT", "WAVE")
5. Repeat for all poses

### Creating Actions
1. Go to **Actions** tab
2. Click **Add Action** and name it
3. Add frames in sequence
4. Configure delay, steps, speed for each transition
5. Optionally add scripts between frames

### Example: Walk Sequence
```javascript
// Execute walk action
controlCommand("Auto Position", "AutoPositionAction", "WALK_FORWARD");

// Or use movement panel
controlCommand("Auto Position", "Forward");
Sleep(2000);  // Walk for 2 seconds
controlCommand("Auto Position", "Stop");
```

### Limitations
- **No Dynamic IK**: Cannot move end-effector to 3D coordinates programmatically
- **Pre-defined Frames Only**: Must create frames manually or via script
- **No Real-time Modification**: Frame positions cannot be altered during execution

---

## 5. The Better Navigator

**Skill ID**: 20956  
**Category**: Navigation  
**URL**: https://synthiam.com/Support/Skills/Navigation/The-Better-Navigator?id=20956

### Requirements
- **Positioning Source** (NMS Layer 3 Group 2):
  - Intel RealSense T265 (recommended)
  - Wheel encoder odometry
  - Hector SLAM (internal)
  
- **Depth/Lidar Sensor** (NMS Layer 3 Group 1):
  - 360° Lidar
  - Intel RealSense Depth Camera
  - Microsoft Kinect

### Configuration
```
Disregard Distance Low: 10 cm (filter noise)
Disregard Distance High: 500 cm (filter inaccurate far data)
Pause Navigation If Distance <: 30 cm
Pause Navigation Degree Range: 90° (45° left + 45° right)
Path Planning Resolution: 5 cm (micro-waypoint density)
Robot Personal Space Size: 40 cm (safety bubble)
Forward Speed: 50 (1-255, start slow)
Turn On Spot Speed: 50 (1-255)
Degrees of Forgiveness: 10° (accuracy before next waypoint)
```

### Pose Hint Types
| Type | Best For |
|------|----------|
| Hector | SLAM-only, feature-rich environments |
| External | Odometry-reliable setups |
| Average | Balanced Hector + External |
| Fused | **Recommended** for depth camera + pose sensor |
| Dynamic | Real-time updates with odometry |

### Control Commands
```javascript
// Start Navigation
controlCommand("The Better Navigator", "NavigateToWaypoint", "WaypointName");

// Stop Navigation
controlCommand("The Better Navigator", "StopNavigation");

// Set Status
controlCommand("The Better Navigator", "setNavigationStatusToNavigating");
controlCommand("The Better Navigator", "setNavigationStatusToPaused");

// Load/Save Map
controlCommand("The Better Navigator", "LoadMap", "map_name");
controlCommand("The Better Navigator", "SaveMap", "map_name");
```

### Variables
```javascript
$Navigator_Location_X        // Current X position (cm)
$Navigator_Location_Y        // Current Y position (cm)
$Navigator_Heading           // Current heading (degrees)
$Navigator_CurrentWayPoint   // Current waypoint name
$Navigator_CurrentWayPoint_X // Target X (cm)
$Navigator_CurrentWayPoint_Y // Target Y (cm)
$Navigator_SavedWayPoints    // Array of waypoint names
$Navigator_IsNavigating      // Navigation status (true/false)
```

### Setup Tips
1. **Starting Position**: Mark robot position on floor with tape
2. **Manual Mapping**: Drive robot manually to create initial map
3. **Waypoints**: Add waypoints at key locations (charging station, task areas)
4. **Speed**: Start slow (50/255) to maintain pose accuracy
5. **Personal Space**: Set to robot's maximum dimension + 10cm

---

## 6. HTTP Server

**Skill ID**: 16082  
**Category**: Remote Control  
**URL**: https://synthiam.com/Support/Skills/Remote-Control/HTTP-Server?id=16082

### Configuration
```
Port: 8080
Enable Authentication: No (for local dev)
CORS Enabled: Yes
Allowed Origins: *
```

### Endpoints
The HTTP Server skill exposes ARC controls via HTTP endpoints. Genesis uses this to send commands to ARC.

### Example: Send Command from Genesis (Python)
```python
import requests

# Send servo command
response = requests.post(
    "http://localhost:8080/genesis/command",
    json={
        "type": "servo_move",
        "port": 3,
        "position": 90,
        "speed": 50
    }
)

# Send speech command
response = requests.post(
    "http://localhost:8080/genesis/command",
    json={
        "type": "speak",
        "text": "Hello from Genesis!"
    }
)
```

### Receive Commands in ARC (JavaScript)
```javascript
// HTTP Server receives POST request
// GenesisBridge.js processes it in ReceiveFromGenesis() function

function ReceiveFromGenesis(jsonString) {
    var cmd = JSON.parse(jsonString);
    
    switch(cmd.type) {
        case "servo_move":
            EZB.Servo.SetPosition(cmd.port, cmd.position, cmd.speed);
            break;
        case "speak":
            EZB.Speech.Speak(cmd.text);
            break;
        // ... more command types
    }
}
```

### Security Notes
- **Local Development**: No authentication required
- **Production**: Enable authentication and use HTTPS
- **Firewall**: Allow port 8080 for local network access

---

## 7. Script Collection

**Skill ID**: 16045  
**Category**: Scripting  
**URL**: https://synthiam.com/Support/Skills/Scripting/Script-Collection?id=16045

### Purpose
Manage multiple scripts in a single control (Script Manager).

### Control Commands
```javascript
// Start a script by name
controlCommand("Script Manager", "ScriptStart", "MyScript");

// Start and wait for completion
controlCommand("Script Manager", "ScriptStartWait", "MyScript");

// Stop a script
controlCommand("Script Manager", "ScriptStop", "MyScript");

// Get status
var status = controlCommand("Script Manager", "GetStatus", "MyScript");
```

### Usage
1. Add Script Collection skill to project
2. Name it (e.g., "Script Manager")
3. Add multiple scripts (Init, behaviors, utilities)
4. Call scripts by name from other scripts or skills

### Example: Genesis Bridge Scripts
```
Script Manager (Script Collection)
├── GenesisBridge.js      // Main bridge to Genesis
├── SensorMonitor.js      // Sensor data collection
├── SafetyMonitor.js      // Emergency monitoring
├── TestServos.js         // Servo test routine
└── Calibration.js        // Robot calibration
```

---

## 8. Script (JavaScript)

**Skill ID**: 16089  
**Category**: Scripting  
**URL**: https://synthiam.com/Support/Skills/Scripting/Script?id=16089

### Supported Languages
- Blockly (visual programming)
- **JavaScript** (recommended for Genesis bridge)
- EZ-Script (ARC's native language)
- Python (ARC Pro only)

### Control Commands
```javascript
// Start script
controlCommand("Script", "ScriptStart");

// Start and wait
controlCommand("Script", "ScriptStartWait");

// Stop script
controlCommand("Script", "ScriptStop");

// Get status
var status = controlCommand("Script", "GetStatus");
```

### JavaScript API (Key Functions)
```javascript
// Variables
getVar('$VariableName');
setVar('$VariableName', value);

// Control Commands
controlCommand("SkillName", "Command", arg1, arg2);
controlCommandWait("SkillName", "Command");  // Wait for completion

// EZ-B Commands
EZB.Servo.SetPosition(port, position, speed);
EZB.Servo.Enable(port);
EZB.Servo.Disable(port);
EZB.Servo.DisableAll();

EZB.Speech.Speak(text);

// HTTP
HTTP.Get(url);
HTTP.Post(url, data, callback);

// Timing
Sleep(milliseconds);
setInterval(function, milliseconds);
setTimeout(function, milliseconds);

// Math
Math.sin, Math.cos, Math.tan, Math.atan2
Math.sqrt, Math.pow, Math.abs
Math.min, Math.max, Math.random
```

### Example: Genesis Bridge Script
```javascript
// See references/phase1-implementation-plan.md for full example

var genesisAPI = "http://localhost:8080/genesis";

function SendToGenesis(eventType, data) {
    var payload = JSON.stringify({
        type: eventType,
        data: data,
        timestamp: new Date().toISOString()
    });
    
    HTTP.Post(genesisAPI + "/event", payload, function(response) {
        console.log("Genesis response: " + response.statusCode);
    });
}
```

---

## 9. 3-In-1 IMU

**Skill ID**: 19886  
**Category**: I2C  
**URL**: https://synthiam.com/Support/Skills/I2c/3-in-1-IMU?id=19886

### Hardware
- EZ-Robot 3-In-1 IMU sensor
- Connects to EZ-B v4 I2C port

### Configuration
```
I2C Port: I2C-0 (default)
Update Rate: 100Hz
Variables Exposed: Enable all
```

### Variables
```javascript
// Accelerometer (m/s²)
$IMU_AccelerometerX
$IMU_AccelerometerY
$IMU_AccelerometerZ

// Gyroscope (degrees/sec)
$IMU_GyroscopeX
$IMU_GyroscopeY
$IMU_GyroscopeZ

// Compass (microteslas)
$IMU_CompassX
$IMU_CompassY
$IMU_CompassZ
```

### Example: Calculate Tilt Angle
```javascript
// Get gyroscope data
var gyroX = getVar('$IMU_GyroscopeX');
var gyroY = getVar('$IMU_GyroscopeY');

// Calculate tilt magnitude
var tilt = Math.sqrt(gyroX * gyroX + gyroY * gyroY);

// Check balance
if (tilt > 30.0) {
    // Critical - emergency stop
    EZB.Servo.DisableAll();
    EZB.Speech.Speak("Critical tilt detected!");
} else if (tilt > 15.0) {
    // Warning
    console.log("Balance warning: " + tilt.toFixed(1) + "°");
}
```

### Balance Monitoring (10Hz)
```javascript
setInterval(function() {
    var accelX = getVar('$IMU_AccelerometerX');
    var accelY = getVar('$IMU_AccelerometerY');
    var gyroX = getVar('$IMU_GyroscopeX');
    var gyroY = getVar('$IMU_GyroscopeY');
    
    // Send to Genesis
    SendToGenesis("imu_data", {
        accelerometer: { x: accelX, y: accelY, z: getVar('$IMU_AccelerometerZ') },
        gyroscope: { x: gyroX, y: gyroY, z: getVar('$IMU_GyroscopeZ') },
        compass: { x: getVar('$IMU_CompassX'), y: getVar('$IMU_CompassY'), z: getVar('$IMU_CompassZ') },
        timestamp: Date.now()
    });
}, 100);
```

---

## 10. Variable Watch

**Skill ID**: 16056  
**Category**: Scripting  
**URL**: https://synthiam.com/Support/Skills/Scripting/Variable-Watch?id=16056

### Purpose
Monitor variables in real-time for debugging.

### Usage
1. Add Variable Watch skill to project
2. Add variables to watch (e.g., `$IMU_GyroscopeX`, `$YOLONumberOfRegions`)
3. View values in real-time during execution

### Debugging Tips
- Monitor YOLO detections: `$YOLONumberOfRegions`, `$YOLOClasses`
- Monitor IMU: `$IMU_GyroscopeX`, `$IMU_AccelerometerY`
- Monitor Genesis bridge: Custom variables for connection status

---

## Additional Useful Skills

### MMA7455 Accelerometer
**Skill ID**: 16078  
**URL**: https://synthiam.com/Support/Skills/I2c/MMA7455-Accelerometer?id=16078

Alternative IMU if 3-In-1 not available.

### Servo Configuration
**Built-in Skill**

Configure servo ports, limits, and speeds.

### Speech Recognition
**Built-in Skill**

Configure microphone and speech-to-text settings.

---

## Control Command Reference

### Quick Syntax
```javascript
// Basic command
controlCommand("SkillName", "Command");

// With arguments
controlCommand("SkillName", "Command", arg1, arg2, arg3);

// Wait for completion
controlCommandWait("SkillName", "Command");

// Get return value
var result = controlCommand("SkillName", "Command");
```

### Common Commands by Category

**Camera**:
```javascript
controlCommand("Camera", "CameraStart");
controlCommand("Camera", "CameraStop");
controlCommand("Camera", "CameraSnapshot");
controlCommand("Camera", "CameraObjectTrackingEnable");
```

**Movement**:
```javascript
controlCommand("Auto Position", "Forward");
controlCommand("Auto Position", "Stop");
controlCommand("Auto Position", "AutoPositionFrame", "STAND");
```

**Scripting**:
```javascript
controlCommand("Script Manager", "ScriptStart", "MyScript");
controlCommand("Script", "ScriptStop");
```

**Vision**:
```javascript
controlCommand("Darknet YOLO", "Run");
```

---

## Troubleshooting

### Camera Not Starting
- Check camera is connected and recognized by Windows
- Verify camera index in `CameraStart` command
- Try different resolution (lower = more compatible)

### YOLO Not Detecting
- Verify `yolov3-tiny.weights` file is in plugin folder
- Check camera is streaming (YOLO needs camera input)
- Ensure adequate lighting

### IMU Variables Zero
- Verify I2C connection to EZ-B v4
- Check I2C port configuration in skill settings
- Test with Variable Watch skill

### HTTP Server Not Responding
- Verify port 8080 is not in use by another application
- Check Windows Firewall allows port 8080
- Test with `curl http://localhost:8080/status`

### Auto Position Jerky Motion
- Increase Steps value (smoother, more updates)
- Decrease Delay value (faster transitions)
- Enable Software Acceleration (smoothing)

---

## Resources

- **ARC Documentation**: https://synthiam.com/Support
- **Control Command Manual**: https://synthiam.com/Support/Programming/control-command
- **ARC Community Forum**: https://synthiam.com/Community
- **EZ-Script Manual**: https://synthiam.com/Support/Programming/ez-script

---

**Version**: 0.1.0  
**Created**: April 15, 2026  
**For**: Genesis Mission Control Phase 1
