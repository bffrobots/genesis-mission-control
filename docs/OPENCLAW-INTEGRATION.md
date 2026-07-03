# OpenClaw Integration Guide

Genesis Mission Control integrates with **OpenClaw** for advanced robotic manipulation and control.

## Overview

OpenClaw provides low-level hardware abstraction and control, while Genesis Mission Control handles high-level AI decision making and user interaction.

```
┌─────────────────────────────────────────────────────────────┐
│  Genesis Mission Control                                    │
│  - AI Decision Making (Ollama + Whisper)                   │
│  - Web Interface (Motion Control, Camera, Voice)           │
│  - Task Planning & Orchestration                           │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API / WebSocket
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  OpenClaw                                                   │
│  - Hardware Abstraction Layer                              │
│  - Servo Control (PWM, position, velocity)                 │
│  - Sensor Fusion (IMU, encoders, force sensors)            │
│  - Kinematics (forward/inverse)                            │
└──────────────────────┬──────────────────────────────────────┘
                       │ Serial/USB
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Robot Hardware                                             │
│  - Servos (Dynamixel, LewanSoul, etc.)                     │
│  - Sensors (IMU, camera, force)                            │
│  - Actuators                                                 │
└─────────────────────────────────────────────────────────────┘
```

## Integration Architecture

### Method 1: REST API Bridge (Recommended)

OpenClaw exposes a REST API that Genesis can call for hardware control.

**Setup:**

1. **Install OpenClaw:**
   ```bash
   git clone https://github.com/openclaw/openclaw.git
   cd openclaw
   pip install -e .
   ```

2. **Start OpenClaw Server:**
   ```bash
   openclaw-server --port 9000
   ```

3. **Create Genesis ↔ OpenClaw Bridge:**
   ```python
   # scripts/openclaw_bridge.py
   import requests
   from flask import Flask, request, jsonify

   app = Flask(__name__)
   OPENCLAW_URL = "http://localhost:9000"

   @app.route('/api/openclaw/servo', methods=['POST'])
   def move_servo():
       """Forward servo command to OpenClaw"""
       data = request.json
       servo_id = data.get('servo_id')
       position = data.get('position')
       
       # Convert to OpenClaw format
       response = requests.post(
           f"{OPENCLAW_URL}/servo/{servo_id}/position",
           json={"position": position, "speed": 50}
       )
       
       return jsonify({"success": True, "openclaw_response": response.json()})

   @app.route('/api/openclaw/pose', methods=['POST'])
   def set_pose():
       """Set entire robot pose via OpenClaw"""
       data = request.json
       positions = data.get('positions')  # Dict of {servo_id: position}
       
       response = requests.post(
           f"{OPENCLAW_URL}/pose",
           json={"servos": positions, "duration": 2.0}
       )
       
       return jsonify({"success": True})

   @app.route('/api/openclaw/home', methods=['POST'])
   def home_position():
       """Move to home position"""
       response = requests.post(f"{OPENCLAW_URL}/home")
       return jsonify({"success": True})

   if __name__ == '__main__':
       app.run(host='0.0.0.0', port=9001)
   ```

4. **Update Genesis Web Interface:**
   
   Add OpenClaw toggle in settings, then modify `sendServoCommand()`:
   ```javascript
   function sendServoCommand(servoId, position) {
     if (STATE.useOpenClaw) {
       // Use OpenClaw backend
       fetch('http://localhost:9001/api/openclaw/servo', {
         method: 'POST',
         headers: {'Content-Type': 'application/json'},
         body: JSON.stringify({servo_id: servoId, position: position})
       });
     } else {
       // Use ARC backend (default)
       fetch('http://localhost:5000/api/servo', {
         method: 'POST',
         headers: {'Content-Type': 'application/json'},
         body: JSON.stringify({servo_id: servoId, position: position})
       });
     }
   }
   ```

### Method 2: Direct Python Integration

For tighter integration, import OpenClaw directly in Genesis backend.

```python
# scripts/genesis_with_openclaw.py
from openclaw.robot import Robot
from openclaw.kinematics import KinematicsSolver
import flask

app = flask.Flask(__name__)
robot = Robot(config="mini_bff_genesis.yaml")
kinematics = KinematicsSolver(robot)

@app.route('/api/arm/ik', methods=['POST'])
def inverse_kinematics():
    """Solve inverse kinematics for arm"""
    data = flask.request.json
    x, y, z = data['x'], data['y'], data['z']
    
    # Solve IK
    joint_angles = kinematics.solve_arm(x, y, z)
    
    # Execute via OpenClaw
    robot.set_servos(joint_angles)
    
    return flask.jsonify({"success": True, "angles": joint_angles})

@app.route('/api/walk', methods=['POST'])
def walk():
    """Execute walking gait"""
    data = flask.request.json
    steps = data['steps']
    direction = data['direction']
    
    # OpenClaw gait execution
    robot.walk(steps=steps, direction=direction)
    
    return flask.jsonify({"success": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## OpenClaw Features for Genesis

### 1. Advanced Servo Control

```python
from openclaw import Robot

robot = Robot()

# Position control (like ARC)
robot.set_servo_position(servo_id=0, position=90)

# Velocity control (not available in ARC)
robot.set_servo_velocity(servo_id=0, velocity=45)  # deg/sec

# Torque control (advanced)
robot.set_servo_torque(servo_id=0, torque=50)  # % of max torque

# Read feedback
current_pos = robot.get_servo_position(servo_id=0)
current_load = robot.get_servo_load(servo_id=0)
```

### 2. Inverse Kinematics

```python
from openclaw.kinematics import KinematicsSolver

kinematics = KinematicsSolver(robot)

# Arm IK
arm_angles = kinematics.solve_arm(x=0.2, y=0.1, z=0.3, roll=0, pitch=0, yaw=0)
robot.set_servos(arm_angles)

# Leg IK (for walking)
leg_angles = kinematics.solve_leg(leg='left', x=0.05, y=0.0, z=-0.15)
robot.set_servos(leg_angles)
```

### 3. Gait Generation

```python
from openclaw.gait import TripodGait, RippleGait

# Tripod gait (fast, for hexapods)
gait = TripodGait(robot, step_length=0.1, height=0.05)
robot.execute_gait(gait, cycles=5)

# Ripple gait (stable, for hexapods)
gait = RippleGait(robot, step_length=0.08, height=0.03)
robot.execute_gait(gait, cycles=5)
```

### 4. Sensor Fusion

```python
from openclaw.sensors import IMU, ForceSensor

imu = IMU(port='/dev/ttyUSB0')
force = ForceSensor(port='/dev/ttyUSB1')

# Read fused sensor data
orientation = imu.get_orientation()  # Roll, pitch, yaw
acceleration = imu.get_acceleration()
foot_contact = force.get_contact()  # Boolean per foot

# Use for balance
if orientation['roll'] > 15:
    robot.compensate_balance(orientation)
```

## Example: Voice-Controlled Robot with OpenClaw

```python
# scripts/voice_openclaw.py
import whisper
from openclaw.robot import Robot
import requests

robot = Robot()
stt_model = whisper.load_model("turbo")

def process_voice_command(audio_file):
    """Convert speech to robot action via OpenClaw"""
    
    # Transcribe
    result = stt_model.transcribe(audio_file)
    command = result["text"].lower()
    
    # Parse and execute
    if "wave" in command:
        robot.play_animation("wave", speed=1.0)
    
    elif "pick up" in command:
        # IK-based grasping
        arm_angles = robot.kinematics.solve_arm(x=0.2, y=0.0, z=0.1)
        robot.set_servos(arm_angles)
        robot.close_gripper()
    
    elif "walk forward" in command:
        robot.walk(steps=10, direction='forward')
    
    elif "balance" in command:
        # Enable balance compensation
        robot.enable_balance_compensation(True)
    
    return f"Executed: {command}"

# Integrate with Genesis Voice & Chat
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data['message']
    
    # If voice command, process with OpenClaw
    if is_robot_command(message):
        response = process_voice_command(message)
    else:
        # Regular AI chat via Ollama
        response = ollama_chat(message)
    
    return jsonify({"response": response})
```

## Configuration Files

### OpenClaw Robot Config (`mini_bff_genesis.yaml`)

```yaml
robot:
  name: "Mini BFF Genesis"
  dof: 18
  
servos:
  head:
    - id: 0
      name: "Head Pan"
      type: "LX-16A"
      min: 0
      max: 180
      home: 90
    - id: 1
      name: "Head Tilt"
      type: "LX-16A"
      min: 0
      max: 180
      home: 90
  
  right_arm:
    - id: 3
      name: "R Shoulder Pan"
      type: "LX-16A"
      min: 0
      max: 180
      home: 90
    - id: 4
      name: "R Shoulder Tilt"
      type: "LX-16A"
      min: 0
      max: 180
      home: 90
    - id: 5
      name: "R Elbow"
      type: "LX-16A"
      min: 0
      max: 180
      home: 90
  
  # ... continue for all 18 servos

kinematics:
  arm:
    link_lengths: [0.1, 0.15, 0.1]
    dof: 3
  leg:
    link_lengths: [0.1, 0.15, 0.1]
    dof: 3

sensors:
  imu:
    port: "/dev/ttyUSB0"
    type: "MPU6050"
  camera:
    port: "/dev/video0"
    resolution: [640, 480]
```

## API Reference

### Genesis ↔ OpenClaw Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/openclaw/servo` | POST | Move single servo |
| `/api/openclaw/pose` | POST | Set entire pose |
| `/api/openclaw/home` | POST | Return to home |
| `/api/openclaw/ik/arm` | POST | Arm inverse kinematics |
| `/api/openclaw/ik/leg` | POST | Leg inverse kinematics |
| `/api/openclaw/walk` | POST | Execute walking gait |
| `/api/openclaw/sensors` | GET | Read all sensors |
| `/api/openclaw/balance` | POST | Enable/disable balance |

### Example Requests

**Move Servo:**
```bash
curl -X POST http://localhost:9001/api/openclaw/servo \
  -H "Content-Type: application/json" \
  -d '{"servo_id": 0, "position": 90}'
```

**Inverse Kinematics:**
```bash
curl -X POST http://localhost:9001/api/openclaw/ik/arm \
  -H "Content-Type: application/json" \
  -d '{"x": 0.2, "y": 0.1, "z": 0.3}'
```

**Walk:**
```bash
curl -X POST http://localhost:9001/api/openclaw/walk \
  -H "Content-Type: application/json" \
  -d '{"steps": 10, "direction": "forward"}'
```

## Troubleshooting

### OpenClaw Not Connecting

```bash
# Check serial ports
ls -la /dev/ttyUSB*

# Test OpenClaw directly
openclaw-cli --list-servos

# Check permissions
sudo usermod -a -G dialout $USER
# Logout and back in
```

### Latency Issues

- Use direct Python integration (Method 2) instead of REST bridge
- Reduce servo update rate (10-20 Hz is usually sufficient)
- Use threaded execution for non-critical tasks

### Kinematics Not Solving

- Verify link lengths in config match your robot
- Check if target position is in workspace
- Use `kinematics.is_reachable(x, y, z)` to verify

## Resources

- **OpenClaw Documentation:** https://github.com/openclaw/openclaw
- **Genesis Mission Control:** https://github.com/bffrobots/genesis-mission-control
- **Kinematics Tutorial:** https://openclaw.readthedocs.io/kinematics

---

**Last Updated:** June 30, 2026  
**Version:** 1.0.0
