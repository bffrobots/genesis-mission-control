# Agentic AI Platform Integration

Genesis Mission Control integrates seamlessly with major AI agent platforms for autonomous robot control.

## Overview

Genesis Mission Control provides multiple integration points for AI agents:

- **HTTP API**: RESTful endpoints for servo control, chat, and status
- **WebSocket**: Real-time bidirectional communication
- **Native Skill**: Direct integration with Hermes Agent
- **File-based**: Simple text file interface for ARC variables

---

## Hermes Agent (Native)

**Status:** ✅ Native Skill

### Loading the Skill

```python
# Load the skill
skill_view("genesis-mission-control")

# Use in cron jobs
cronjob(action='create', 
        prompt="Monitor Genesis robot status and log any issues",
        skills=["genesis-mission-control"],
        schedule="*/5 * * * *")
```

### Available Functions

The skill provides direct access to:
- Servo control (18 DOF)
- Camera feed access
- Voice command processing
- Autonomous decision making
- System monitoring

### Example: Autonomous Monitoring

```python
from hermes_tools import skill_view, terminal

# Load skill
skill = skill_view("genesis-mission-control")

# Check robot status
result = terminal(command="curl http://localhost:5001/status")
print(result)
```

---

## LangChain Integration

**Status:** 🔧 Custom Tools Required

### Installation

```bash
pip install langchain langchain-community requests
```

### Tool Definitions

```python
from langchain.tools import Tool
import requests

# Servo Control Tool
def move_servo(port: str, position: int) -> str:
    """
    Move robot servo to specified position.
    
    Args:
        port: Servo port (e.g., "D0", "D1", ..., "D17")
        position: Position in degrees (0-180)
    
    Returns:
        Success/failure message
    """
    try:
        response = requests.post(
            "http://localhost:5000/api/servo",
            json={"servo_id": int(port[1:]), "position": position, "port": port},
            timeout=5
        )
        if response.status_code == 200:
            return f"✅ Servo {port} moved to {position}°"
        return f"❌ Failed: {response.text}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Camera Status Tool
def get_camera_status() -> str:
    """Check if camera stream is active."""
    try:
        response = requests.get("http://localhost:8097/live", timeout=2)
        return "✅ Camera stream active" if response.status_code == 200 else "❌ Camera offline"
    except:
        return "❌ Camera offline"

# Chat Tool
def send_chat_message(message: str) -> str:
    """Send message to Genesis AI and get response."""
    try:
        response = requests.post(
            "http://localhost:5001/chat",
            json={"message": message},
            timeout=10
        )
        return response.json().get("response", "No response")
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Create LangChain tools
servo_tool = Tool(
    name="move_servo",
    func=move_servo,
    description="Move robot servo to position (0-180 degrees). Input: 'port,position' e.g., 'D0,90'"
)

camera_tool = Tool(
    name="get_camera_status",
    func=get_camera_status,
    description="Check if robot camera is online and streaming"
)

chat_tool = Tool(
    name="genesis_chat",
    func=send_chat_message,
    description="Send a message to Genesis AI and get a response"
)

tools = [servo_tool, camera_tool, chat_tool]
```

### Agent Configuration

```python
from langchain.agents import initialize_agent, AgentType
from langchain.llms import Ollama

# Initialize LLM
llm = Ollama(model="llama3.1", base_url="http://localhost:11434")

# Create agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Use agent
agent.run("Wave at the camera by moving servos D3, D4, D5 in sequence")
```

---

## AutoGen Integration

**Status:** ✅ Ready

### Installation

```bash
pip install pyautogen
```

### Agent Configuration

```python
from autogen import AssistantAgent, UserProxyAgent

# Genesis Robot Agent
genesis_robot = AssistantAgent(
    name="Genesis_Robot",
    system_message="""You are Genesis, an autonomous humanoid robot controller.
    
Capabilities:
- Control 18 DOF servos (ports D0-D17, range 0-180 degrees)
- Stream live camera feed from localhost:8097
- Process voice commands and chat
- Execute autonomous behaviors

Safety Rules:
- Never move servos beyond 0-180 degree range
- Always check current position before moving
- Stop immediately if "E-STOP" command is received
- Prioritize human safety above all tasks

API Endpoints:
- POST http://localhost:5000/api/servo (servo control)
- GET http://localhost:5001/status (system status)
- POST http://localhost:5001/chat (AI chat)
""",
    llm_config={"config_list": [{"model": "llama3.1", "base_url": "http://localhost:11434"}]}
)

# User Proxy (for approval)
user_proxy = UserProxyAgent(
    name="Human_Operator",
    system_message="Human operator who approves robot actions",
    human_input_mode="ALWAYS",
    code_execution_config=False
)

# Start conversation
user_proxy.initiate_chat(
    genesis_robot,
    message="Pick up the cup from the table using your right arm"
)
```

### Multi-Agent Collaboration

```python
from autogen import GroupChat, GroupChatManager

# Define specialized agents
planner = AssistantAgent(
    name="Planner",
    system_message="You plan complex robot tasks by breaking them into steps"
)

operator = AssistantAgent(
    name="Operator",
    system_message="You execute robot commands safely"
)

monitor = AssistantAgent(
    name="Monitor",
    system_message="You watch camera feedback and detect issues"
)

# Group chat
groupchat = GroupChat(
    agents=[planner, operator, monitor, genesis_robot],
    messages=[],
    max_round=10
)

manager = GroupChatManager(
    groupchat=groupchat,
    llm_config={"config_list": [{"model": "llama3.1", "base_url": "http://localhost:11434"}]}
)

# Execute task
user_proxy.initiate_chat(
    manager,
    message="Navigate to the kitchen and report what you see"
)
```

---

## CrewAI Integration

**Status:** ✅ Ready

### Installation

```bash
pip install crewai
```

### Role Definitions

```python
from crewai import Agent, Task, Crew, Process

# Robot Operator Agent
robot_operator = Agent(
    role='Robot Operator',
    goal='Control Genesis humanoid robot safely and precisely',
    backstory='''Expert in humanoid robot motion control with 10+ years experience.
    Specializes in smooth, natural movements and safe human-robot interaction.''',
    tools=[servo_tool, camera_tool],
    verbose=True,
    allow_delegation=False
)

# Vision Analyst Agent
vision_analyst = Agent(
    role='Vision Analyst',
    goal='Analyze camera feed to detect objects and people',
    backstory='''Computer vision expert specializing in real-time object detection
    and scene understanding for robotics applications.''',
    tools=[camera_tool],
    verbose=True
)

# Task Planner Agent
task_planner = Agent(
    role='Task Planner',
    goal='Break down complex tasks into executable robot commands',
    backstory='''Strategic planner with expertise in robot task decomposition
    and motion planning for humanoid robots.''',
    verbose=True
)

# Define Tasks
pick_up_task = Task(
    description='''1. Analyze camera feed to locate cup
    2. Plan arm trajectory to reach cup
    3. Execute grasp motion with right hand
    4. Lift cup to chest height
    5. Confirm successful grasp''',
    expected_output='Cup picked up successfully',
    agent=robot_operator
)

vision_task = Task(
    description='''1. Monitor camera feed during operation
    2. Detect cup position (x, y coordinates)
    3. Track hand position relative to cup
    4. Report success when cup is grasped''',
    expected_output='Object detection report with coordinates',
    agent=vision_analyst
)

# Create Crew
crew = Crew(
    agents=[task_planner, robot_operator, vision_analyst],
    tasks=[pick_up_task, vision_task],
    verbose=2,
    process=Process.sequential
)

# Execute
result = crew.kickoff()
print(result)
```

---

## API Reference

### Servo Control

**Endpoint:** `POST http://localhost:5000/api/servo`

**Request:**
```json
{
  "servo_id": 0,
  "position": 90,
  "port": "D0",
  "timestamp": 1234567890
}
```

**Response:**
```json
{
  "success": true,
  "message": "Servo D0 moved to 90°",
  "servo_id": 0,
  "position": 90
}
```

### System Status

**Endpoint:** `GET http://localhost:5001/status`

**Response:**
```json
{
  "status": "ok",
  "robot": "mini-bff-genesis",
  "robot_name": "Genesis",
  "ollama": {
    "available": true,
    "model": "llama3.1"
  },
  "arc": {
    "available": true,
    "port": 8080
  }
}
```

### AI Chat

**Endpoint:** `POST http://localhost:5001/chat`

**Request:**
```json
{
  "message": "Navigate to the kitchen"
}
```

**Response:**
```json
{
  "response": "I'll navigate to the kitchen now. Starting motion planning...",
  "intent": "navigate",
  "location": "kitchen"
}
```

---

## Security Considerations

### Authentication

For production deployments, implement authentication:

```python
from functools import wraps
from flask import request, abort

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token != f"Bearer {os.getenv('API_TOKEN')}":
            abort(403)
        return f(*args, **kwargs)
    return decorated

@app.route('/api/servo', methods=['POST'])
@require_auth
def servo_control():
    # ... servo control code
```

### Rate Limiting

Prevent abuse with rate limiting:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.route('/api/servo', methods=['POST'])
@limiter.limit("10/second")
def servo_control():
    # ... servo control code
```

### Input Validation

Always validate servo positions:

```python
def validate_servo_position(position: int) -> bool:
    """Validate servo position is within safe range."""
    if not isinstance(position, int):
        return False
    if position < 0 or position > 180:
        return False
    return True

# Usage
position = request.json.get('position')
if not validate_servo_position(position):
    return jsonify({"error": "Position must be 0-180 degrees"}), 400
```

### Emergency Stop

Implement emergency stop for all agents:

```python
@app.route('/api/estop', methods=['POST'])
def emergency_stop():
    """Immediately disable all servos."""
    # Disable all servos via ARC
    requests.get("http://localhost:8080/set.html?var=$Genesis_EStop&val=1")
    return jsonify({"status": "E-STOP ACTIVATED"}), 200
```

---

## Example: Complete Multi-Agent Workflow

```python
from crewai import Agent, Task, Crew

# Define agents
navigator = Agent(
    role='Navigator',
    goal='Safely navigate robot to specified locations',
    tools=[servo_tool, camera_tool]
)

object_detector = Agent(
    role='Object Detector',
    goal='Identify and locate objects in camera feed',
    tools=[camera_tool]
)

manipulator = Agent(
    role='Manipulator',
    goal='Manipulate objects with robot arms',
    tools=[servo_tool]
)

# Define tasks
navigate_task = Task(
    description='Navigate to the table where the cup is located',
    agent=navigator,
    expected_output='Robot positioned at table'
)

detect_task = Task(
    description='Detect cup location and calculate grasp pose',
    agent=object_detector,
    expected_output='Cup coordinates and grasp pose'
)

grasp_task = Task(
    description='Execute grasp motion to pick up cup',
    agent=manipulator,
    expected_output='Cup successfully grasped'
)

# Create and run crew
crew = Crew(
    agents=[navigator, object_detector, manipulator],
    tasks=[navigate_task, detect_task, grasp_task],
    verbose=2
)

result = crew.kickoff()
print(f"Task completed: {result}")
```

---

## Troubleshooting

### Agent Cannot Connect to Robot

**Symptoms:** Timeout errors, connection refused

**Solutions:**
1. Verify backends are running: `curl http://localhost:5001/status`
2. Check ports: `netstat -tlnp | grep 5000`
3. Ensure WSL networking is configured correctly

### Servo Commands Not Executing

**Symptoms:** API returns success but robot doesn't move

**Solutions:**
1. Verify ARC is running and HTTP Server skill is active
2. Check servo ports match your robot configuration
3. Ensure servo backend is writing to correct directory

### Camera Feed Not Available

**Symptoms:** Camera status shows offline

**Solutions:**
1. Verify Live Stream Broadcast skill is running on port 8097
2. Test direct: `http://localhost:8097/live`
3. Check Camera Device skill is active in ARC

---

## Resources

- [Hermes Agent Documentation](https://github.com/hermes-agent/hermes)
- [LangChain Tools](https://python.langchain.com/docs/modules/agents/tools/)
- [AutoGen Documentation](https://microsoft.github.io/autogen/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [Genesis Mission Control Skill](SKILL.md)

---

**Last Updated:** June 30, 2026  
**Version:** 1.0.0
