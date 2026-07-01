#!/bin/bash
# Genesis Mission Control - Startup Script
# Runs on WSL/Linux for voice & chat server

set -e

echo "================================"
echo "Genesis Mission Control"
echo "Voice & Chat Server (WSL)"
echo "================================"
echo ""

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "❌ Ollama is not running!"
    echo "   Start Ollama: ollama serve"
    exit 1
fi

echo "✅ Ollama is running"

# Check if model exists
if ! ollama list | grep -q "llama3.1"; then
    echo "⚠️  llama3.1 model not found, pulling..."
    ollama pull llama3.1
fi

echo "✅ Model loaded"
echo ""
echo "Starting voice-chat-server.py..."
echo "Listening on: http://localhost:5001"
echo "Ollama: http://localhost:11434"
echo ""

# Start the server
cd "$(dirname "$0")/.."
python3 scripts/voice-chat-server.py
