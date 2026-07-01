#!/usr/bin/env python3
"""
Genesis Mission Control - Python Backend (On Variable Changed)
Mini BFF Genesis Humanoid Robot (18 DOF)

Author: Genesis AI for Roberto Cardenas @ BFF Robots
Version: 1.2.0 - On Variable Changed integration
Date: April 25, 2026

Communication: Backend writes variable files → On Variable Changed triggers → Servos move
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

GENESIS_PORT = 5000
GENESIS_HOST = "0.0.0.0"
ROBOT_ID = "mini-bff-genesis-001"

# Variable files directory (ARC HTTP Server Root)
VARIABLES_DIR = Path(r"C:\Users\Perseus\Documents\ARC\HTTP Server Root")
VARIABLES_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# DATA MODELS
# ============================================================================

class ChatMessage(BaseModel):
    text: str
    from_user: bool = True

class RobotCommand(BaseModel):
    type: str
    data: Dict[str, Any] = {}

class ActionCommand(BaseModel):
    action: str

# ============================================================================
# GENESIS AI CORE
# ============================================================================

class GenesisAI:
    """Genesis AI Brain - processes commands"""
    
    def __init__(self):
        self.conversation_history = []
        
    async def process_command(self, text: str) -> Dict[str, Any]:
        """Process natural language command"""
        text_lower = text.lower().strip()
        
        if any(word in text_lower for word in ["stand", "stand up"]):
            return {"action": {"type": "execute_action", "action": "STAND"}, "response": "Standing up now"}
        elif "sit" in text_lower or "sit down" in text_lower:
            return {"action": {"type": "execute_action", "action": "SIT"}, "response": "Sitting down"}
        elif "wave" in text_lower:
            return {"action": {"type": "execute_action", "action": "WAVE"}, "response": "Waving hello!"}
        elif "dance" in text_lower:
            return {"action": {"type": "execute_action", "action": "DANCE"}, "response": "Let's dance!"}
        elif "bow" in text_lower:
            return {"action": {"type": "execute_action", "action": "BOW"}, "response": "Bowing"}
        elif "reset" in text_lower or "neutral" in text_lower:
            return {"action": {"type": "execute_action", "action": "NEUTRAL"}, "response": "Resetting to neutral"}
        elif "status" in text_lower or "how are you" in text_lower:
            return {"action": None, "response": "All systems operational. Ready for commands."}
        elif "help" in text_lower:
            return {"action": None, "response": "I can: stand, sit, wave, dance, bow, reset, or answer questions."}
        elif "hello" in text_lower or "hi" in text_lower:
            return {"action": None, "response": "Hello! I'm Genesis, your Mini BFF humanoid robot assistant."}
        else:
            return {"action": None, "response": f"I heard: '{text}'. Try: 'stand', 'sit', 'wave', 'dance', 'bow', 'reset', or 'help'"}

# ============================================================================
# VARIABLE FILE WRITER
# ============================================================================

def set_variable(var_name: str, value: str):
    """Write variable to plain text file - no HTML wrapper"""
    try:
        # Remove $ from filename for HTTP compatibility
        # $Servo_D0 → Servo_D0.txt (use .txt for plain text)
        safe_name = var_name.replace("$", "")
        var_file = VARIABLES_DIR / f"{safe_name}.txt"
        var_file.write_text(str(value))
        logger.info(f"Set {var_name} = {value} (file: {safe_name}.txt)")
        return True
    except Exception as e:
        logger.error(f"Failed to set variable {var_name}: {e}")
        return False

def write_servo_command(port: str, position: int, speed: int = 50):
    """Set $Servo_D# variable - On Variable Changed will move the servo"""
    var_name = f"$Servo_{port}"  # $Servo_D0, $Servo_D1, etc. (with $ prefix!)
    success = set_variable(var_name, str(position))
    if success:
        logger.info(f"🤖 Servo {port} @ {position}° (variable: {var_name})")
    return success

def write_action_command(action_name: str):
    """Set action variable"""
    success = set_variable("Genesis_Action", action_name)
    if success:
        logger.info(f"🎭 Action: {action_name}")
    return success

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

def create_app() -> FastAPI:
    """Create FastAPI application"""
    
    app = FastAPI(
        title="Genesis Mission Control API",
        description="AI Backend for Mini BFF Genesis (On Variable Changed)",
        version="1.2.0"
    )
    
    # Enable CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    genesis_ai = GenesisAI()
    
    robot_state = {
        "connected": True,
        "arc_available": True,
        "battery": 12.6,
        "temperature": 35.0,
    }
    
    @app.on_event("startup")
    async def startup_event():
        logger.info("================================")
        logger.info("Genesis Mission Control")
        logger.info("Python Backend v1.2.0")
        logger.info("(On Variable Changed)")
        logger.info("================================")
        logger.info(f"Starting server on port {GENESIS_PORT}")
        logger.info(f"Variables Directory: {VARIABLES_DIR}")
        logger.info("")
        logger.info("API Endpoints:")
        logger.info(f"  GET  http://localhost:{GENESIS_PORT}/api/status")
        logger.info(f"  POST http://localhost:{GENESIS_PORT}/api/command")
        logger.info(f"  POST http://localhost:{GENESIS_PORT}/api/servo")
        logger.info(f"  POST http://localhost:{GENESIS_PORT}/api/action")
        logger.info(f"  POST http://localhost:{GENESIS_PORT}/api/chat")
        logger.info("")
        logger.info("Ready to control Mini BFF Genesis! 🤖")
        logger.info("")
    
    @app.get("/")
    async def root():
        return {
            "status": "ok",
            "service": "Genesis AI Backend",
            "version": "1.2.0",
            "control_method": "on-variable-changed"
        }
    
    @app.get("/api/status")
    async def get_status():
        return {
            "connected": robot_state["connected"],
            "arc_available": robot_state["arc_available"],
            "battery": robot_state["battery"],
            "genesis_status": "Online",
            "timestamp": datetime.now().isoformat(),
            "robot_id": ROBOT_ID,
            "variables_dir": str(VARIABLES_DIR)
        }
    
    @app.post("/api/command")
    async def receive_command(command: RobotCommand):
        logger.info(f"Command received: {command.type}")
        
        if command.type == "voice_command":
            text = command.data.get("text", "")
            result = await genesis_ai.process_command(text)
            
            if result.get("action") and result["action"].get("type") == "execute_action":
                action_name = result["action"]["action"]
                write_action_command(action_name)
            
            return {"response": result["response"]}
        
        elif command.type == "move_servo":
            port = command.data.get("port", "D0")
            position = command.data.get("position", 90)
            speed = command.data.get("speed", 50)
            
            success = write_servo_command(port, position, speed)
            
            return {
                "status": "sent" if success else "failed",
                "port": port,
                "position": position,
                "simulated": False
            }
        
        elif command.type == "speak":
            text = command.data.get("text", "")
            logger.info(f"🔊 Speech: {text}")
            return {"status": "logged", "text": text}
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown command type: {command.type}")
    
    @app.post("/api/servo")
    async def move_servo_direct(request: dict):
        """Direct servo control endpoint - writes to Servo_D{port}.txt file"""
        try:
            servo_id = request.get('servo_id', 0)
            position = request.get('position', 90)
            port = request.get('port', f'D{servo_id}')
            
            success = write_servo_command(port, position)
            
            return {
                "status": "sent" if success else "failed",
                "servo_id": servo_id,
                "port": port,
                "position": position,
                "file": f"Servo_{port}.txt"
            }
        except Exception as e:
            logger.error(f"Servo command error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/action")
    async def execute_action(cmd: ActionCommand):
        success = write_action_command(cmd.action)
        return {"status": "sent" if success else "failed", "action": cmd.action}
    
    @app.post("/api/chat")
    async def chat(message: ChatMessage):
        result = await genesis_ai.process_command(message.text)
        
        genesis_ai.conversation_history.append({
            "from": "user",
            "text": message.text,
            "timestamp": datetime.now().isoformat()
        })
        genesis_ai.conversation_history.append({
            "from": "genesis",
            "text": result["response"],
            "timestamp": datetime.now().isoformat()
        })
        
        return {"response": result["response"]}
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        logger.info("WebSocket client connected")
        
        try:
            while True:
                await websocket.send_json({"type": "state_update", "data": robot_state})
                await asyncio.sleep(1)
        except WebSocketDisconnect:
            logger.info("WebSocket client disconnected")
    
    return app

# ============================================================================
# MAIN
# ============================================================================

async def main():
    config = uvicorn.Config(create_app(), host=GENESIS_HOST, port=GENESIS_PORT, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nGenesis Backend shutting down...")
