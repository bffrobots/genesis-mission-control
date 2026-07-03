#!/usr/bin/env python3
"""
Genesis Mission Control - Voice & Chat Server
AI-powered conversation with Ollama + Whisper STT + TTS

Runs on Windows OR WSL - auto-detects platform
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

print(f"🤖 Robot: {ROBOT_NAME} ({ROBOT_ID})")
print(f"🧠 Ollama Model: {OLLAMA_MODEL}")
print(f"🌐 Ollama URL: {OLLAMA_URL}")

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
            return ChatResponse(
                response=command_result['response'],
                intent=command_result['intent'],
                action=command_result['action']
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
        'robot': ROBOT_NAME
    }

@app.get('/status')
def get_status():
    """Health check endpoint"""
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
        'ollama': {
            'available': ollama_available,
            'url': OLLAMA_URL,
            'model': ollama_model
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
            # Send to ARC via HTTP Server
            arc_url = "http://localhost:8080/set.html"
            params = {
                'var': '$Genesis_Command',
                'val': json.dumps(result.action)
            }
            
            try:
                requests.get(arc_url, params=params, timeout=5)
                print(f"✅ Command sent to ARC: {result.action}")
            except Exception as e:
                print(f"⚠️  Failed to send to ARC: {e}")
        
        return {
            'success': True,
            'response': result.response,
            'action': result.action
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
                'action': result.action.dict() if result.action else None
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
    print()
    print('Starting server...')
    print(f'Listening on http://{GENESIS_HOST}:{GENESIS_PORT}')
    print()
    print('Endpoints:')
    print(f'  GET  /              - Root endpoint')
    print(f'  GET  /status        - Health check')
    print(f'  POST /chat          - Chat with AI')
    print(f'  POST /command       - Send robot command')
    print(f'  WS   /ws/chat       - WebSocket chat')
    print(f'  GET  /models        - List Ollama models')
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
