/**
 * Genesis Voice & Chat Integration v2.0
 * Fast Hybrid Architecture - Cloud AI + Rule-based fallback
 * 
 * Updated for voice-chat-server-v2.py with:
 * - Port 5001 (avoid conflict with Windows backend on 5000)
 * - Latency tracking for performance monitoring
 * - Clear status indicators for AI availability
 */

// ============================================================================
// CONFIGURATION
// ============================================================================

var GENESIS_VOICE_CONFIG = {
  apiHost: "http://localhost:5001",  // Port 5001 - WSL voice-chat server
  wsHost: "ws://localhost:5001/ws/chat",
  timeout: 5000,  // 5 second timeout (cloud AI responds in 1-2s)
  robotName: "Genesis",
  debug: true
};

// ============================================================================
// GLOBAL STATE
// ============================================================================

var genesisVoiceState = {
  connected: false,
  aiProvider: 'none',
  arcConnected: false,
  websocket: null,
  lastLatency: 0,
  messageCount: 0
};

// ============================================================================
// INITIALIZATION
// ============================================================================

function initializeGenesisVoice() {
  console.log('[Voice & Chat v2.0] Initializing...');
  
  // Check server status
  checkGenesisStatus();
  
  // Setup WebSocket for real-time chat
  setupWebSocket();
  
  // Setup UI event listeners
  setupEventListeners();
  
  console.log('[Voice & Chat v2.0] Initialization complete');
}

function checkGenesisStatus() {
  fetch(GENESIS_VOICE_CONFIG.apiHost + '/status')
    .then(function(response) {
      return response.json();
    })
    .then(function(status) {
      genesisVoiceState.connected = true;
      genesisVoiceState.aiProvider = status.ai ? status.ai.provider : 'none';
      genesisVoiceState.arcConnected = status.arc ? status.arc.connected : false;
      
      // Update UI
      updateConnectionStatus('connected', status.ai.mode);
      
      console.log('[Voice & Chat v2.0] Status:', status);
    })
    .catch(function(error) {
      genesisVoiceState.connected = false;
      updateConnectionStatus('disconnected', 'offline');
      console.error('[Voice & Chat v2.0] Server offline:', error);
    });
}

function setupWebSocket() {
  if (!window.WebSocket) {
    console.warn('[Voice & Chat v2.0] WebSocket not supported - using HTTP polling');
    return;
  }
  
  try {
    genesisVoiceState.websocket = new WebSocket(GENESIS_VOICE_CONFIG.wsHost);
    
    genesisVoiceState.websocket.onopen = function() {
      console.log('[Voice & Chat v2.0] WebSocket connected');
      genesisVoiceState.connected = true;
    };
    
    genesisVoiceState.websocket.onmessage = function(event) {
      var data = JSON.parse(event.data);
      handleChatResponse(data);
    };
    
    genesisVoiceState.websocket.onclose = function() {
      console.log('[Voice & Chat v2.0] WebSocket disconnected');
      genesisVoiceState.connected = false;
      // Reconnect after 3 seconds
      setTimeout(setupWebSocket, 3000);
    };
    
    genesisVoiceState.websocket.onerror = function(error) {
      console.error('[Voice & Chat v2.0] WebSocket error:', error);
    };
    
  } catch (error) {
    console.error('[Voice & Chat v2.0] WebSocket setup failed:', error);
  }
}

function setupEventListeners() {
  // Chat input form
  var chatForm = document.getElementById('genesis-chat-form');
  if (chatForm) {
    chatForm.addEventListener('submit', function(e) {
      e.preventDefault();
      var input = document.getElementById('genesis-chat-input');
      if (input && input.value.trim()) {
        sendChatMessage(input.value.trim());
        input.value = '';
      }
    });
  }
  
  // Voice input button (if using Web Speech API)
  var voiceBtn = document.getElementById('genesis-voice-btn');
  if (voiceBtn) {
    voiceBtn.addEventListener('click', startVoiceInput);
  }
}

// ============================================================================
// CHAT FUNCTIONS
// ============================================================================

function sendChatMessage(message) {
  var startTime = Date.now();
  
  // Add user message to chat UI
  addChatMessage(message, 'user');
  
  // Show typing indicator
  showTypingIndicator();
  
  // Send via WebSocket if available, otherwise HTTP
  if (genesisVoiceState.connected && genesisVoiceState.websocket && 
      genesisVoiceState.websocket.readyState === WebSocket.OPEN) {
    genesisVoiceState.websocket.send(message);
  } else {
    // Fallback to HTTP POST
    fetch(GENESIS_VOICE_CONFIG.apiHost + '/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        message: message,
        session_id: getOrCreateSessionId()
      }),
      timeout: GENESIS_VOICE_CONFIG.timeout
    })
    .then(function(response) {
      return response.json();
    })
    .then(function(data) {
      handleChatResponse(data, startTime);
    })
    .catch(function(error) {
      hideTypingIndicator();
      addChatMessage('Error: Server not responding. Check connection.', 'error');
      console.error('[Voice & Chat v2.0] HTTP error:', error);
    });
  }
}

function handleChatResponse(data, startTime) {
  hideTypingIndicator();
  
  var latency = data.latency_ms || (Date.now() - startTime);
  genesisVoiceState.lastLatency = latency;
  genesisVoiceState.messageCount++;
  
  // Add response to chat UI
  addChatMessage(data.response, 'assistant', {
    latency: latency,
    source: data.source,
    action: data.action
  });
  
  // Log performance
  console.log('[Voice & Chat v2.0] Response:', data.response.substring(0, 50) + '...', 
              '| Latency:', latency + 'ms', '| Source:', data.source);
  
  // Execute action if present
  if (data.action) {
    console.log('[Voice & Chat v2.0] Action detected:', data.action);
    // Action is already executed by backend via ARC
  }
  
  // Update latency display
  updateLatencyDisplay(latency, data.source);
}

// ============================================================================
// UI FUNCTIONS
// ============================================================================

function addChatMessage(text, type, metadata) {
  var chatContainer = document.getElementById('genesis-chat-messages');
  if (!chatContainer) {
    console.warn('[Voice & Chat v2.0] Chat container not found');
    return;
  }
  
  var messageDiv = document.createElement('div');
  messageDiv.className = 'chat-message ' + type;
  
  var contentHtml = '<div class="message-text">' + escapeHtml(text) + '</div>';
  
  // Add metadata for assistant messages
  if (type === 'assistant' && metadata) {
    var sourceIcon = getSourceIcon(metadata.source);
    contentHtml += '<div class="message-meta">' + 
                   sourceIcon + ' ' + metadata.latency + 'ms' +
                   (metadata.action ? ' • Action: ' + metadata.action : '') +
                   '</div>';
  }
  
  messageDiv.innerHTML = contentHtml;
  chatContainer.appendChild(messageDiv);
  
  // Auto-scroll to bottom
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showTypingIndicator() {
  var chatContainer = document.getElementById('genesis-chat-messages');
  if (!chatContainer) return;
  
  var typingDiv = document.createElement('div');
  typingDiv.id = 'genesis-typing-indicator';
  typingDiv.className = 'chat-message typing';
  typingDiv.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
  chatContainer.appendChild(typingDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

function hideTypingIndicator() {
  var typingIndicator = document.getElementById('genesis-typing-indicator');
  if (typingIndicator) {
    typingIndicator.remove();
  }
}

function updateConnectionStatus(status, mode) {
  var statusEl = document.getElementById('genesis-connection-status');
  if (!statusEl) return;
  
  if (status === 'connected') {
    statusEl.className = 'connection-status connected';
    statusEl.innerHTML = '✓ Connected ' + 
                         (mode === 'cloud-fast' ? '(Cloud AI)' : '(Rule-based)');
  } else {
    statusEl.className = 'connection-status disconnected';
    statusEl.innerHTML = '✗ Disconnected';
  }
}

function updateLatencyDisplay(latency, source) {
  var latencyEl = document.getElementById('genesis-latency-display');
  if (!latencyEl) return;
  
  var latencyClass = latency < 1000 ? 'fast' : (latency < 3000 ? 'medium' : 'slow');
  var sourceLabel = source === 'cloud-ai' ? 'AI' : (source === 'rule-based' ? 'Command' : 'Fallback');
  
  latencyEl.className = 'latency-display ' + latencyClass;
  latencyEl.innerHTML = sourceLabel + ': ' + latency + 'ms';
}

function getSourceIcon(source) {
  var icons = {
    'cloud-ai': '🤖',
    'rule-based': '⚡',
    'fallback': '⚙️'
  };
  return icons[source] || '•';
}

function escapeHtml(text) {
  var div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function getOrCreateSessionId() {
  var sessionId = sessionStorage.getItem('genesis_session_id');
  if (!sessionId) {
    sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    sessionStorage.setItem('genesis_session_id', sessionId);
  }
  return sessionId;
}

// ============================================================================
// VOICE INPUT (Web Speech API)
// ============================================================================

function startVoiceInput() {
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    alert('Voice input not supported in this browser. Use Chrome or Edge.');
    return;
  }
  
  var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  var recognition = new SpeechRecognition();
  
  recognition.lang = 'en-US';
  recognition.continuous = false;
  recognition.interimResults = false;
  
  recognition.onstart = function() {
    console.log('[Voice & Chat v2.0] Listening...');
    var voiceBtn = document.getElementById('genesis-voice-btn');
    if (voiceBtn) voiceBtn.classList.add('listening');
  };
  
  recognition.onresult = function(event) {
    var transcript = event.results[0][0].transcript;
    console.log('[Voice & Chat v2.0] Recognized:', transcript);
    sendChatMessage(transcript);
  };
  
  recognition.onerror = function(event) {
    console.error('[Voice & Chat v2.0] Speech recognition error:', event.error);
    alert('Voice input error: ' + event.error);
  };
  
  recognition.onend = function() {
    var voiceBtn = document.getElementById('genesis-voice-btn');
    if (voiceBtn) voiceBtn.classList.remove('listening');
  };
  
  recognition.start();
}

// ============================================================================
// QUICK COMMAND BUTTONS
// ============================================================================

function sendQuickCommand(command) {
  var commands = {
    'stand': 'stand up',
    'sit': 'sit down',
    'wave': 'wave hello',
    'dance': 'do a dance',
    'bow': 'bow to the audience',
    'stop': 'stop moving',
    'reset': 'reset to neutral'
  };
  
  var message = commands[command] || command;
  sendChatMessage(message);
}

// ============================================================================
// AUTO-INITIALIZE
// ============================================================================

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeGenesisVoice);
} else {
  initializeGenesisVoice();
}

// Export for global access
window.genesisVoice = {
  send: sendChatMessage,
  quickCommand: sendQuickCommand,
  state: genesisVoiceState,
  config: GENESIS_VOICE_CONFIG
};

console.log('[Voice & Chat v2.0] Module loaded - call initializeGenesisVoice() to start');
