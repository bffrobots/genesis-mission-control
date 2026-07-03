/**
 * Genesis Voice & Chat Integration
 * Connects web interface to Voice & Chat Server (port 5001)
 * 
 * Usage: Include in HTML after DOM load
 * <script src="voice-chat-integration.js"></script>
 */

// ═══════════════════════════════════════════════════════════
// CONFIGURATION
// ═══════════════════════════════════════════════════════════

var GENESIS_VOICE_CONFIG = {
  apiHost: "http://localhost:5001",  // Voice & Chat Server port
  wsHost: "ws://localhost:5001/ws/chat",
  arcHttpHost: "http://localhost:8080",  // ARC HTTP Server
  servoBackendHost: "http://localhost:5000",  // Servo Backend
  timeout: 10000,  // 10 second timeout
  debug: true
};

// ═══════════════════════════════════════════════════════════
// STATE
// ═══════════════════════════════════════════════════════════

var GenesisVoice = {
  ws: null,
  isConnected: false,
  isProcessing: false,
  conversationHistory: [],
  maxHistory: 20
};

// ═══════════════════════════════════════════════════════════
// LOGGING
// ═══════════════════════════════════════════════════════════

function log(message, type) {
  if (!GENESIS_VOICE_CONFIG.debug) return;
  
  type = type || 'info';
  var prefix = '[Voice & Chat]';
  var timestamp = new Date().toLocaleTimeString();
  
  if (type === 'error') {
    console.error(prefix + ' ❌ ' + message);
  } else if (type === 'success') {
    console.log(prefix + ' ✅ ' + message);
  } else if (type === 'warning') {
    console.warn(prefix + ' ⚠️  ' + message);
  } else {
    console.log(prefix + ' ' + message);
  }
}

// ═══════════════════════════════════════════════════════════
// WEBSOCKET CONNECTION
// ═══════════════════════════════════════════════════════════

function connectWebSocket() {
  if (GenesisVoice.ws && GenesisVoice.ws.readyState === WebSocket.OPEN) {
    log('WebSocket already connected');
    return;
  }
  
  try {
    GenesisVoice.ws = new WebSocket(GENESIS_VOICE_CONFIG.wsHost);
    
    GenesisVoice.ws.onopen = function() {
      GenesisVoice.isConnected = true;
      log('WebSocket connected to ' + GENESIS_VOICE_CONFIG.wsHost, 'success');
      updateConnectionStatus('connected');
    };
    
    GenesisVoice.ws.onmessage = function(event) {
      try {
        var data = JSON.parse(event.data);
        log('Received: ' + JSON.stringify(data));
        handleServerResponse(data);
      } catch (e) {
        log('Failed to parse response: ' + e.message, 'error');
      }
    };
    
    GenesisVoice.ws.onclose = function() {
      GenesisVoice.isConnected = false;
      log('WebSocket disconnected', 'warning');
      updateConnectionStatus('disconnected');
      
      // Auto-reconnect after 3 seconds
      setTimeout(connectWebSocket, 3000);
    };
    
    GenesisVoice.ws.onerror = function(error) {
      log('WebSocket error: ' + error, 'error');
      updateConnectionStatus('error');
    };
    
  } catch (e) {
    log('Failed to create WebSocket: ' + e.message, 'error');
  }
}

function sendWebSocketMessage(message) {
  if (!GenesisVoice.isConnected || !GenesisVoice.ws) {
    log('WebSocket not connected, using HTTP fallback', 'warning');
    return sendHttpMessage(message);
  }
  
  GenesisVoice.ws.send(JSON.stringify({
    message: message,
    from_user: true,
    timestamp: new Date().toISOString()
  }));
  
  return true;
}

// ═══════════════════════════════════════════════════════════
// HTTP FALLBACK
// ═══════════════════════════════════════════════════════════

function sendHttpMessage(message) {
  return fetch(GENESIS_VOICE_CONFIG.apiHost + '/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message: message,
      from_user: true
    })
  })
  .then(function(response) {
    if (!response.ok) {
      throw new Error('HTTP error: ' + response.status);
    }
    return response.json();
  })
  .then(function(data) {
    log('HTTP response: ' + JSON.stringify(data), 'success');
    handleServerResponse(data);
    return data;
  })
  .catch(function(error) {
    log('HTTP error: ' + error.message, 'error');
    showError('Failed to connect to Voice & Chat server');
    return null;
  });
}

// ═══════════════════════════════════════════════════════════
// RESPONSE HANDLING
// ═══════════════════════════════════════════════════════════

function handleServerResponse(data) {
  GenesisVoice.isProcessing = false;
  
  var response = data.response || '';
  var intent = data.intent || 'conversation';
  var action = data.action || null;
  
  log('Response: "' + response + '" (intent: ' + intent + ')');
  
  // Add to conversation history
  addToHistory('assistant', response);
  
  // Display in chat
  displayMessage('assistant', response);
  
  // If there's an action, execute it
  if (action) {
    log('Executing action: ' + JSON.stringify(action), 'success');
    executeRobotAction(action);
  }
  
  // Update UI
  hideProcessingIndicator();
  enableChatInput();
}

function executeRobotAction(action) {
  // Send to ARC via HTTP Server
  var variableName = '$Genesis_Command';
  var variableValue = JSON.stringify(action);
  
  var url = GENESIS_VOICE_CONFIG.arcHttpHost + '/set.html?var=' + 
            encodeURIComponent(variableName) + '&val=' + 
            encodeURIComponent(variableValue);
  
  // Use image beacon for no-CORS request
  var img = new Image();
  img.src = url;
  
  log('Sent to ARC: ' + variableName + ' = ' + variableValue, 'success');
  
  // Also try direct fetch (may fail due to CORS)
  fetch(url, { mode: 'no-cors' })
    .catch(function(e) {
      log('CORS expected, action still sent via image beacon', 'warning');
    });
}

// ═══════════════════════════════════════════════════════════
// CHAT UI FUNCTIONS
// ═══════════════════════════════════════════════════════════

function sendMessage() {
  var input = document.getElementById('chat-input');
  if (!input) return;
  
  var message = input.value.trim();
  if (!message) return;
  
  // Clear input
  input.value = '';
  
  // Add to history
  addToHistory('user', message);
  
  // Display user message
  displayMessage('user', message);
  
  // Show processing
  showProcessingIndicator();
  disableChatInput();
  
  // Send to server
  GenesisVoice.isProcessing = true;
  sendWebSocketMessage(message);
  
  // Timeout after 10 seconds
  setTimeout(function() {
    if (GenesisVoice.isProcessing) {
      log('Request timeout', 'error');
      hideProcessingIndicator();
      enableChatInput();
      showError('Request timeout - server not responding');
    }
  }, GENESIS_VOICE_CONFIG.timeout);
}

function displayMessage(role, text) {
  var container = document.getElementById('chat-messages');
  if (!container) return;
  
  var messageDiv = document.createElement('div');
  messageDiv.className = 'chat-msg chat-' + role;
  
  var avatar = document.createElement('div');
  avatar.className = 'chat-avatar chat-avatar-' + (role === 'user' ? 'user' : 'bot');
  avatar.textContent = role === 'user' ? '👤' : '🤖';
  
  var bubble = document.createElement('div');
  bubble.className = 'chat-bubble chat-bubble-' + role;
  bubble.innerHTML = '<p>' + escapeHtml(text) + '</p>' +
                     '<span class="chat-time">' + new Date().toLocaleTimeString() + '</span>';
  
  messageDiv.appendChild(avatar);
  messageDiv.appendChild(bubble);
  container.appendChild(messageDiv);
  
  // Scroll to bottom
  container.scrollTop = container.scrollHeight;
}

function showProcessingIndicator() {
  var container = document.getElementById('chat-messages');
  if (!container) return;
  
  var processingDiv = document.createElement('div');
  processingDiv.id = 'processing-indicator';
  processingDiv.className = 'chat-msg chat-assistant';
  processingDiv.innerHTML = '<div class="chat-avatar chat-avatar-bot">🤖</div>' +
                            '<div class="chat-bubble chat-bubble-bot">' +
                            '<p>Processing...</p>' +
                            '<div class="typing-indicator">' +
                            '<span></span><span></span><span></span>' +
                            '</div></div>';
  
  container.appendChild(processingDiv);
  container.scrollTop = container.scrollHeight;
}

function hideProcessingIndicator() {
  var indicator = document.getElementById('processing-indicator');
  if (indicator) {
    indicator.remove();
  }
}

function addToHistory(role, text) {
  GenesisVoice.conversationHistory.push({
    role: role,
    text: text,
    timestamp: new Date().toISOString()
  });
  
  // Limit history size
  if (GenesisVoice.conversationHistory.length > GenesisVoice.maxHistory) {
    GenesisVoice.conversationHistory.shift();
  }
}

function updateConnectionStatus(status) {
  var indicator = document.getElementById('connection-status');
  if (!indicator) return;
  
  if (status === 'connected') {
    indicator.className = 'status-dot dot-ok';
    indicator.title = 'Connected';
  } else if (status === 'error') {
    indicator.className = 'status-dot dot-err';
    indicator.title = 'Connection error';
  } else {
    indicator.className = 'status-dot dot-warn';
    indicator.title = 'Disconnected';
  }
}

function disableChatInput() {
  var input = document.getElementById('chat-input');
  var button = document.getElementById('btn-send');
  if (input) input.disabled = true;
  if (button) button.disabled = true;
}

function enableChatInput() {
  var input = document.getElementById('chat-input');
  var button = document.getElementById('btn-send');
  if (input) input.disabled = false;
  if (button) button.disabled = false;
  if (input) input.focus();
}

function showError(message) {
  var container = document.getElementById('chat-messages');
  if (!container) return;
  
  var errorDiv = document.createElement('div');
  errorDiv.className = 'chat-msg chat-system';
  errorDiv.innerHTML = '<div class="chat-avatar chat-avatar-system">⚠️</div>' +
                       '<div class="chat-bubble chat-bubble-system">' +
                       '<p>' + escapeHtml(message) + '</p></div>';
  
  container.appendChild(errorDiv);
  container.scrollTop = container.scrollHeight;
}

function escapeHtml(text) {
  var div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// ═══════════════════════════════════════════════════════════
// QUICK COMMANDS
// ═══════════════════════════════════════════════════════════

function sendQuickCommand(command) {
  var input = document.getElementById('chat-input');
  if (input) {
    input.value = command;
  }
  sendMessage();
}

// ═══════════════════════════════════════════════════════════
// STATUS CHECK
// ═══════════════════════════════════════════════════════════

function checkServerStatus() {
  return fetch(GENESIS_VOICE_CONFIG.apiHost + '/status', {
    method: 'GET',
    timeout: 5000
  })
  .then(function(response) {
    if (!response.ok) {
      throw new Error('Server returned ' + response.status);
    }
    return response.json();
  })
  .then(function(data) {
    log('Server status: ' + JSON.stringify(data), 'success');
    return data;
  })
  .catch(function(error) {
    log('Status check failed: ' + error.message, 'error');
    return null;
  });
}

// ═══════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════

function initializeGenesisVoice() {
  log('Initializing Genesis Voice & Chat...');
  log('API Host: ' + GENESIS_VOICE_CONFIG.apiHost);
  log('WebSocket: ' + GENESIS_VOICE_CONFIG.wsHost);
  log('ARC HTTP: ' + GENESIS_VOICE_CONFIG.arcHttpHost);
  log('Servo Backend: ' + GENESIS_VOICE_CONFIG.servoBackendHost);
  
  // Connect WebSocket
  connectWebSocket();
  
  // Setup send button
  var sendButton = document.getElementById('btn-send');
  if (sendButton) {
    sendButton.addEventListener('click', sendMessage);
  }
  
  // Setup enter key
  var chatInput = document.getElementById('chat-input');
  if (chatInput) {
    chatInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  }
  
  // Setup quick commands
  var quickCommands = document.querySelectorAll('.quick-cmd');
  quickCommands.forEach(function(cmd) {
    cmd.addEventListener('click', function() {
      sendQuickCommand(this.dataset.command || this.textContent);
    });
  });
  
  // Check server status on load
  setTimeout(function() {
    checkServerStatus().then(function(status) {
      if (status) {
        log('Server is running', 'success');
      } else {
        log('Server not responding - check if start_voice_chat.bat is running', 'error');
      }
    });
  }, 1000);
  
  log('Initialization complete', 'success');
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeGenesisVoice);
} else {
  initializeGenesisVoice();
}

// Export for external use
if (typeof window !== 'undefined') {
  window.GenesisVoice = GenesisVoice;
  window.sendQuickCommand = sendQuickCommand;
  window.checkServerStatus = checkServerStatus;
}
