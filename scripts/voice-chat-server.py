#!/usr/bin/env python3
"""
Genesis Mission Control - Voice & Chat Server
AI-powered conversation with Ollama + Whisper STT + TTS

Runs on Windows OR WSL - auto-detects platform
Integrates with ARC (8080) and Servo Backend (5000)
"""

import os
import sys
import json
import time
import socket
import asyncio
import requests
from datetime import datetime
from typing import Dict, Any, Optional

# Auto-detect platform
if sys.platform == 'win32':
    # Windows
    print("🪟 Running on Windows")
    OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
else:
    # WSL/Linux
    print("🐧 Running on WSL/Linux")
    OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434')

try:
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("❌ Missing dependencies! Run: pip install -r requirements.txt")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

GENESIS_PORT = int(os.environ.get('VOICE_CHAT_PORT', 5001))
GENESIS_HOST = os.environ.get('VOICE_CHAT_HOST', '0.0.0.0')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama3.1')
ROBOT_NAME = os.environ.get('ROBOT_NAME', 'Genesis')
ROBOT_ID = os.environ.get('ROBOT_ID', 'mini-bff-genesis')

# Integration URLs
ARC_HTTP_URL = os.environ.get('ARC_HTTP_URL', 'http://localhost:8080')
SERVO_BACKEND_URL = os.environ.get('SERVO_BACKEND_URL', 'http://localhost:5000')

print(f"🤖 Robot: {ROBOT_NAME} ({ROBOT_ID})")
print(f"🧠 Ollama Model: {OLLAMA_MODEL}")
print(f"🌐 Ollama URL: {OLLAMA_URL}")
print(f"🔗 ARC HTTP URL: {ARC_HTTP_URL}")
print(f"🔗 Servo Backend URL: {SERVO_BACKEND_URL}")

# ═══════════════════════════════════════════════════════════
# FASTAPI APP
# ═══════════════════════════════════════════════════════════

app = FastAPI(title="Genesis Voice & Chat Server")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════

class ChatMessage(BaseModel):
    message: str
    from_user: bool = True

class ChatResponse(BaseModel):
    response: str
    intent: Optional[str] = None
    action: Optional[Dict[str, Any]] = None

# ═══════════════════════════════════════════════════════════
# INTEGRATION HELPERS
# ═══════════════════════════════════════════════════════════

def send_to_arc(variable_name: str, value: str) -> bool:
    """Send variable to ARC via HTTP Server"""
    try:
        url = f"{ARC_HTTP_URL}/set.html"
        params = {'var': variable_name, 'val': value}
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Sent to ARC: {variable_name} = {value}")
            return True
        else:
            print(f"❌ ARC error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ARC connection error: {e}")
        return False

def send_to_servo_backend(servo_id: int, position: int) -> bool:
    """Send servo command to backend"""
    try:
        url = f"{SERVO_BACKEND_URL}/api/servo"
        data = {'servo_id': servo_id, 'position': position}
        response = requests.post(url, json=data, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Servo D{servo_id} -> {position}°")
            return True
        else:
            print(f"❌ Servo backend error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Servo backend connection error: {e}")
        return False

def execute_action(action: Dict[str, Any]) -> bool:
    """Execute robot action via ARC or servo backend"""
    action_type = action.get('type', '')
    
    if action_type == 'execute_action':
        # Send to ARC via variable
        action_name = action.get('action', '')
        return send_to_arc('$Genesis_Action', json.dumps(action))
    
    elif action_type == 'servo_move':
        # Send to servo backend
        servo_id = action.get('servo_id', 0)
        position = action.get('position', 90)
        return send_to_servo_backend(servo_id, position)
    
    elif action_type == 'navigate':
        # Send navigation command to ARC
        return send_to_arc('$Genesis_Navigation', json.dumps(action))
    
    else:
        print(f"⚠️  Unknown action type: {action_type}")
        return False

# ═══════════════════════════════════════════════════════════
# GENESIS AI CORE
# ═══════════════════════════════════════════════════════════

class GenesisAI:
    """Genesis AI Brain - processes commands and conversations"""
    
    def __init__(self):
        self.conversation_history = []
        self.robot_actions = {
            'stand': {'type': 'execute_action', 'action': 'STAND'},
            'sit': {'type': 'execute_action', 'action': 'SIT'},
            'wave': {'type': 'execute_action', 'action': 'WAVE'},
            'dance': {'type': 'execute_action', 'action': 'DANCE'},
            'bow': {'type': 'execute_action', 'action': 'BOW'},
            'walk': {'type': 'execute_action', 'action': 'WALK'},
            'stop': {'type': 'execute_action', 'action': 'STOP'},
            'neutral': {'type': 'execute_action', 'action': 'NEUTRAL'},
        }
    
    def process_command(self, text: str) -> Dict[str, Any]:
        """Process natural language command - rule-based fallback"""
        text_lower = text.lower().strip()
        
        # Check for robot commands
        for cmd, action in self.robot_actions.items():
            if cmd in text_lower:
                return {
                    'action': action,
                    'response': f"Executing {cmd}...",
                    'intent': cmd
                }
        
        # Check for navigation
        if any(word in text_lower for word in ['go to', 'navigate', 'walk to', 'move to']):
            locations = ['kitchen', 'bedroom', 'living room', 'office', 'garage']
            for loc in locations:
                if loc in text_lower:
                    return {
                        'action': {'type': 'navigate', 'location': loc},
                        'response': f"Navigating to {loc}",
                        'intent': 'navigate'
                    }
        
        # Check for servo control
        if 'move' in text_lower and 'servo' in text_lower:
            # Extract servo ID and position from text
            # Example: "move servo 0 to 90 degrees"
            import re
            servo_match = re.search(r'servo\s*(\d+)', text_lower)
            pos_match = re.search(r'(\d+)\s*degrees?', text_lower)
            
            if servo_match and pos_match:
                servo_id = int(servo_match.group(1))
                position = int(pos_match.group(1))
                return {
                    'action': {'type': 'servo_move', 'servo_id': servo_id, 'position': position},
                    'response': f"Moving servo D{servo_id} to {position}°",
                    'intent': 'servo_control'
                }
        
        # Check for questions
        if any(word in text_lower for word in ['what', 'who', 'when', 'where', 'why', 'how']):
            return {
                'action': None,
                'response': "Let me think about that...",
                'intent': 'question'
            }
        
        # Default conversation
        return {
            'action': None,
            'response': "I heard you. How can I help?",
            'intent': 'conversation'
        }
    
    async def ollama_chat(self, message: str) -> str:
        """Get response from Ollama LLM"""
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    'model': OLLAMA_MODEL,
                    'prompt': f"You are {ROBOT_NAME}, a friendly humanoid robot. Keep responses short (1-2 sentences). User said: {message}",
                    'stream': False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '...')
            else:
                return f"Ollama error: {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return "Ollama is not running. Start with: ollama serve"
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def process_message(self, message: str) -> ChatResponse:
        """Process message - combines rule-based + LLM"""
        # First try rule-based command parsing
        command_result = self.process_command(message)
        
        # If it's a robot command, execute immediately
        if command_result['action']:
            # Execute the action
            action_executed = execute_action(command_result['action'])
            
            if action_executed:
                return ChatResponse(
                    response=command_result['response'],
                    intent=command_result['intent'],
                    action=command_result['action']
                )
            else:
                return ChatResponse(
                    response=f"Failed to execute {command_result['intent']}. Check connections.",
                    intent=command_result['intent'],
                    action=None
                )
        
        # Otherwise, use LLM for conversation
        llm_response = await self.ollama_chat(message)
        
        return ChatResponse(
            response=llm_response,
            intent='conversation',
            action=None
        )

# Initialize Genesis AI
genesis_ai = GenesisAI()

# ═══════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════

@app.get('/')
def root():
    """Root endpoint"""
    return {
        'service': 'Genesis Voice & Chat',
        'version': '1.0.0',
        'robot': ROBOT_NAME,
        'arc_url': ARC_HTTP_URL,
        'servo_backend_url': SERVO_BACKEND_URL
    }

@app.get('/status')
def get_status():
    """Health check endpoint"""
    # Check ARC connection
    arc_available = False
    try:
        response = requests.get(ARC_HTTP_URL, timeout=2)
        if response.status_code == 200:
            arc_available = True
    except:
        pass
    
    # Check servo backend connection
    servo_available = False
    try:
        response = requests.get(f"{SERVO_BACKEND_URL}/status", timeout=2)
        if response.status_code == 200:
            servo_available = True
    except:
        pass
    
    # Check Ollama
    ollama_available = False
    ollama_model = None
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            ollama_available = True
            models = response.json().get('models', [])
            ollama_model = next((m['name'] for m in models if OLLAMA_MODEL in m['name']), None)
    except:
        pass
    
    return JSONResponse(content={
        'status': 'ok',
        'robot': ROBOT_ID,
        'robot_name': ROBOT_NAME,
        'connections': {
            'arc': {
                'available': arc_available,
                'url': ARC_HTTP_URL
            },
            'servo_backend': {
                'available': servo_available,
                'url': SERVO_BACKEND_URL
            },
            'ollama': {
                'available': ollama_available,
                'url': OLLAMA_URL,
                'model': ollama_model
            }
        },
        'port': GENESIS_PORT,
        'timestamp': datetime.now().isoformat()
    })

@app.post('/chat', response_model=ChatResponse)
async def chat(message: ChatMessage):
    """
    Chat with Genesis AI
    
    Request:
    {
        "message": "Hello Genesis!"
    }
    
    Response:
    {
        "response": "Hello! How can I help you today?",
        "intent": "conversation",
        "action": null
    }
    """
    try:
        result = await genesis_ai.process_message(message.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/command')
async def send_command(message: ChatMessage):
    """Send command to robot via ARC"""
    try:
        result = await genesis_ai.process_message(message.message)
        
        if result.action:
            # Action already executed in process_message
            return {
                'success': result.action is not None,
                'response': result.response,
                'action': result.action
            }
        else:
            return {
                'success': False,
                'response': 'No action to execute',
                'action': None
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket('/ws/chat')
async def websocket_chat(websocket: WebSocket):
    """WebSocket chat endpoint for real-time conversation"""
    await websocket.accept()
    
    print(f"🔌 WebSocket connected")
    
    try:
        while True:
            data = await websocket.receive_text()
            
            # Process message
            result = await genesis_ai.process_message(data)
            
            # Send response
            await websocket.send_json({
                'response': result.response,
                'intent': result.intent,
                'action': result.action if result.action else None
            })
            
    except WebSocketDisconnect:
        print(f"🔌 WebSocket disconnected")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")

@app.get('/models')
def list_models():
    """List available Ollama models"""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return {'models': [m['name'] for m in models]}
        else:
            raise HTTPException(status_code=500, detail="Failed to fetch models")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/test-connections')
def test_connections():
    """Test all connections (ARC, servo backend, Ollama)"""
    results = {}
    
    # Test ARC
    try:
        response = requests.get(ARC_HTTP_URL, timeout=5)
        results['arc'] = {'status': 'ok', 'code': response.status_code}
    except Exception as e:
        results['arc'] = {'status': 'error', 'message': str(e)}
    
    # Test servo backend
    try:
        response = requests.get(f"{SERVO_BACKEND_URL}/status", timeout=5)
        results['servo_backend'] = {'status': 'ok', 'code': response.status_code}
    except Exception as e:
        results['servo_backend'] = {'status': 'error', 'message': str(e)}
    
    # Test Ollama
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        results['ollama'] = {'status': 'ok', 'code': response.status_code}
    except Exception as e:
        results['ollama'] = {'status': 'error', 'message': str(e)}
    
    return results

# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

if __name__ == '__main__':
    print('=' * 60)
    print('🚀 Genesis Voice & Chat Server')
    print('=' * 60)
    print(f'Platform: {sys.platform}')
    print(f'Robot: {ROBOT_NAME} ({ROBOT_ID})')
    print(f'Ollama: {OLLAMA_URL} ({OLLAMA_MODEL})')
    print(f'ARC HTTP: {ARC_HTTP_URL}')
    print(f'Servo Backend: {SERVO_BACKEND_URL}')
    print()
    print('Starting server...')
    print(f'Listening on http://{GENESIS_HOST}:{GENESIS_PORT}')
    print()
    print('Endpoints:')
    print(f'  GET  /              - Root endpoint')
    print(f'  GET  /status        - Health check (tests all connections)')
    print(f'  POST /chat          - Chat with AI')
    print(f'  POST /command       - Send robot command')
    print(f'  WS   /ws/chat       - WebSocket chat')
    print(f'  GET  /models        - List Ollama models')
    print(f'  POST /test-connections - Test all connections')
    print()
    print('Press Ctrl+C to stop')
    print('=' * 60)
    
    # Run FastAPI with uvicorn
    uvicorn.run(
        app,
        host=GENESIS_HOST,
        port=GENESIS_PORT,
        log_level='info'
    )
