#!/bin/bash
# Genesis Mission Control - Diagnostic Script

echo "================================"
echo "Genesis Mission Control"
echo "System Diagnostic"
echo "================================"
echo ""

check_service() {
    local name=$1
    local url=$2
    echo -n "Checking $name... "
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200"; then
        echo "✅ OK"
        return 0
    else
        echo "❌ FAILED"
        return 1
    fi
}

check_service "HTTP Server (8080)" "http://localhost:8080"
check_service "Camera Stream (8097)" "http://localhost:8097/live"
check_service "Servo Backend (5000)" "http://localhost:5000/status"
check_service "Voice Chat (5001)" "http://localhost:5001/status"
check_service "Ollama (11434)" "http://localhost:11434/api/tags"

echo ""
echo "================================"
echo "Diagnostic Complete"
echo "================================"
