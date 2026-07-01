# Troubleshooting Guide

## Common Issues and Solutions

### Camera Feed Not Showing

**Symptoms:** Black screen or "loading" forever in Camera & Vision tab

**Solutions:**
1. **Verify Live Stream Broadcast is running:**
   ```bash
   # Test direct stream
   curl -I http://localhost:8097/live
   # Should return: HTTP/1.1 200 OK
   ```

2. **Check ARC skills:**
   - Open ARC
   - Verify "Live Stream Broadcast" skill shows "Running" (green)
   - Verify "Camera Device" skill is active

3. **Test in browser:**
   ```
   Direct: http://localhost:8097/live
   Web UI: http://localhost:8080 → Camera & Vision tab
   ```

4. **Check browser console:**
   - Press F12 → Console tab
   - Look for errors related to iframe or connection

5. **Restart Live Stream Broadcast:**
   - In ARC, disable then re-enable the skill
   - Wait 5 seconds for stream to initialize

### Servo Control Not Working

**Symptoms:** Web interface sliders move but robot doesn't respond

**Solutions:**
1. **Verify backend is running:**
   ```bash
   # Windows (PowerShell)
   curl http://localhost:5000/status
   
   # Should return: {"status": "ok"}
   ```

2. **Check ARC HTTP Server:**
   - Verify HTTP Server Custom skill is running on port 8080
   - Test: `curl http://localhost:8080`

3. **Verify servo files are written:**
   ```bash
   ls -la "/mnt/c/Users/Perseus/Documents/ARC/HTTP Server Root/Servo_D*.txt"
   # Should show files with recent timestamps
   ```

4. **Test in ARC directly:**
   - Open ARC Script Console
   - Run: `controlCommand("Auto Position", "AutoPositionFrame", "STAND")`
   - Robot should execute STAND pose

5. **Check servo backend logs:**
   ```bash
   # Look for error messages in backend output
   python servo-backend.py
   ```

### Voice Chat Not Responding

**Symptoms:** Chat sends but no response from Genesis AI

**Solutions:**
1. **Verify Ollama is running:**
   ```bash
   curl http://localhost:11434/api/tags
   # Should return list of models
   ```

2. **Check voice-chat-server:**
   ```bash
   curl http://localhost:5001/status
   # Should return: {"status": "ok", "ollama": {...}}
   ```

3. **Verify model is loaded:**
   ```bash
   ollama list
   # Should show llama3.1 or configured model
   ```

4. **Test chat directly:**
   ```bash
   curl -X POST http://localhost:5001/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello"}'
   ```

5. **Restart voice-chat-server:**
   ```bash
   ./scripts/start-voice-chat.sh
   ```

### CORS Errors

**Symptoms:** Console shows "Access-Control-Allow-Origin" errors

**Solutions:**
1. **Verify all services on localhost:**
   - Web UI: http://localhost:8080
   - Camera: http://localhost:8097 (iframe, bypasses CORS)
   - Backend: http://localhost:5000, 5001

2. **For iframe camera:**
   - Iframe bypasses CORS by design
   - If still failing, check Live Stream Broadcast is running

3. **For API calls:**
   - Ensure backends set CORS headers
   - Check voice-chat-server.py has CORS enabled

### High Latency

**Symptoms:** Camera feed delayed (>2 seconds) or servo lag

**Solutions:**
1. **Camera latency:**
   - Reduce camera resolution in ARC Camera Device skill
   - Close other applications using camera
   - Check CPU usage (high CPU = slower encoding)

2. **Servo latency:**
   - Verify backend is running on Windows (not WSL)
   - Check file system performance (SSD recommended)
   - Reduce polling interval in web interface

3. **Chat latency:**
   - Use smaller LLM model (llama3.1:8b instead of 70b)
   - Increase Ollama context window if needed
   - Check GPU utilization (if using GPU acceleration)

### Connection Refused Errors

**Symptoms:** "ERR_CONNECTION_REFUSED" in browser

**Solutions:**
1. **Identify which port:**
   ```bash
   # Check which ports are listening
   netstat -tlnp | grep -E "8080|8097|5000|5001"
   ```

2. **Start missing service:**
   - Port 8080: Start HTTP Server Custom in ARC
   - Port 8097: Start Live Stream Broadcast in ARC
   - Port 5000: Run `python servo-backend.py` (Windows)
   - Port 5001: Run `./scripts/start-voice-chat.sh` (WSL)

3. **Check firewall:**
   ```bash
   # Windows Firewall
   netsh advfirewall firewall show rule name=all | grep python
   
   # Allow Python if blocked
   netsh advfirewall firewall add rule name="Python" dir=in action=allow program="C:\Python311\python.exe" enable=yes
   ```

### WSL Networking Issues

**Symptoms:** WSL can't reach Windows services or vice versa

**Solutions:**
1. **Test WSL → Windows:**
   ```bash
   curl http://localhost:5000/status
   # From WSL, should reach Windows backend
   ```

2. **Test Windows → WSL:**
   ```powershell
   # From Windows PowerShell
   curl http://localhost:5001/status
   # Should reach WSL voice-chat-server
   ```

3. **Restart WSL:**
   ```powershell
   # From Windows (admin)
   wsl --shutdown
   # Then restart WSL terminal
   ```

4. **Check /etc/hosts in WSL:**
   ```bash
   cat /etc/hosts
   # Should have: 127.0.0.1 localhost
   ```

## Diagnostic Commands

### Quick Status Check

```bash
# Run all checks
echo "=== Genesis Mission Control Status ==="
echo ""
echo "1. HTTP Server (8080):"
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 && echo " ✅" || echo " ❌"
echo ""
echo "2. Camera Stream (8097):"
curl -s -o /dev/null -w "%{http_code}" http://localhost:8097/live && echo " ✅" || echo " ❌"
echo ""
echo "3. Servo Backend (5000):"
curl -s http://localhost:5000/status 2>/dev/null && echo " ✅" || echo " ❌"
echo ""
echo "4. Voice Chat (5001):"
curl -s http://localhost:5001/status 2>/dev/null && echo " ✅" || echo " ❌"
echo ""
echo "5. Ollama (11434):"
curl -s http://localhost:11434/api/tags >/dev/null && echo " ✅" || echo " ❌"
```

### Log Collection

```bash
# Collect logs for debugging
mkdir -p /tmp/genesis-logs
echo "=== Web Interface ===" > /tmp/genesis-logs/web.log
curl http://localhost:8080 > /tmp/genesis-logs/web.log 2>&1

echo "=== Camera Stream ===" > /tmp/genesis-logs/camera.log
curl -I http://localhost:8097/live > /tmp/genesis-logs/camera.log 2>&1

echo "=== Servo Backend ===" > /tmp/genesis-logs/servo.log
curl http://localhost:5000/status > /tmp/genesis-logs/servo.log 2>&1

echo "=== Voice Chat ===" > /tmp/genesis-logs/voice.log
curl http://localhost:5001/status > /tmp/genesis-logs/voice.log 2>&1

echo "Logs saved to /tmp/genesis-logs/"
```

## Getting Help

### Information to Provide

When reporting issues, include:
1. **OS Version:** Windows 10/11, WSL version
2. **ARC Version:** Help → About in ARC
3. **Python Version:** `python --version`
4. **Error Messages:** Full console output
5. **Steps to Reproduce:** Exact sequence of actions
6. **Diagnostic Output:** Run the status check script above

### Where to Get Help

- **GitHub Issues:** https://github.com/bffrobots/genesis-mission-control/issues
- **Email:** support@bffrobots.com
- **Documentation:** https://github.com/bffrobots/genesis-mission-control/docs

---

**Last Updated:** June 30, 2026
