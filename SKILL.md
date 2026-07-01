---
name: genesis-mission-control
description: Autonomous humanoid robot control system with Genesis AI as central brain - 21 DOF control, vision, speech, navigation, imitation learning, and decision making for EZ-B v4 + Synthiam ARC + NVIDIA Isaac Sim/GR00T
version: 0.1.0
author: Genesis (Roberto Cardenas @ BFF Robots)
license: MIT
dependencies: [synthiam-arc, ez-b-v4, transformers, openai-whisper, torch, opencv-python, ultralytics, segment-anything, mediapipe, stable-baselines3, chromadb, fastapi, websocket-client]
metadata:
  hermes:
    tags: [Humanoid Robot, Robotics, Autonomous Systems, Computer Vision, Speech Recognition, Motion Control, Imitation Learning, Reinforcement Learning, EZ-B, Synthiam ARC, NVIDIA Isaac Sim, GR00T, 21 DOF]
  hardware:
    controller: EZ-B v4 Smart Robot Controller
    dof: 21
    sensors: [RGB Camera, Kinect/RealSense Depth, IMU, GPS, Force Sensors, Microphone Array]
    servos: Head(3), Arms(12), Hands(12), Torso(2), Legs(12)
  software:
    primary: Synthiam ARC
    ml_platform: NVIDIA Isaac Sim / GR00T
    model_hub: Hugging Face

---

# Genesis Mission Control - Autonomous Humanoid Robot System

## Overview

Genesis Mission Control is a fully autonomous humanoid robot control system with Genesis (the AI agent) as the central brain and orchestrator. The system controls a 21 DOF humanoid robot with advanced perception, manipulation, and decision-making capabilities.

**Primary Platforms**:
- **Synthiam ARC** - Robot control and scripting (https://synthiam.com/Support)
- **EZ-B v4** - Hardware servo controller (https://www.ez-robot.com/store/p24/EZB-smart-robot-controller.html)
- **NVIDIA Isaac Sim / GR00T** - Simulation and imitation learning
- **Hugging Face** - Vision, speech, and decision models

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    GENESIS MISSION CONTROL                          │
│                         (Central Brain)                             │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   VISION     │  │   SPEECH     │  │  NAVIGATION  │              │
│  │   LAYER      │  │   LAYER      │  │    LAYER     │              │
│  │              │  │              │  │              │              │
│  │ • Object Det │  │ • STT (Whisper)│ │ • SLAM      │              │
│  │ • Face Rec   │  │ • TTS        │  │ • Path Plan │              │
│  │ • Depth Map  │  │ • Voice Cmd  │  │ • Obstacle  │              │
│  │ • Mocap Ext  │  │ • Speaker ID │  │ • GPS Track │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                 │                       │
│         └─────────────────┼─────────────────┘                       │
│                           ▼                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              DECISION & ORCHESTRATION LAYER                  │   │
│  │                                                              │   │
│  │  • Task Planning          • Skill Memory Retrieval          │   │
│  │  • Priority Management    • Learning & Adaptation           │   │
│  │  • Multi-modal Fusion     • Safety & Ethics                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                           │                                         │
│                           ▼                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                   MOTOR CONTROL LAYER                        │   │
│  │                                                              │   │
│  │  • 21 DOF Servo Control     • Balance & Gait               │   │
│  │  • Hand Grasping (6 DOF)    • Force Feedback               │   │
│  │  • Mocap Replay             • Trajectory Optimization      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                           │                                         │
└───────────────────────────┼─────────────────────────────────────────┘
                            ▼
              ┌─────────────────────────┐
              │      EZ-B v4            │
              │   Hardware Interface    │
              │                         │
              │  [Servos] [Sensors]     │
              │  [Audio] [Camera]       │
              └─────────────────────────┘
```

---

## Hardware Configuration

### 21 DOF Breakdown

| Body Part | DOF | Ports | Movement |
|-----------|-----|-------|----------|
| **Head** | 3 | D0-D2 | Pan, Tilt, Roll |
| **Left Arm** | 6 | D3-D8 | Shoulder(3), Elbow(1), Wrist(2) |
| **Right Arm** | 6 | D9-D14 | Shoulder(3), Elbow(1), Wrist(2) |
| **Left Hand** | 3 | D15-D17 | Grip, Finger joints |
| **Right Hand** | 3 | D18-D20 | Grip, Finger joints |
| **Torso** | 2 | D21-D22 | Waist Pan, Tilt |
| **Left Leg** | 6 | D23-D28 | Hip(3), Knee(1), Ankle(2) |
| **Right Leg** | 6 | D29-D34 | Hip(3), Knee(1), Ankle(2) |

**Note**: 21 DOF total (some configurations count hands as 6 DOF each = 33 total)

### Sensor Integration

| Sensor | Interface | Purpose |
|--------|-----------|---------|
| RGB Camera | USB-0 | Object recognition, face detection |
| Kinect/RealSense | USB-1 | Depth mapping, 3D scene, mocap |
| IMU (Accelerometer + Gyro) | I2C-0 | Balance, orientation |
| GPS Module | UART-0 | Outdoor navigation |
| Force Sensors (Hands/Feet) | ADC-0 to ADC-7 | Touch, pressure, grip force |
| Microphone Array | Audio-In | Speech capture |
| Speaker | Audio-Out | Speech output |
| IR/Distance Sensors | Digital/Analog | Obstacle detection |

### Power Requirements

- **Servos**: 6V, 3A peak per servo (use high-current servo bus)
- **EZ-B Controller**: 5V, 500mA
- **Sensors**: 5V/12V depending on device
- **Recommended Battery**: 12V 10Ah LiPo with BEC regulators
- **Total Peak Current**: ~15-20A during dynamic movement

---

## Core Capabilities

### 1. Vision & Object Recognition

**Models**: CLIP, YOLO, Segment Anything (SAM), Depth Anything

**Pipeline**:
- Real-time object detection and classification
- Face recognition for known individuals
- Depth map generation from Kinect/RealSense
- 3D scene reconstruction
- Motion capture extraction from video

**Quick Start**:
```python
from transformers import CLIPProcessor, CLIPModel
from segment_anything import SamPredictor
import cv2

# Initialize vision system
class GenesisVision:
    def __init__(self):
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.sam_predictor = SamPredictor.load_from_checkpoint("sam_vit_h_4b8939.pth")
        
    def recognize_objects(self, image, candidate_labels):
        """Detect and classify objects in image"""
        inputs = self.clip_processor(
            text=candidate_labels, 
            images=image, 
            return_tensors="pt", 
            padding=True
        )
        outputs = self.clip_model(**inputs)
        return outputs.logits_per_image.softmax(dim=1)
        
    def segment_objects(self, image, points=None, boxes=None):
        """Segment objects with SAM"""
        self.sam_predictor.set_image(image)
        masks, scores, logits = self.sam_predictor.predict(
            point_coords=points,
            point_labels=None,
            box=boxes,
            multimask_output=True
        )
        return masks, scores
        
    def extract_depth(self, depth_frame):
        """Process depth map from Kinect/RealSense"""
        # Convert to point cloud
        points = cv2.reprojectImageTo3D(depth_frame, self.Q_matrix)
        return points
```

### 2. Speech Processing

**Models**: Whisper (STT), Coqui TTS/Bark (TTS)

**Pipeline**:
- Multi-language speech-to-text (99 languages)
- Wake word detection ("Hey Genesis")
- Voice command parsing
- Natural, expressive text-to-speech
- Speaker identification

**Quick Start**:
```python
import whisper
from TTS.api import TTS

class GenesisSpeech:
    def __init__(self):
        # Speech-to-text
        self.stt_model = whisper.load_model("turbo")  # Fast, good quality
        
        # Text-to-speech
        self.tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", gpu=True)
        
    def listen(self, audio_path):
        """Convert speech to text"""
        result = self.stt_model.transcribe(audio_path, language="en")
        return result["text"]
        
    def speak(self, text, output_path="output.wav"):
        """Convert text to speech"""
        self.tts.tts_to_file(text=text, file_path=output_path)
        return output_path
        
    def parse_command(self, text):
        """Extract intent from voice command"""
        # Use LLM for command parsing
        command_structure = genesis.decide.parse_voice_command(text)
        return command_structure
```

### 3. Motor Control & Balance

**21 DOF Configuration**:
- Inverse kinematics for arms and legs
- Walking gait generation
- Balance control with Zero Moment Point (ZMP)
- Hand grasping primitives
- Fall detection and recovery

**EZ-B v4 Integration**:
```python
import requests
import websocket

class GenesisMotorControl:
    def __init__(self, arc_host="localhost", arc_port=8080):
        self.arc_host = arc_host
        self.arc_port = arc_port
        
    def move_servo(self, port, position, speed=100):
        """Move servo to position (0-180 degrees)"""
        cmd = {
            "type": "servo_move",
            "port": port,
            "position": position,
            "speed": speed
        }
        response = requests.post(
            f"http://{self.arc_host}:{self.arc_port}/command", 
            json=cmd
        )
        return response.json()
        
    def move_arm_ik(self, arm, x, y, z, roll, pitch, yaw):
        """Move arm using inverse kinematics"""
        # Calculate joint angles from end-effector pose
        joint_angles = self.solve_ik(arm, x, y, z, roll, pitch, yaw)
        
        # Send to EZ-B via ARC
        for port, angle in zip(self.get_arm_ports(arm), joint_angles):
            self.move_servo(port, angle, speed=50)
            
    def solve_ik(self, arm, x, y, z, roll, pitch, yaw):
        """Solve inverse kinematics for 6-DOF arm"""
        # Implement analytical or numerical IK solver
        # For 6-DOF: shoulder(3), elbow(1), wrist(2)
        import numpy as np
        from scipy.optimize import minimize
        
        def ik_objective(joint_angles):
            # Forward kinematics
            end_effector = self.forward_kinematics(arm, joint_angles)
            # Minimize distance to target
            return np.linalg.norm(end_effector - [x, y, z, roll, pitch, yaw])
            
        # Initial guess
        initial_guess = [0] * 6
        
        # Constraints: joint limits
        bounds = [(0, 180)] * 6
        
        result = minimize(ik_objective, initial_guess, bounds=bounds)
        return result.x
        
    def walk_gait(self, step_length, step_height, duration):
        """Generate walking gait pattern"""
        # ZMP-based gait generation
        gait_pattern = self.generate_zmp_gait(step_length, step_height)
        
        # Execute gait cycle
        for timestep, joint_config in gait_pattern:
            self.apply_joint_config(joint_config)
            time.sleep(duration / len(gait_pattern))
            
    def balance_recovery(self, imu_data):
        """Recover balance when tilt detected"""
        tilt_angle = imu_data["gyro"]["tilt"]
        
        if abs(tilt_angle) > 15.0:  # degrees threshold
            # Shift center of mass
            compensating_move = self.calculate_balance_compensation(tilt_angle)
            self.execute_compensating_move(compensating_move)
```

### 4. Motion Capture & Imitation Learning

**Pipeline**:
1. Record human demonstration (Kinect/RealSense + RGB)
2. Extract skeleton mocap data (MediaPipe, OpenPose, or Isaac Sim)
3. Retarget to robot kinematics
4. Store in skill memory
5. Replay and refine with reinforcement learning

**NVIDIA Isaac Sim / GR00T Integration**:
```python
# Motion capture extraction
import mediapipe as mp

class GenesisMocap:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        
    def extract_skeleton(self, video_path):
        """Extract 3D skeleton from video"""
        cap = cv2.VideoCapture(video_path)
        skeleton_frames = []
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Convert to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)
            
            if results.pose_landmarks:
                # Extract 33 pose landmarks
                landmarks = results.pose_landmarks.landmark
                skeleton_frames.append(landmarks)
                
        return skeleton_frames
        
    def retarget_to_robot(self, human_skeleton):
        """Retarget human motion to robot kinematics"""
        # Scale and map human joints to robot joints
        robot_joint_angles = []
        
        for frame in human_skeleton:
            # Map shoulder, elbow, wrist to robot arm
            arm_angles = self.map_arm_motion(frame)
            # Map hip, knee, ankle to robot leg
            leg_angles = self.map_leg_motion(frame)
            
            robot_joint_angles.append({
                "arms": arm_angles,
                "legs": leg_angles
            })
            
        return robot_joint_angles
        
    def store_skill(self, skill_name, demonstration_data):
        """Store learned skill in memory"""
        # Save to vector database for retrieval
        import chromadb
        client = chromadb.PersistentClient(path="./genesis_memory")
        collection = client.get_or_create_collection("motor_skills")
        
        collection.add(
            documents=[demonstration_data["description"]],
            embeddings=[self.embed_skill(demonstration_data)],
            metadatas=[{"skill_name": skill_name, "timestamp": datetime.now()}],
            ids=[skill_name]
        )
```

### 5. Skill Memory & Learning

**Memory Architecture**:
```
Genesis Memory Store
├── Procedural Skills (movement patterns)
│   ├── Walking gaits
│   ├── Grasping primitives
│   ├── Object manipulation
│   └── Balance recovery
├── Semantic Knowledge
│   ├── Object categories
│   ├── Spatial maps
│   └── Task procedures
├── Episodic Memory
│   ├── Interaction history
│   ├── Learning episodes
│   └── Success/failure logs
└── Learned Models
    ├── Fine-tuned vision models
    ├── Custom speech commands
    └── Adapted control policies
```

**Storage Implementation**:
```python
class GenesisMemory:
    def __init__(self):
        # Vector database for semantic search
        import chromadb
        self.vector_db = chromadb.PersistentClient(path="./genesis_memory/skills")
        
        # SQL database for structured data
        from sqlalchemy import create_engine
        self.sql_engine = create_engine("sqlite:///genesis_memory/structured.db")
        
    def store_skill(self, name, skill_data, embedding):
        """Store a learned skill"""
        collection = self.vector_db.get_or_create_collection("motor_skills")
        
        collection.add(
            documents=[skill_data["description"]],
            embeddings=[embedding],
            metadatas=[{
                "skill_name": name,
                "demonstration_count": skill_data["demo_count"],
                "success_rate": skill_data["success_rate"],
                "created_at": datetime.now().isoformat()
            }],
            ids=[name]
        )
        
    def retrieve_similar_skill(self, query, query_embedding, top_k=3):
        """Find similar skills for a task"""
        collection = self.vector_db.get_or_create_collection("motor_skills")
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas"]
        )
        
        return results
        
    def log_episode(self, episode_data):
        """Log an interaction episode"""
        # Store in SQL for structured queries
        with self.sql_engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO episodes (timestamp, task, success, reward, notes)
                VALUES (:timestamp, :task, :success, :reward, :notes)
            """), episode_data)
            conn.commit()
```

### 6. Autonomous Navigation

**Capabilities**:
- SLAM (Simultaneous Localization and Mapping)
- Path planning (A*, RRT, Dijkstra)
- Dynamic obstacle avoidance
- GPS outdoor navigation
- Indoor localization (visual markers, LiDAR)

**Navigation Stack**:
```python
from nav2_simple_commander import Navigator
import numpy as np

class GenesisNavigation:
    def __init__(self):
        self.navigator = Navigator()
        self.current_pose = None
        
    def navigate_to_pose(self, x, y, theta):
        """Navigate to target pose"""
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = "map"
        goal_pose.pose.position.x = x
        goal_pose.pose.position.y = y
        goal_pose.pose.orientation.z = np.sin(theta / 2)
        goal_pose.pose.orientation.w = np.cos(theta / 2)
        
        # Compute path
        path = self.navigator.compute_path_to_pose(goal_pose)
        
        # Execute via EZ-B motor control
        self.follow_path(path)
        
    def follow_path(self, path):
        """Follow computed path"""
        for waypoint in path.poses:
            # Convert to robot coordinates
            robot_command = self.waypoint_to_robot_command(waypoint)
            # Send to EZ-B
            genesis.motor.send_movement_command(robot_command)
            
    def avoid_obstacles(self, sensor_data):
        """Dynamic obstacle avoidance"""
        # Process depth sensor data
        obstacles = self.detect_obstacles(sensor_data["depth"])
        
        if obstacles:
            # Replan path
            new_path = self.replan_avoiding_obstacles(obstacles)
            self.follow_path(new_path)
            
    def gps_navigation(self, target_lat, target_lon):
        """Outdoor GPS navigation"""
        current_gps = self.get_gps_position()
        
        # Calculate bearing and distance
        bearing = self.calculate_bearing(current_gps, (target_lat, target_lon))
        distance = self.calculate_distance(current_gps, (target_lat, target_lon))
        
        # Navigate toward target
        while distance > 1.0:  # 1 meter tolerance
            self.move_forward()
            current_gps = self.get_gps_position()
            distance = self.calculate_distance(current_gps, (target_lat, target_lon))
```

### 7. Decision Making & Orchestration

**Genesis Brain Architecture**:
- Multi-agent system for parallel processing
- Priority-based task queue
- Real-time sensor fusion
- Safety-first decision making
- Continuous learning loop

**Decision Loop**:
```python
class GenesisDecision:
    def __init__(self):
        self.task_queue = PriorityQueue()
        self.current_context = {}
        
    def perception_loop(self):
        """Gather all sensor data"""
        sensor_data = {
            "vision": genesis.vision.get_current_scene(),
            "audio": genesis.speech.listen_continuous(),
            "imu": genesis.sensors.get_imu_data(),
            "gps": genesis.sensors.get_gps(),
            "force": genesis.sensors.get_force_data()
        }
        return sensor_data
        
    def understand(self, sensor_data):
        """Interpret scene, commands, context"""
        # Multi-modal fusion
        scene_understanding = self.fuse_sensor_data(sensor_data)
        
        # Extract intents
        if sensor_data["audio"]["command"]:
            intent = self.parse_command(sensor_data["audio"]["command"])
            scene_understanding["intent"] = intent
            
        return scene_understanding
        
    def plan(self, goal, context):
        """Generate action sequence with constraints"""
        # Retrieve relevant skills
        skills = genesis.memory.retrieve_similar_skill(goal)
        
        # Create plan
        plan = []
        for subtask in self.decompose_goal(goal):
            action = self.select_best_action(subtask, skills, context)
            plan.append(action)
            
        return plan
        
    def execute(self, plan):
        """Send commands to motor/speech/vision layers"""
        for action in plan:
            if action["type"] == "move":
                genesis.motor.execute(action)
            elif action["type"] == "speak":
                genesis.speech.speak(action["text"])
            elif action["type"] == "grasp":
                genesis.motor.grasp_object(action["pose"])
                
            # Monitor execution
            feedback = self.monitor_execution(action)
            if feedback["status"] == "failed":
                self.recover_from_failure(action, feedback)
                
    def learn(self, outcome):
        """Store outcomes, update models, refine skills"""
        # Log episode
        genesis.memory.log_episode(outcome)
        
        # Update skill if successful
        if outcome["success"]:
            genesis.memory.update_skill(outcome["skill_name"], outcome)
            
        # Reinforcement learning update
        if outcome["reward"] is not None:
            self.rl_update(outcome["policy"], outcome["reward"])
```

---

## Integration with Synthiam ARC

### Critical ARC JavaScript Limitations (Lessons Learned)

**⚠️ ARC JavaScript does NOT support `console.log()`**
- **Error**: `Execution Error - console is not defined`
- **Solution**: Use `setVar('$VariableName', message)` for logging
- **Monitor**: Add Variable Watch skill to view `$GenesisBridge_Log`

**⚠️ ARC JavaScript does NOT support `setInterval()` or `setTimeout()`**
- **Error**: `setInterval is not defined`
- **Solution 1**: Use `while (true) { code; Sleep(100); }` loop (works universally)
- **Solution 2**: If Script Collection has timer settings, use `OnTimer()` event function
- **Note**: Some ARC versions don't expose timer settings - use while+Sleep as fallback

**⚠️ ARC JavaScript does NOT support `Sleep()` in all contexts**
- **Error**: `Sleep is not defined`
- **Solution**: Only works inside script execution, not in event handlers
- **Alternative**: Use Script Collection timer events if available

**⚠️ ARC JavaScript does NOT support `True`/`False` constants**
- **Error**: `True is not defined`
- **Solution**: Use lowercase `true`/`false` or `1`/`0`
- **Example**: `while (1)` or `while (true)` instead of `while (True)`

**⚠️ Variables MUST be initialized before reading**
- **Error**: `Variable not defined: $Servo_D0`
- **Solution**: Call `setVar('$VariableName', initialValue)` before any `getVar()` calls
- **Pattern**: Initialize all variables in `OnScriptStart()` or script init section

**⚠️ ARC HTTP Server does NOT support custom REST endpoints**
- **Cannot do**: `POST /genesis/command`, `POST /genesis/event`
- **Can do**: Read/write variables via `/get.html` and `/set.html`
- **Pattern**: 
  - Genesis → ARC: `GET /set.html?var=$Genesis_Command&val={json}`
  - ARC → Genesis: `HTTP.Post("http://localhost:8080/arc/event", payload)`

**⚠️ Script Collection must match exact name**
- **Error**: `Robot skill named 'Script Manager' does not exist`
- **Solution**: Rename Script Collection skill to match controlCommand() calls
- **Or**: Update script to use actual skill name

### ARC JavaScript Syntax Rules

**❌ NOT Supported**:
```javascript
setInterval(fn, 1000);           // Use while+Sleep or OnTimer()
console.log("msg");              // Use setVar('$Log', "msg")
const x = 5; let y = 10;         // Use var only
const fn = () => { };            // Use function fn() { }
`Value: ${x}`;                   // Use "Value: " + x
while (True) { }                 // Use while (true) or while (1)
[1, 2, 3].map(x => x * 2);       // Use for loop
```

**✅ Use These Instead**:
```javascript
// Loop with timing
while (true) {
    myFunction();
    Sleep(100);
}

// Logging
function Log(message) {
    setVar('$GenesisBridge_Log', message);
}

// Variable declaration
var x = 5;
var y = 10;

// Functions
function myFunction() {
    return x;
}

// String concatenation
var msg = "Value: " + x;

// Initialize variables before reading
setVar('$MyVar', -1);  // Initialize
var val = getVar('$MyVar');  // Now safe to read
```

### ARC Logging Pattern

```javascript
// ❌ WRONG - Will cause execution error
console.log("Message");

// ✅ CORRECT - ARC-compatible logging
function Log(message) {
    setVar('$GenesisBridge_Log', message);
}

Log("Genesis Bridge initialized");
```

### ARC ↔ Genesis Communication Architecture

```
┌─────────────────┐                    ┌─────────────────┐
│   GENESIS       │                    │      ARC        │
│   (Python)      │                    │   (JavaScript)  │
│                 │                    │                 │
│  FastAPI        │◄──── POST ──────── │  HTTP.Post()    │
│  Port: 8080     │    (sensor data)   │                 │
│                 │                    │                 │
│  HTTP Client    │──── GET ──────────►│  HTTP Server    │
│  /set.html      │    (commands)      │  /set.html      │
│  ?var=          │                    │  ?var=          │
│  $Genesis_      │                    │  $Genesis_      │
│  Command        │                    │  Command        │
└─────────────────┘                    └─────────────────┘
```

**Genesis → ARC** (Commands):
```python
import requests
import json

def send_command_to_arc(command_type, **kwargs):
    cmd = {"type": command_type, **kwargs}
    requests.get(
        "http://localhost:8080/set.html",
        params={"var": "$Genesis_Command", "val": json.dumps(cmd)}
    )
```

**ARC → Genesis** (Sensor Data):
```javascript
function SendToGenesis(eventType, data) {
    var payload = JSON.stringify({
        type: eventType,
        data: data,
        timestamp: new Date().toISOString()
    });
    HTTP.Post("http://localhost:8080/arc/event", payload);
}
```

**ARC Polling** (check for commands every 500ms):
```javascript
setInterval(function() {
    var commandJson = getVar('$Genesis_Command');
    if (commandJson && commandJson !== "") {
        var cmd = JSON.parse(commandJson);
        ReceiveFromGenesis(cmd);
        setVar('$Genesis_Command', "");  // Clear after processing
    }
}, 500);
```

### ARC HTTP Server Variable Access

**Read Variable**:
```bash
curl "http://localhost:8080/get.html?var=\$BatteryVoltage"
```

**Write Variable**:
```bash
curl "http://localhost:8080/set.html?var=\$TestVar&val=hello"
```

**In JavaScript**:
```javascript
// Read
var value = getVar('$VariableName');

// Write
setVar('$VariableName', value);
```

### Script Collection Setup

1. Add **Script Collection** skill to ARC project
2. **Rename skill** to match your controlCommand calls (e.g., "Script Manager")
3. Add scripts via **Add Script** button
4. Start script:
   ```javascript
   controlCommand("Script Manager", "ScriptStart", "ScriptName");
   ```

### Common ARC JavaScript Functions

```javascript
// Variables
getVar('$VariableName');
setVar('$VariableName', value);

// Control Commands
controlCommand("SkillName", "Command", arg1, arg2);
controlCommand("Script Manager", "ScriptStart", "MyScript");

// HTTP
HTTP.Get(url);
HTTP.Post(url, payload, callback);

// Timing
Sleep(milliseconds);
setInterval(function, milliseconds);

// EZ-B Hardware
EZB.Servo.SetPosition(port, position, speed);
EZB.Servo.Enable(port);
EZB.Servo.DisableAll();
EZB.Speech.Speak(text);
```

### Genesis Bridge JavaScript Template

```javascript
// ARC Logging Helper
function Log(message) {
    setVar('$GenesisBridge_Log', message);
}

// Poll for Genesis commands
setInterval(function() {
    var cmdJson = getVar('$Genesis_Command');
    if (cmdJson && cmdJson !== "") {
        var cmd = JSON.parse(cmdJson);
        // Process command...
        setVar('$Genesis_Command', "");  // Clear
    }
}, 500);

// Send data to Genesis
function SendToGenesis(eventType, data) {
    HTTP.Post("http://localhost:8080/arc/event", 
        JSON.stringify({type: eventType, data: data}));
}

// Initialize
Log("Script starting...");
```

---

## Integration with Synthiam ARC (Original Content)

### ARC JavaScript Bridge

```javascript
// Genesis Bridge - connects ARC to Genesis AI
// Add this script in Synthiam ARC

var genesisAPI = "http://localhost:8080/genesis";
var wsConnection = null;

function InitializeGenesisBridge() {
    console.log("Initializing Genesis Bridge...");
    
    // Connect WebSocket for real-time communication
    wsConnection = new WebSocket("ws://localhost:8080/genesis/ws");
    
    wsConnection.onopen = function() {
        console.log("Connected to Genesis");
        SendToGenesis("system_ready", { timestamp: new Date().toISOString() });
    };
    
    wsConnection.onmessage = function(event) {
        ReceiveFromGenesis(event.data);
    };
    
    // Set up sensor event handlers
    SetupSensorEvents();
}

function SendToGenesis(eventType, data) {
    var payload = JSON.stringify({
        type: eventType,
        data: data,
        timestamp: new Date().toISOString()
    });
    
    if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
        wsConnection.send(payload);
    } else {
        // Fallback to HTTP
        HTTP.Post(genesisAPI + "/event", payload, function(response) {
            console.log("Genesis response:", response);
        });
    }
}

function SetupSensorEvents() {
    // Camera frames
    EZB.Camera.OnFrame = function(frame) {
        // Downsample for bandwidth
        var downsampled = ResizeFrame(frame, 640, 480);
        SendToGenesis("vision_frame", { 
            frame: downsampled, 
            source: "main_camera",
            timestamp: Date.now()
        });
    };
    
    // Speech recognition
    EZB.SpeechRecognition.OnRecognized = function(text, confidence) {
        SendToGenesis("voice_command", { 
            text: text, 
            confidence: confidence,
            timestamp: Date.now()
        });
    };
    
    // IMU data
    EZB.IMU.OnUpdate = function(accel, gyro) {
        SendToGenesis("imu_data", { 
            accelerometer: accel, 
            gyroscope: gyro,
            timestamp: Date.now()
        });
    };
    
    // Distance sensors
    EZB.Distance.OnUpdate = function(port, distance) {
        SendToGenesis("distance_sensor", {
            port: port,
            distance: distance,
            timestamp: Date.now()
        });
    };
}

function ReceiveFromGenesis(jsonString) {
    var cmd = JSON.parse(jsonString);
    
    console.log("Genesis command:", cmd.type);
    
    switch(cmd.type) {
        case "servo_move":
            EZB.Servo.SetPosition(cmd.port, cmd.position, cmd.speed);
            break;
            
        case "speak":
            EZB.Speech.Speak(cmd.text);
            break;
            
        case "move_base":
            ExecuteMovement(cmd.command, cmd.duration);
            break;
            
        case "play_sound":
            EZB.Sound.Play(cmd.soundFile);
            break;
            
        case "enable_servos":
            EZB.Servo.Enable(cmd.ports);
            break;
            
        case "disable_servos":
            EZB.Servo.Disable(cmd.ports);
            break;
            
        case "emergency_stop":
            EZB.Servo.DisableAll();
            EZB.Speech.Speak("Emergency stop activated");
            break;
            
        default:
            console.log("Unknown command type:", cmd.type);
    }
}

function ExecuteMovement(command, duration) {
    switch(command) {
        case "forward":
            EZB.Movement.Forward(duration);
            break;
        case "backward":
            EZB.Movement.Backward(duration);
            break;
        case "left":
            EZB.Movement.Left(duration);
            break;
        case "right":
            EZB.Movement.Right(duration);
            break;
        case "stop":
            EZB.Movement.Stop();
            break;
    }
}

// Initialize on script load
InitializeGenesisBridge();
```

### Genesis Python Bridge

```python
import asyncio
import websockets
import json
from datetime import datetime

class GenesisARCBridge:
    def __init__(self, host="localhost", port=8080):
        self.host = host
        self.port = port
        self.ws_uri = f"ws://{host}:{port}/genesis/ws"
        self.http_url = f"http://{host}:{port}/genesis"
        self.ws = None
        
    async def connect(self):
        """Connect to ARC WebSocket"""
        self.ws = await websockets.connect(self.ws_uri)
        print(f"Connected to Genesis at {self.ws_uri}")
        
    async def send_command(self, command_type, **kwargs):
        """Send command to ARC"""
        cmd = {
            "type": command_type,
            **kwargs,
            "timestamp": datetime.now().isoformat()
        }
        
        if self.ws:
            await self.ws.send(json.dumps(cmd))
        else:
            # Fallback to HTTP
            import aiohttp
            async with aiohttp.ClientSession() as session:
                await session.post(f"{self.http_url}/command", json=cmd)
                
    async def send_servo_move(self, port, position, speed=100):
        """Move a servo"""
        await self.send_command("servo_move", port=port, position=position, speed=speed)
        
    async def send_speak(self, text):
        """Make robot speak"""
        await self.send_command("speak", text=text)
        
    async def send_movement(self, command, duration=1000):
        """Send movement command"""
        await self.send_command("move_base", command=command, duration=duration)
        
    async def send_emergency_stop(self):
        """Emergency stop all systems"""
        await self.send_command("emergency_stop")
        
    async def receive_events(self):
        """Listen for sensor events from ARC"""
        async for message in self.ws:
            event = json.loads(message)
            await self.process_event(event)
            
    async def process_event(self, event):
        """Process incoming sensor event"""
        event_type = event["type"]
        data = event["data"]
        
        if event_type == "vision_frame":
            await genesis.vision.process_frame(data["frame"])
        elif event_type == "voice_command":
            await genesis.speech.process_command(data["text"], data["confidence"])
        elif event_type == "imu_data":
            genesis.sensors.update_imu(data)
        elif event_type == "distance_sensor":
            genesis.sensors.update_distance(data["port"], data["distance"])
            
    async def run(self):
        """Main event loop"""
        await self.connect()
        
        # Run receive loop in background
        receive_task = asyncio.create_task(self.receive_events())
        
        # Run Genesis decision loop
        await genesis.run_autonomous_loop()
        
        await receive_task
```

---

## Implementation Phases

### Phase 1: Foundation (Weeks 1-4)
- [ ] Set up Synthiam ARC with EZ-B v4 integration
- [ ] Basic servo control for all 21 DOF
- [ ] IMU integration for balance sensing
- [ ] Speech-to-text with Whisper
- [ ] Text-to-speech integration
- [ ] Basic voice command parsing
- [ ] Genesis-ARC WebSocket bridge

### Phase 2: Perception (Weeks 5-8)
- [ ] Camera integration with ARC
- [ ] Object detection (YOLO/CLIP)
- [ ] Depth sensing with Kinect/RealSense
- [ ] Face recognition system
- [ ] Visual SLAM setup
- [ ] Multi-modal sensor fusion

### Phase 3: Motion & Manipulation (Weeks 9-12)
- [ ] Inverse kinematics for arms and legs
- [ ] Walking gait generation
- [ ] Balance control with ZMP
- [ ] Hand grasping primitives
- [ ] Motion capture extraction pipeline
- [ ] Fall detection and recovery

### Phase 4: Learning & Memory (Weeks 13-16)
- [ ] Skill memory database (Chroma)
- [ ] Imitation learning from demos
- [ ] Isaac Sim simulation setup
- [ ] Sim-to-real transfer pipeline
- [ ] Reinforcement learning for skill refinement
- [ ] Episodic memory logging

### Phase 5: Autonomy (Weeks 17-20)
- [ ] Full navigation stack
- [ ] Task planning system
- [ ] Multi-modal decision making
- [ ] Autonomous task execution
- [ ] Continuous learning loop
- [ ] Priority-based task queue

### Phase 6: Advanced Capabilities (Weeks 21-24)
- [ ] NVIDIA GR00T integration
- [ ] Advanced manipulation skills
- [ ] Social interaction capabilities
- [ ] Multi-robot coordination (optional)
- [ ] Edge deployment optimization
- [ ] Production hardening

---

## Safety Systems

### Critical Safety Features

1. **Emergency Stop**
   - Physical button on robot
   - Voice command: "Genesis stop"
   - Remote emergency via app

2. **Force Limiting**
   - Current monitoring on all servos
   - Automatic shutdown on overcurrent
   - Soft grip force control

3. **Balance Recovery**
   - IMU-based tilt detection
   - Automatic compensation movements
   - Controlled fall if unrecoverable

4. **Collision Avoidance**
   - Real-time obstacle detection
   - Dynamic path replanning
   - Safe speed near humans

5. **Thermal Monitoring**
   - Servo temperature sensors
   - Automatic derating on overheating
   - Cooldown periods

### Safety Implementation

```python
class SafetyMonitor:
    def __init__(self):
        self.emergency_stop = False
        self.force_limits = {port: 2.5 for port in range(35)}  # Amps
        self.balance_threshold = 15.0  # degrees
        self.servo_temps = {}
        
    def check_emergency_conditions(self, sensor_data):
        """Check all safety conditions"""
        # Emergency stop button
        if sensor_data.get("estop_pressed"):
            self.trigger_emergency_stop("E-stop button pressed")
            return True
            
        # Balance check
        tilt = abs(sensor_data["imu"]["tilt"])
        if tilt > self.balance_threshold:
            self.initiate_balance_recovery(sensor_data["imu"])
            
        # Servo current check
        for port, current in sensor_data.get("servo_current", {}).items():
            if current > self.force_limits[port]:
                self.stop_servo(port)
                print(f"Servo {port} overcurrent: {current}A")
                
        # Temperature check
        for port, temp in sensor_data.get("servo_temp", {}).items():
            if temp > 70.0:  # Celsius
                self.stop_servo(port)
                print(f"Servo {port} overheated: {temp}C")
                
        return False
        
    def trigger_emergency_stop(self, reason):
        """Emergency stop all systems"""
        self.emergency_stop = True
        
        # Disable all servos except critical ones
        genesis.motor.disable_all_servos()
        
        # Alert user
        genesis.speech.speak(f"Emergency stop: {reason}")
        
        # Log incident
        genesis.memory.log_episode({
            "type": "emergency_stop",
            "reason": reason,
            "timestamp": datetime.now()
        })
        
    def initiate_balance_recovery(self, imu_data):
        """Attempt to recover balance"""
        tilt_angle = imu_data["tilt"]
        tilt_direction = imu_data["tilt_direction"]
        
        # Calculate compensating movement
        compensation = self.calculate_balance_compensation(tilt_angle, tilt_direction)
        
        # Execute recovery
        genesis.motor.execute_compensation(compensation)
```

---

## API Reference

### Genesis Core API

```python
# Initialize Genesis
genesis = GenesisMissionControl(
    arc_host="localhost",
    arc_port=8080,
    enable_vision=True,
    enable_speech=True,
    enable_navigation=True,
    enable_learning=True
)

# Lifecycle
genesis.initialize()  # Start all subsystems
genesis.shutdown()    # Graceful shutdown

# Perception
objects = genesis.vision.detect_objects()
faces = genesis.vision.recognize_faces()
depth = genesis.vision.get_depth_map()
mocap = genesis.vision.extract_mocap(video_path)
scene = genesis.vision.understand_scene()

# Speech
text = genesis.speech.listen()  # STT
genesis.speech.speak(text)      # TTS
command = genesis.speech.parse_command(text)
genesis.speech.set_voice("female", "calm")

# Movement
genesis.motor.move_servo(port, position, speed)
genesis.motor.move_arm_ik(arm, x, y, z, roll, pitch, yaw)
genesis.motor.walk_to(x, y, theta)
genesis.motor.grasp_object(object_pose)
genesis.motor.replay_skill(skill_name)
genesis.motor.balance_recovery()

# Learning
genesis.learn.store_skill(name, demonstration_data)
genesis.learn.retrieve_similar_skill(query)
genesis.learn.train_with_rl(skill_name, reward_fn)
genesis.learn.update_policy(policy, trajectory)

# Navigation
genesis.navigate.to_pose(x, y, theta)
genesis.navigate.follow_path(path)
genesis.navigate.avoid_obstacles()
genesis.navigate.gps_to(lat, lon)

# Decision
action = genesis.decide.next_action(context)
plan = genesis.decide.create_plan(goal)
genesis.decide.execute_plan(plan)

# Memory
memories = genesis.memory.search(query, top_k=5)
genesis.memory.log_episode(episode_data)
genesis.memory.update_skill(skill_name, outcome)
```

---

## Dependencies

### Python Packages

```txt
# Core
numpy>=1.24.0
opencv-python>=4.8.0
torch>=2.0.0
transformers>=4.30.0

# Vision
ultralytics>=8.0.0  # YOLO
segment-anything>=1.0  # SAM
mediapipe>=0.10.0  # Mocap

# Speech
openai-whisper>=20230314  # STT
TTS>=0.20.0  # Coqui TTS

# Robotics
pyezrobot>=1.0.0  # EZ-B communication
nav2-simple-commander>=0.2.0  # Navigation

# Learning
stable-baselines3>=2.0.0  # RL
gymnasium>=0.28.0  # RL environments

# Memory
chromadb>=0.4.0  # Vector storage
sqlalchemy>=2.0.0  # Structured storage

# Communication
websocket-client>=1.6.0
fastapi>=0.100.0  # API server
uvicorn>=0.23.0  # ASGI server
```

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU | NVIDIA RTX 3060 | RTX 4090 |
| CPU | 8 cores (i7/Ryzen 7) | 16 cores (i9/Ryzen 9) |
| RAM | 32GB | 64GB |
| Storage | 1TB SSD | 2TB NVMe SSD |
| OS | Ubuntu 22.04 LTS | Ubuntu 24.04 LTS |

---

## Troubleshooting

### Common Issues

**Servo jitter or instability**:
- Check power supply voltage and current capacity
- Verify servo horn alignment and mechanical binding
- Reduce speed settings in ARC
- Add software filtering to IMU data
- Use separate power bus for servos

**Speech recognition failures**:
- Improve microphone placement and quality
- Add noise reduction preprocessing
- Use speaker adaptation with Whisper
- Implement wake word detection to reduce false triggers
- Check audio sample rate (16kHz recommended)

**Balance issues during walking**:
- Calibrate IMU zero offsets
- Adjust ZMP parameters for robot's weight distribution
- Reduce walking speed initially
- Implement adaptive gait based on terrain
- Check mechanical play in leg joints

**Simulation to real-world gap**:
- Add domain randomization in Isaac Sim
- Use system identification to match sim to real dynamics
- Start with conservative control parameters
- Implement sim-to-real adaptation layer
- Gradually increase task complexity

**WebSocket connection drops**:
- Implement reconnection logic with exponential backoff
- Use heartbeat/ping-pong for connection health
- Buffer events during disconnection
- Log connection state changes

---

## Future Enhancements

1. **Multi-modal Learning**: Combine vision, touch, and proprioception for richer representations
2. **Meta-Learning**: Learn to learn new skills faster with few-shot learning
3. **Social Cognition**: Understand human intentions, emotions, and social cues
4. **Collaborative Tasks**: Work alongside humans safely with shared task understanding
5. **Edge Optimization**: Quantize models for onboard deployment (GGUF, TensorRT)
6. **Swarm Coordination**: Multiple Genesis robots working together
7. **Cloud Integration**: Offload heavy computation when needed
8. **Haptic Feedback**: Advanced force feedback for delicate manipulation
9. **Energy Optimization**: Power-aware motion planning and task scheduling
10. **Self-Diagnosis**: Automated fault detection and recovery

---

## Resources

- **Synthiam ARC Documentation**: https://synthiam.com/Support
- **EZ-B v4 Manual**: https://www.ez-robot.com/store/p24/EZB-smart-robot-controller.html
- **NVIDIA Isaac Sim**: https://developer.nvidia.com/isaac-sim
- **NVIDIA GR00T**: https://developer.nvidia.com/project-gr00t
- **Hugging Face Robotics**: https://huggingface.co/robotics
- **ROS 2 Navigation**: https://navigation.ros.org/
- **MediaPipe Pose**: https://google.github.io/mediapipe/solutions/pose

---

## Version History

- **v0.1.0** (April 15, 2026): Initial skill creation - comprehensive architecture, hardware configuration, implementation plan, and integration guides for Genesis Mission Control
