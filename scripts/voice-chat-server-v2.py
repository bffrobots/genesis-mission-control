#!/usr/bin/env python3
"""
Genesis Voice & Chat Server v2.0 - Windows Edition
Fast Hybrid Architecture: Cloud AI + Rule-based fallback

Runs natively on Windows (no WSL required)
- Cloud AI (Anthropic/OpenAI) for conversations: 1-2 second responses
- Local rule-based parsing for commands: <100ms responses
- No Ollama dependency - removes the 10-20 second timeouts

Author: Genesis AI for BFF Robots
License: MIT
"""

import os
import sys
import json
import time
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

# FastAPI setup
try:
    from fastapi import FastAPI, WebSocket, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("   pip install fastapi uvicorn websockets anthropic openai")
    input("Press Enter to exit...")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    GENESIS_HOST = "0.0.0.0"
    GENESIS_PORT = 5001  # Avoid conflict with Windows backend on 5000
    
    # ARC Integration
    ARC_HTTP_HOST = "localhost"
    ARC_HTTP_PORT = 8080
    ARC_VARIABLE_PREFIX = "$Genesis_"
    
    # AI Services (Cloud - FAST)
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Prefer Anthropic Claude (faster, better for robotics)
    AI_PROVIDER = "anthropic" if ANTHROPIC_API_KEY else ("openai" if OPENAI_API_KEY else "none")
    
    # Robot identity
    ROBOT_NAME = "Genesis"
    ROBOT_MODEL = "Mini BFF Genesis (18 DOF)"

# ============================================================================
# AI SERVICE CLIENTS (Cloud - 1-2 second responses)
# ============================================================================

class CloudAIClient:
    """Unified interface for cloud AI providers"""
    
    def __init__(self):
        self.provider = Config.AI_PROVIDER
        self.client = None
        self._init_client()
        
    def _init_client(self):
        """Initialize the appropriate AI client"""
        if self.provider == "anthropic":
            try:
                from anthropic import AsyncAnthropic
                self.client = AsyncAnthropic(api_key=Config.ANTHROPIC_API_KEY)
                logger.info("✅ Anthropic Claude initialized (FAST - 1-2s responses)")
            except Exception as e:
                logger.error(f"❌ Anthropic init failed: {e}")
                self.provider = "none"
                
        elif self.provider == "openai":
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
                logger.info("✅ OpenAI GPT initialized (FAST - 1-2s responses)")
            except Exception as e:
                logger.error(f"❌ OpenAI init failed: {e}")
                self.provider = "none"
        else:
            logger.warning("⚠️  No AI provider configured - running in RULE-BASED MODE only")
            
    async def chat(self, message: str, context: list = None) -> str:
        """Get AI response from cloud provider"""
        if self.provider == "none" or not self.client:
            return None
            
        system_prompt = """You are Genesis, an AI controlling a 18 DOF humanoid robot (Mini BFF Genesis).
You are helpful, concise, and action-oriented. Keep responses under 2 sentences unless explaining something complex.
You can control the robot with commands like: stand, sit, wave, dance, bow, walk, stop.
Always prioritize safety - if something seems dangerous, warn the user.
Current time: """ + datetime.now().strftime("%I:%M %p")

        messages = [
            {"role": "system", "content": system_prompt},
            *(context or []),
            {"role": "user", "content": message}
        ]
        
        try:
            if self.provider == "anthropic":
                response = await self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=200,
                    messages=[{"role": m["role"], "content": m["content"]} for m in messages[1:]],
                    system=system_prompt
                )
                return response.content[0].text
                
            elif self.provider == "openai":
                response = await self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=200
                )
                return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"AI chat error: {e}")
            return None
            
        return None

# ============================================================================
# RULE-BASED COMMAND PARSER (Instant - <100ms)
# ============================================================================

class RuleBasedParser:
    """Fast rule-based command parsing - works without AI"""
    
    # Robot action commands
    COMMANDS = {
        'stand': {'action': 'STAND', 'response': 'Standing up'},
        'sit': {'action': 'SIT', 'response': 'Sitting down'},
        'wave': {'action': 'WAVE', 'response': 'Waving hello'},
        'dance': {'action': 'DANCE', 'response': 'Dancing!'},
        'bow': {'action': 'BOW', 'response': 'Bowing'},
        'stop': {'action': 'STOP', 'response': 'Stopping all motion'},
        'reset': {'action': 'RESET', 'response': 'Resetting to neutral position'},
        'walk': {'action': 'WALK_FORWARD', 'response': 'Walking forward'},
        'backward': {'action': 'WALK_BACKWARD', 'response': 'Walking backward'},
        'left': {'action': 'TURN_LEFT', 'response': 'Turning left'},
        'right': {'action': 'TURN_RIGHT', 'response': 'Turning right'},
    }
    
    # Servo control patterns
    SERVO_PATTERNS = [
        r'(?:move|set)\s*(?:servo|port)\s*([dD]?\d+)\s*(?:to)?\s*(\d+)\s*(?:degrees)?',
        r'(?:servo|port)\s*([dD]?\d+)\s*(?:to)?\s*(\d+)',
    ]
    
    def __init__(self):
        import re
        self.re = re
        
    def parse(self, text: str) -> Dict[str, Any]:
        """Parse text into command - returns immediately"""
        text_lower = text.lower().strip()
        
        # Check for known commands
        for cmd_key, cmd_data in self.COMMANDS.items():
            if cmd_key in text_lower:
                return {
                    'action': cmd_data['action'],
                    'response': cmd_data['response'],
                    'intent': 'command',
                    'confidence': 0.95
                }
        
        # Check for servo commands
        for pattern in self.SERVO_PATTERNS:
            match = self.re.search(pattern, text, self.re.IGNORECASE)
            if match:
                port = match.group(1)
                position = int(match.group(2))
                if not port.startswith('D'):
                    port = 'D' + port
                return {
                    'action': 'SERVO_MOVE',
                    'port': port.upper(),
                    'position': position,
                    'response': f'Moving {port.upper()} to {position}°',
                    'intent': 'servo_control',
                    'confidence': 0.90
                }
        
        # Check for questions about robot
        if any(word in text_lower for word in ['what can you do', 'what are you', 'who are you', 'your name']):
            return {
                'action': None,
                'response': f"I'm {Config.ROBOT_NAME}, a {Config.ROBOT_MODEL}. I can stand, sit, wave, dance, bow, walk, and control my 18 servos. Try saying 'stand up' or 'wave hello'!",
                'intent': 'question',
                'confidence': 0.85
            }
        
        # No command detected
        return {
            'action': None,
            'response': None,
            'intent': 'conversation',
            'confidence': 0.0
        }

# ============================================================================
# ARC INTEGRATION
# ============================================================================

class ARCIntegration:
    """Communicate with Synthiam ARC via HTTP Server Custom"""
    
    def __init__(self):
        self.base_url = f"http://{Config.ARC_HTTP_HOST}:{Config.ARC_HTTP_PORT}"
        self.available = False
        self._check_availability()
        
    def _check_availability(self):
        """Check if ARC HTTP server is reachable"""
        import requests
        try:
            resp = requests.get(f"{self.base_url}/get.html?var=$Genesis_Status", timeout=2)
            if resp.status_code == 200:
                self.available = True
                logger.info(f"✅ ARC HTTP Server detected at {self.base_url}")
            else:
                logger.warning(f"⚠️  ARC HTTP Server returned {resp.status_code}")
        except Exception as e:
            logger.warning(f"⚠️  ARC HTTP Server not reachable: {e}")
            logger.warning("   Robot commands will be logged but not executed")
            
    def set_variable(self, var_name: str, value: str):
        """Set ARC variable via HTTP Server Custom"""
        import requests
        try:
            if not var_name.startswith('$'):
                var_name = '$' + var_name
            resp = requests.get(
                f"{self.base_url}/set.html",
                params={'var': var_name, 'val': value},
                timeout=2
            )
            if resp.status_code == 200:
                logger.debug(f"Set {var_name} = {value}")
                return True
        except Exception as e:
            logger.error(f"Failed to set {var_name}: {e}")
        return False
        
    def execute_command(self, command: Dict[str, Any]):
        """Send command to ARC for execution"""
        if not self.available:
            logger.warning(f"Command queued (ARC offline): {command}")
            return False
            
        # Set command variable for ARC to process
        cmd_json = json.dumps(command)
        return self.set_variable(f"{Config.ARC_VARIABLE_PREFIX}Command", cmd_json)

# ============================================================================
# MAIN GENESIS SERVER
# ============================================================================

class GenesisVoiceChatServer:
    """Main server with hybrid AI + rule-based architecture"""
    
    def __init__(self):
        self.app = FastAPI(title="Genesis Voice & Chat Server v2.0")
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Initialize components
        self.ai = CloudAIClient()
        self.parser = RuleBasedParser()
        self.arc = ARCIntegration()
        
        # Conversation context (last 5 messages)
        self.context: Dict[str, list] = {}
        
        # WebSocket connections
        self.active_connections: list = []
        
        # Setup routes
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/")
        async def root():
            return {
                "service": "Genesis Voice & Chat Server v2.0",
                "status": "running",
                "ai_provider": Config.AI_PROVIDER,
                "arc_connected": self.arc.available,
                "robot": Config.ROBOT_NAME,
                "uptime": datetime.now().isoformat()
            }
            
        @self.app.get("/status")
        async def status():
            """Health check endpoint"""
            return {
                "status": "ok",
                "robot": Config.ROBOT_NAME,
                "robot_model": Config.ROBOT_MODEL,
                "ai": {
                    "provider": Config.AI_PROVIDER,
                    "available": Config.AI_PROVIDER != "none",
                    "mode": "cloud-fast" if Config.AI_PROVIDER != "none" else "rule-based"
                },
                "arc": {
                    "connected": self.arc.available,
                    "http_server": f"{self.arc.base_url}"
                },
                "active_connections": len(self.active_connections),
                "timestamp": datetime.now().isoformat()
            }
            
        @self.app.post("/chat")
        async def chat(message: ChatMessage):
            """
            Chat endpoint - HYBRID ARCHITECTURE
            1. Rule-based parser checks for commands (instant)
            2. If conversation, use cloud AI (1-2 seconds)
            3. If AI unavailable, use rule-based fallback
            """
            start_time = time.time()
            
            # Step 1: Parse with rules (instant)
            parsed = self.parser.parse(message.message)
            
            # If command detected, execute immediately
            if parsed['action']:
                self.arc.execute_command(parsed)
                elapsed = (time.time() - start_time) * 1000
                logger.info(f"⚡ Command executed in {elapsed:.0f}ms: {parsed['action']}")
                
                return ChatResponse(
                    response=parsed['response'],
                    action=parsed['action'],
                    intent=parsed['intent'],
                    latency_ms=round(elapsed, 1),
                    source="rule-based"
                )
            
            # Step 2: For conversation, try cloud AI
            if Config.AI_PROVIDER != "none":
                # Get context for this session
                session_context = self.context.get(message.session_id, [])
                
                # Call cloud AI (1-2 seconds)
                ai_response = await self.ai.chat(message.message, session_context)
                
                if ai_response:
                    # Update context
                    session_context.append({"role": "user", "content": message.message})
                    session_context.append({"role": "assistant", "content": ai_response})
                    self.context[message.session_id] = session_context[-10:]  # Keep last 5 pairs
                    
                    elapsed = (time.time() - start_time) * 1000
                    logger.info(f"🤖 AI response in {elapsed:.0f}ms: {ai_response[:50]}...")
                    
                    return ChatResponse(
                        response=ai_response,
                        action=None,
                        intent="conversation",
                        latency_ms=round(elapsed, 1),
                        source="cloud-ai"
                    )
            
            # Step 3: Fallback - no AI available
            elapsed = (time.time() - start_time) * 1000
            fallback_response = "I'm running in basic mode. I understand commands like 'stand', 'sit', 'wave', 'dance'. For conversation, configure an AI provider."
            
            logger.info(f"⚙️  Fallback response in {elapsed:.0f}ms")
            
            return ChatResponse(
                response=fallback_response,
                action=None,
                intent="conversation",
                latency_ms=round(elapsed, 1),
                source="fallback"
            )
            
        @self.app.websocket("/ws/chat")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket for real-time chat"""
            await websocket.accept()
            self.active_connections.append(websocket)
            logger.info(f"🔌 WebSocket connected ({len(self.active_connections)} active)")
            
            try:
                while True:
                    data = await websocket.receive_text()
                    message = ChatMessage(message=data, session_id="ws_default")
                    
                    # Process message
                    response = await chat(message)
                    
                    # Send response
                    await websocket.send_json({
                        "response": response.response,
                        "action": response.action,
                        "intent": response.intent,
                        "latency_ms": response.latency_ms,
                        "source": response.source
                    })
                    
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
            finally:
                self.active_connections.remove(websocket)
                logger.info(f"🔌 WebSocket disconnected ({len(self.active_connections)} active)")
                
        @self.app.get("/commands")
        async def list_commands():
            """List all supported robot commands"""
            return {
                "commands": list(self.parser.COMMANDS.keys()),
                "examples": [
                    "stand up",
                    "sit down",
                    "wave hello",
                    "do a dance",
                    "bow to the audience",
                    "stop moving",
                    "move servo D0 to 90 degrees"
                ]
            }
            
    async def run(self, host: str = Config.GENESIS_HOST, port: int = Config.GENESIS_PORT):
        """Start the server"""
        logger.info("=" * 70)
        logger.info("🚀 Genesis Voice & Chat Server v2.0 - FAST HYBRID ARCHITECTURE")
        logger.info("=" * 70)
        logger.info(f"🤖 Robot: {Config.ROBOT_NAME} ({Config.ROBOT_MODEL})")
        logger.info(f"🌐 AI Provider: {Config.AI_PROVIDER} (Cloud - 1-2s responses)")
        logger.info(f"⚡ Rule-based: Enabled (instant <100ms)")
        logger.info(f"🔗 ARC HTTP Server: {self.arc.base_url} ({'connected' if self.arc.available else 'offline'})")
        logger.info(f"📡 Listening on: http://{host}:{port}")
        logger.info("=" * 70)
        
        # Print startup banner
        if Config.AI_PROVIDER == "none":
            logger.warning("⚠️  Running in RULE-BASED MODE only")
            logger.warning("   Set ANTHROPIC_API_KEY or OPENAI_API_KEY for AI conversations")
        else:
            logger.info("✅ Cloud AI enabled - expect 1-2 second responses")
            
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level="info",
            access_log=False
        )
        server = uvicorn.Server(config)
        await server.serve()

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class ChatMessage(BaseModel):
    message: str
    session_id: str = "default"
    
class ChatResponse(BaseModel):
    response: str
    action: Optional[str] = None
    intent: str
    latency_ms: float
    source: str  # "rule-based", "cloud-ai", or "fallback"

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Create server instance
    server = GenesisVoiceChatServer()
    
    # Run server
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("\n👋 Server stopped by user")
    except Exception as e:
        logger.error(f"Server crashed: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
