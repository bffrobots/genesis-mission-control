#!/usr/bin/env python3
"""
Genesis Mission Control - Voice & Chat Server
AI-powered conversation with Ollama + Whisper STT + TTS

Runs on Windows OR WSL - auto-detects platform
Integrates with ARC (8080) and Servo Backend (5000)
WORKS WITHOUT OLLAMA - Falls back to rule-based commands
OPTIMIZED FOR TABLET - Longer timeouts, better error handling
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
    print("🪟 Running on Windows")
else:
    print("🐧 Running on WSL/Linux")

# ═══════════════════════════════════════════════════════════
# CONFIGURATION - Optimized for Tablet
# ═══════════════════════════════════════════════════════════

OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
GENESIS_PORT = int(os.environ.get('VOICE_CHAT_PORT', 5001))
GENESIS_HOST = os.environ.get('VOICE_CHAT_HOST', '0.0.0.0')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama3.1')
ROBOT_NAME = os.environ.get('ROBOT_NAME', 'Genesis')
ROBOT_ID = os.environ.get('ROBOT_ID', 'mini-bff-genesis')
ARC_HTTP_URL = os.environ.get('ARC_HTTP_URL', 'http://localhost:8080')
SERVO_BACKEND_URL = os.environ.get('SERVO_BACKEND_URL', 'http://localhost:5000')

# TIMEOUT SETTINGS - Increased for tablet performance
OLLAMA_TIMEOUT = int(os.environ.get('OLLAMA_TIMEOUT', '120'))  # 120 seconds (was 30)
OLLAMA_CONNECT_TIMEOUT = int(os.environ.get('OLLAMA_CONNECT_TIMEOUT', '10'))  # 10 seconds
REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', '30'))  # 30 seconds for other requests

print(f"⏱️  Ollama Timeout: {OLLAMA_TIMEOUT}s (connect: {OLLAMA_CONNECT_TIMEOUT}s)")
print(f"⏱️  Request Timeout: {REQUEST_TIMEOUT}s")

# Check if Ollama is available
OLLAMA_AVAILABLE = False
OLLAMA_MODEL_LOADED = None

try:
    print(f"🔍 Checking Ollama at {OLLAMA_URL}...")
    response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=OLLAMA_CONNECT_TIMEOUT)
    if response.status_code == 200:
        OLLAMA_AVAILABLE = True
        models = response.json().get('models', [])
        if models:
            OLLAMA_MODEL_LOADED = models[0].get('name', 'unknown')
            print(f"✅ Ollama detected: {OLLAMA_URL}")
            print(f"📦 Model loaded: {OLLAMA_MODEL_LOADED}")
        else:
            print(f"⚠️  Ollama running but no models installed")
            print(f"   Run: ollama pull llama3.1")
    else:
        print(f"⚠️  Ollama returned status {response.status_code}")
except requests.exceptions.ConnectionError:
    print(f"⚠️  Ollama not running at {OLLAMA_URL}")
    print(f"   Start Ollama or install from: https://ollama.com/download")
except Exception as e:
    print(f"⚠️  Ollama check failed: {e}")
    print(f"   Will run in RULE-BASED MODE")

if not OLLAMA_AVAILABLE:
    print(f"   Running in RULE-BASED MODE only")
    print(f"   Commands will work, but open conversation will not")

print(f"🤖 Robot: {ROBOT_NAME} ({ROBOT_ID})")
print(f"🔗 ARC HTTP URL: {ARC_HTTP_URL}")
print(f"🔗 Servo Backend URL: {SERVO_BACKEND_URL}")
print(f"🧠 Ollama: {'✅ Available (' + str(OLLAMA_MODEL_LOADED) + ')' if OLLAMA_AVAILABLE else '⚠️  Not available (rule-based mode)'}")

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
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        
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
        response = requests.post(url, json=data, timeout=REQUEST_TIMEOUT)
        
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
        action_name = action.get('action', '')
        return send_to_arc('$Genesis_Action', json.dumps(action))
    
    elif action_type == 'servo_move':
        servo_id = action.get('servo_id', 0)
        position = action.get('position', 90)
        return send_to_servo_backend(servo_id, position)
    
    elif action_type == 'navigate':
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
        """Process natural language command - rule-based (ALWAYS WORKS)"""
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
                'response': "I'm a robot. I can control servos, walk, wave, dance, etc.",
                'intent': 'question'
            }
        
        # Default: acknowledge but no action
        return {
            'action': None,
            'response': f"I heard: '{text}'. Try commands like 'stand', 'sit', 'wave', 'dance'.",
            'intent': 'conversation'
        }
    
    async def ollama_chat(self, message: str) -> str:
        """Get response from Ollama LLM (only if available) - OPTIMIZED FOR TABLET"""
        if not OLLAMA_AVAILABLE:
            return "Ollama not available. Using rule-based mode."
        
        try:
            print(f"🧠 Sending to Ollama: '{message[:50]}...'")
            start_time = time.time()
            
            response = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    'model': OLLAMA_MODEL,
                    'prompt': f"You are {ROBOT_NAME}, a friendly humanoid robot. Keep responses short (1-2 sentences). User said: {message}",
                    'stream': False,
                    'options': {
                        'temperature': 0.7,
                        'top_p': 0.9,
                        'num_predict': 100,  # Limit response length for speed
                    }
                },
                timeout=OLLAMA_TIMEOUT  # Use increased timeout
            )
            
            elapsed = time.time() - start_time
            print(f"✅ Ollama response in {elapsed:.1f}s")
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '...')
            else:
                return f"Ollama error: {response.status_code}"
                
        except requests.exceptions.Timeout:
            print(f"⏱️  Ollama timeout after {OLLAMA_TIMEOUT}s")
            return f"Response taking too long (>{OLLAMA_TIMEOUT}s). Try a simpler question or use rule-based commands."
        except requests.exceptions.ConnectionError:
            return "Ollama is not running. Start with: ollama serve"
        except Exception as e:
            print(f"❌ Ollama error: {e}")
            return f"Error: {str(e)}"
    
    async def process_message(self, message: str) -> ChatResponse:
        """Process message - rule-based ALWAYS works, LLM is optional"""
        # First try rule-based command parsing
        command_result = self.process_command(message)
        
        # If it's a robot command, execute immediately (WORKS WITHOUT OLLAMA)
        if command_result['action']:
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
        
        # For conversation, try LLM if available, otherwise use fallback
        if OLLAMA_AVAILABLE:
            llm_response = await self.ollama_chat(message)
        else:
            llm_response = command_result['response']  # Use rule-based fallback
        
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
        'ollama_available': OLLAMA_AVAILABLE,
        'ollama_model': OLLAMA_MODEL_LOADED,
        'timeouts': {
            'ollama': OLLAMA_TIMEOUT,
            'connect': OLLAMA_CONNECT_TIMEOUT,
            'request': REQUEST_TIMEOUT
        },
        'arc_url': ARC_HTTP_URL,
        'servo_backend_url': SERVO_BACKEND_URL
    }

@app.get('/status')
def get_status():
    """Health check endpoint"""
    # Check ARC connection
    arc_available = False
    try:
        response = requests.get(ARC_HTTP_URL, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            arc_available = True
    except:
        pass
    
    # Check servo backend connection
    servo_available = False
    try:
        response = requests.get(f"{SERVO_BACKEND_URL}/status", timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            servo_available = True
    except:
        pass
    
    return JSONResponse(content={
        'status': 'ok',
        'robot': ROBOT_ID,
        'robot_name': ROBOT_NAME,
        'ollama_available': OLLAMA_AVAILABLE,
        'ollama_model': OLLAMA_MODEL_LOADED,
        'connections': {
            'arc': {
                'available': arc_available,
                'url': ARC_HTTP_URL
            },
            'servo_backend': {
                'available': servo_available,
                'url': SERVO_BACKEND_URL
            }
        },
        'timeouts': {
            'ollama_seconds': OLLAMA_TIMEOUT,
            'request_seconds': REQUEST_TIMEOUT
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

@app.post('/test-connections')
def test_connections():
    """Test all connections (ARC, servo backend, Ollama)"""
    results = {}
    
    # Test ARC
    try:
        response = requests.get(ARC_HTTP_URL, timeout=REQUEST_TIMEOUT)
        results['arc'] = {'status': 'ok', 'code': response.status_code}
    except Exception as e:
        results['arc'] = {'status': 'error', 'message': str(e)}
    
    # Test servo backend
    try:
        response = requests.get(f"{SERVO_BACKEND_URL}/status", timeout=REQUEST_TIMEOUT)
        results['servo_backend'] = {'status': 'ok', 'code': response.status_code}
    except Exception as e:
        results['servo_backend'] = {'status': 'error', 'message': str(e)}
    
    # Test Ollama
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=OLLAMA_CONNECT_TIMEOUT)
        if response.status_code == 200:
            models = response.json().get('models', [])
            results['ollama'] = {
                'status': 'ok',
                'available': True,
                'models': [m['name'] for m in models],
                'timeout_seconds': OLLAMA_TIMEOUT
            }
        else:
            results['ollama'] = {'status': 'error', 'code': response.status_code}
    except requests.exceptions.Timeout:
        results['ollama'] = {'status': 'timeout', 'message': f'Connection timed out after {OLLAMA_CONNECT_TIMEOUT}s'}
    except Exception as e:
        results['ollama'] = {'status': 'error', 'message': str(e)}
    
    return results

# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

if __name__ == '__main__':
    print('=' * 60)
    print('🚀 Genesis Voice & Chat Server')
    print('Optimized for Tablet PC')
    print('=' * 60)
    print(f'Platform: {sys.platform}')
    print(f'Robot: {ROBOT_NAME} ({ROBOT_ID})')
    print(f'ARC HTTP: {ARC_HTTP_URL}')
    print(f'Servo Backend: {SERVO_BACKEND_URL}')
    print(f'Ollama Timeout: {OLLAMA_TIMEOUT}s (increased for tablet)')
    print(f'Ollama: {"✅ Available (' + str(OLLAMA_MODEL_LOADED) + ')" if OLLAMA_AVAILABLE else "⚠️  Not available (rule-based mode)"}')
    print()
    print('Starting server...')
    print(f'Listening on http://{GENESIS_HOST}:{GENESIS_PORT}')
    print()
    print('Commands that WORK without Ollama:')
    print('  - "stand", "sit", "wave", "dance", "bow"')
    print('  - "move servo X to Y degrees"')
    print('  - "navigate to kitchen"')
    print()
    print('With Ollama (full AI conversation):')
    print('  - Any question or conversation')
    print('  - Response time: 5-30 seconds (tablet)')
    print()
    print('Endpoints:')
    print(f'  GET  /              - Root endpoint')
    print(f'  GET  /status        - Health check')
    print(f'  POST /chat          - Chat with AI')
    print(f'  POST /command       - Send robot command')
    print(f'  WS   /ws/chat       - WebSocket chat')
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
