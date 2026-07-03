# Claude Code Integration Guide

Genesis Mission Control integrates with **Claude Code** (Anthropic's CLI agent) for autonomous code generation, debugging, and robot programming.

## Overview

Claude Code can:
- Generate servo control code
- Debug robot behaviors
- Create new motion sequences
- Analyze camera feed data
- Write test scripts
- Refactor Genesis backend code

```
┌─────────────────────────────────────────────────────────────┐
│  Developer                                                   │
│  - Natural language commands                                │
│  - "Claude, make the robot wave"                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Claude Code (Anthropic CLI)                                │
│  - Code generation                                          │
│  - File editing                                             │
│  - Terminal execution                                       │
│  - Git operations                                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Genesis Mission Control                                    │
│  - Execute generated code                                   │
│  - Servo control via API                                    │
│  - Camera feed access                                       │
│  - Voice chat integration                                   │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### 1. Install Claude Code

```bash
# Install via npm
npm install -g @anthropic-ai/claude-code

# Or via pip
pip install claude-code
```

### 2. Authenticate

```bash
claude login
# Follow authentication prompts
```

### 3. Configure for Genesis

Create `.claude/settings.json` in Genesis directory:

```json
{
  "allowedTools": ["Bash", "Write", "Read", "Edit", "Glob"],
  "forbiddenTools": ["WebFetch"],
  "customInstructions": "You are working with Genesis Mission Control, a humanoid robot control system. Always test servo code in simulation first before running on real hardware. Safety first: validate servo positions (0-180 degrees) and implement emergency stop.",
  "environmentVariables": {
    "GENESIS_API_URL": "http://localhost:5000",
    "ARC_HTTP_URL": "http://localhost:8080"
  }
}
```

## Usage Examples

### 1. Generate Motion Sequence

**Command:**
```bash
claude "Create a Python function that makes Genesis wave hello by moving servos D3, D4, D5 in sequence. Save it as scripts/wave_motion.py"
```

**Claude will generate:**
```python
# scripts/wave_motion.py
import requests
import time

def wave_hello():
    """Wave hello using right arm (servos D3, D4, D5)"""
    api_url = "http://localhost:5000/api/servo"
    
    # Wave positions
    positions = [
        {"D3": 90, "D4": 45, "D5": 60},   # Up
        {"D3": 90, "D4": 135, "D5": 120}, # Down
        {"D3": 90, "D4": 45, "D5": 60},   # Up
        {"D3": 90, "D4": 135, "D5": 120}, # Down
        {"D3": 90, "D4": 90, "D5": 90},   # Home
    ]
    
    for pos in positions:
        for servo_id, position in pos.items():
            requests.post(api_url, json={
                "servo_id": int(servo_id[1:]),
                "position": position
            })
        time.sleep(0.5)
    
    print("✅ Wave complete!")

if __name__ == "__main__":
    wave_hello()
```

**Then run:**
```bash
python scripts/wave_motion.py
```

### 2. Debug Servo Issues

**Command:**
```bash
claude "The robot's right arm (servos D3-D5) isn't moving smoothly. Check the servo_backend.py code and fix any timing or position issues."
```

**Claude will:**
1. Read `scripts/main.py` (servo backend)
2. Identify timing issues
3. Suggest fixes
4. Apply patches with your approval

### 3. Create Camera Object Detection

**Command:**
```bash
claude "Add YOLO object detection to the camera feed. When an object is detected, save its position to a file that the web interface can read."
```

**Claude will generate:**
```python
# scripts/camera_detection.py
import cv2
from ultralytics import YOLO
import json
import time

model = YOLO('yolov8n.pt')
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    results = model(frame)
    
    detections = []
    for result in results:
        boxes = result.boxes
        for box in boxes:
            detections.append({
                "class": model.names[int(box.cls)],
                "confidence": float(box.conf),
                "bbox": box.xyxy[0].tolist(),
                "timestamp": time.time()
            })
    
    # Save for web interface
    with open('/tmp/detections.json', 'w') as f:
        json.dump(detections, f)

cap.release()
```

### 4. Create Test Suite

**Command:**
```bash
claude "Write pytest tests for the servo backend API. Test position validation, rate limiting, and error handling."
```

**Claude will generate:**
```python
# tests/test_servo_backend.py
import pytest
import requests
import time

BASE_URL = "http://localhost:5000"

def test_valid_servo_position():
    """Test valid servo position (0-180)"""
    response = requests.post(
        f"{BASE_URL}/api/servo",
        json={"servo_id": 0, "position": 90}
    )
    assert response.status_code == 200

def test_invalid_position_too_high():
    """Test position > 180 should fail"""
    response = requests.post(
        f"{BASE_URL}/api/servo",
        json={"servo_id": 0, "position": 200}
    )
    assert response.status_code == 400

def test_invalid_position_negative():
    """Test negative position should fail"""
    response = requests.post(
        f"{BASE_URL}/api/servo",
        json={"servo_id": 0, "position": -10}
    )
    assert response.status_code == 400

def test_rate_limiting():
    """Test rate limiting (max 10 commands/sec)"""
    for i in range(15):
        response = requests.post(
            f"{BASE_URL}/api/servo",
            json={"servo_id": 0, "position": 90}
        )
        if i >= 10:
            assert response.status_code == 429  # Too Many Requests
```

**Then run:**
```bash
pytest tests/test_servo_backend.py -v
```

### 5. Autonomous Code Improvement

**Command:**
```bash
claude "Refactor the voice-chat-server.py to add better error handling, logging, and support for multiple LLM models (not just Ollama)."
```

**Claude will:**
1. Analyze current code
2. Identify improvements
3. Refactor with better structure
4. Add logging throughout
5. Add support for OpenAI, Anthropic APIs
6. Write migration guide

## Advanced Integration Patterns

### Pattern 1: Claude as Code Reviewer

Add to CI/CD pipeline:

```yaml
# .github/workflows/claude-review.yml
name: Claude Code Review

on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Claude Review
        run: |
          claude "Review this PR for safety issues, bugs, and performance. Focus on servo control code."
```

### Pattern 2: Claude as Pair Programmer

Interactive session:

```bash
# Start Claude in interactive mode
claude --interactive

# Then have a conversation:
# You: "Let's add a new dance motion to Genesis"
# Claude: "Sure! What style of dance?"
# You: "Something simple, like the macarena"
# Claude: *generates code*
# You: "Can you make it smoother?"
# Claude: *refactors code*
```

### Pattern 3: Claude for Documentation

```bash
claude "Generate comprehensive documentation for all API endpoints in Genesis Mission Control. Include example requests and responses for each."
```

**Output:** `docs/API-REFERENCE.md` with full endpoint documentation.

### Pattern 4: Claude for Bug Triage

```bash
claude "Analyze the last 10 GitHub issues for Genesis. Categorize them by severity and suggest fixes for the top 3 critical issues."
```

## Safety Guidelines

When using Claude Code with Genesis:

### 1. Always Validate Servo Positions

```python
# Claude should include this in all servo code
def validate_position(position):
    assert 0 <= position <= 180, "Position must be 0-180 degrees"
    return True
```

### 2. Implement Emergency Stop

```python
# Every motion script should have E-STOP
import signal

def emergency_stop(signum, frame):
    print("🛑 E-STOP ACTIVATED")
    requests.post("http://localhost:5000/api/estop")
    exit(0)

signal.signal(signal.SIGINT, emergency_stop)
```

### 3. Test in Simulation First

```bash
# Before running on real robot
claude "Create a simulation mode for this motion that visualizes it without moving real servos"
```

### 4. Rate Limit Commands

```python
# Prevent servo burnout
from time import sleep

def move_servo_safe(servo_id, position):
    sleep(0.1)  # Minimum 100ms between commands
    requests.post(f"{BASE_URL}/api/servo", json={...})
```

## Example Workflow: Complete Feature

**Task:** Add "dance mode" to Genesis

**Step 1: Ask Claude to design**
```bash
claude "Design a dance mode feature for Genesis robot. It should:
1. Load dance sequences from JSON files
2. Sync movements to music tempo
3. Support multiple dance styles
4. Have smooth transitions between moves

Create a design document first."
```

**Step 2: Review design**
```bash
# Claude generates DANCE_DESIGN.md
# You review and approve
```

**Step 3: Implement**
```bash
claude "Implement the dance mode feature according to the design. Create:
1. scripts/dance_controller.py
2. dances/wave.json
3. dances/macarena.json
4. tests/test_dance.py"
```

**Step 4: Test**
```bash
claude "Run the tests and fix any failures"
```

**Step 5: Document**
```bash
claude "Write user documentation for the dance mode feature"
```

## Configuration Files

### Claude Config for Genesis

```json
// .claude/settings.json
{
  "allowedTools": [
    "Bash",
    "Write",
    "Read",
    "Edit",
    "Glob",
    "Grep"
  ],
  "forbiddenTools": [
    "WebFetch",
    "TodoWrite"
  ],
  "customInstructions": "You are Genesis Mission Control AI assistant. You help users program a 18 DOF humanoid robot. SAFETY FIRST: Always validate servo positions (0-180°), implement emergency stop, and test in simulation before real hardware. Use Python for backend, JavaScript for web interface.",
  "environmentVariables": {
    "GENESIS_API_URL": "http://localhost:5000",
    "ARC_HTTP_URL": "http://localhost:8080",
    "OLLAMA_URL": "http://localhost:11434"
  },
  "autoApprove": [
    "Read",
    "Glob"
  ],
  "requireApproval": [
    "Write",
    "Edit",
    "Bash"
  ]
}
```

### Example Dance Sequence

```json
// dances/wave.json
{
  "name": "Wave Hello",
  "tempo": 120,
  "moves": [
    {
      "name": "arm_up",
      "servos": {"D3": 90, "D4": 45, "D5": 60},
      "duration": 0.5
    },
    {
      "name": "arm_down",
      "servos": {"D3": 90, "D4": 135, "D5": 120},
      "duration": 0.5
    },
    {
      "name": "arm_up",
      "servos": {"D3": 90, "D4": 45, "D5": 60},
      "duration": 0.5
    },
    {
      "name": "arm_down",
      "servos": {"D3": 90, "D4": 135, "D5": 120},
      "duration": 0.5
    },
    {
      "name": "home",
      "servos": {"D3": 90, "D4": 90, "D5": 90},
      "duration": 0.5
    }
  ]
}
```

## Troubleshooting

### Claude Not Following Instructions

**Issue:** Claude generates unsafe code

**Solution:** Add stricter custom instructions:
```json
"customInstructions": "NEVER generate servo code without position validation (0-180). ALWAYS include emergency stop. NEVER bypass safety checks."
```

### Claude Can't Access API

**Issue:** API calls fail

**Solution:** Ensure environment variables are set:
```bash
export GENESIS_API_URL=http://localhost:5000
claude "Test the servo API"
```

### Slow Code Generation

**Issue:** Claude takes too long

**Solution:** Be more specific:
```bash
# Instead of:
claude "Add camera support"

# Use:
claude "Add YOLO object detection to camera feed. Save detections to /tmp/detections.json. Use ultralytics YOLOv8n model."
```

## Resources

- **Claude Code Docs:** https://docs.anthropic.com/claude-code
- **Genesis Mission Control:** https://github.com/bffrobots/genesis-mission-control
- **Best Practices:** https://docs.anthropic.com/claude-code/best-practices

---

**Last Updated:** June 30, 2026  
**Version:** 1.0.0
