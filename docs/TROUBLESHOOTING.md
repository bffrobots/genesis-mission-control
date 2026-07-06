# Troubleshooting Guide

**Common issues and solutions for Genesis Mission Control v2.0**

---

## 🔍 Quick Diagnostic

Run the diagnostic script first:

```bash
cd scripts
./diagnose.sh
```

**Expected Output:**
```
Checking HTTP Server (8080)... ✅ OK
Checking Camera Stream (8097)... ✅ OK
Checking Motion Control (5000)... ✅ OK
Checking Voice & Chat (5001)... ✅ OK
```

---

## 🐛 Common Issues

### Installation Issues

#### Python not found

**Error:**
```
ERROR: Python 3 not found!
```

**Solution:**
1. Download Python 3.11+ from https://www.python.org/downloads/
2. During installation, **check "Add Python to PATH"**
3. Restart Command Prompt
4. Verify: `python --version`

#### Dependencies not installed

**Error:**
```
[WARN] Dependencies not found!
```

**Solution:**
```cmd
cd scripts
install-dependencies.bat
```

**Or manually:**
```cmd
pip install flask flask-cors fastapi uvicorn websockets requests anthropic openai
```

---

### Port Issues

#### Port 5000 already in use (Motion Control)

**Error:**
```
[WARN] Port 5000 is already in use!
```

**Solution:**
```cmd
REM Find what's using port 5000
netstat -ano | findstr :5000

REM Kill the process (replace PID with actual number)
taskkill /F /PID <PID>

REM Restart
cd scripts
start-genesis.bat
```

**Prevention:** Only run one instance of motion control at a time.

#### Port 5001 already in use (Voice & Chat)

**Error:**
```
[WARN] Port 5001 is already in use!
```

**Solution:**
```cmd
REM Find what's using port 5001
netstat -ano | findstr :5001

REM Kill the process
taskkill /F /PID <PID>

REM Restart
cd scripts
start.bat
```

**Prevention:** Only run one instance of voice & chat at a time.

---

### ARC Integration Issues

#### ARC HTTP Server not responding

**Error:**
```
[WARN] ARC HTTP Server not responding on port 8080
```

**Solution:**
1. Open Synthiam ARC
2. Add **HTTP Server Custom** skill (if not already added)
3. Configure:
   - Port: 8080
   - Root Directory: `%USERPROFILE%\Documents\ARC\HTTP Server Root`
4. Enable the skill
5. Verify: `curl http://localhost:8080/get.html?var=$Genesis_Status`

#### Commands work but robot doesn't move

**Symptoms:**
- Web interface sliders move
- No error messages
- Robot doesn't respond

**Solution:**

1. **Check ARC is running:**
   - Open ARC
   - Load Genesis project

2. **Check HTTP Server Custom:**
   ```cmd
   curl http://localhost:8080/get.html?var=$Genesis_Status
   ```
   Should return a value

3. **Check servo files:**
   ```cmd
   dir "%USERPROFILE%\Documents\ARC\HTTP Server Root\Servo_D*.txt"
   ```
   Should show files like `Servo_D0.txt`, `Servo_D1.txt`, etc.

4. **Check Variable Watch:**
   - In ARC, add **Variable Watch** skill
   - Watch variable: `$Genesis_Command`
   - Send voice command: "stand up"
   - Verify variable is being set

5. **Check Auto Position skill:**
   - Ensure **Auto Position** skill is active
   - Verify poses exist: STAND, SIT, WAVE, etc.

6. **Test API:**
   ```cmd
   curl http://localhost:5000/status
   curl -X POST http://localhost:5000/api/servo -H "Content-Type: application/json" -d "{\"servo_id\": 0, \"position\": 90, \"port\": \"D0\"}"
   ```

---

### Voice & Chat Issues

#### AI not available

**Error:**
```
[INFO] No API key found - running in RULE-BASED MODE only
```

**Note:** This is NOT an error! Commands still work <1ms.

**To enable AI conversations:**

1. Get API key from https://console.anthropic.com/
2. Set environment variable:
   ```cmd
   setx ANTHROPIC_API_KEY "sk-ant-..."
   ```
3. Restart voice & chat server:
   ```cmd
   cd scripts
   start.bat
   ```

#### High latency (>5 seconds)

**Symptoms:**
- AI responses take >5 seconds
- Commands still work <1ms

**Solution:**

1. **Test network:**
   ```cmd
   curl -w "Time: %{time_total}s\n" -o /dev/null -s https://api.anthropic.com
   ```
   Should be <2 seconds

2. **Check API key:**
   ```cmd
   echo %ANTHROPIC_API_KEY%
   ```
   Should show your key (not empty)

3. **Check API quota:**
   - Go to https://console.anthropic.com/
   - Verify you have quota remaining

4. **Use rule-based mode for commands:**
   - Commands always work <1ms (no AI needed)
   - Only use AI for conversation

#### Voice commands not working

**Symptoms:**
- Chat interface shows "offline"
- No response to commands

**Solution:**

1. **Check server is running:**
   ```cmd
   curl http://localhost:5001/status
   ```

2. **Check web interface:**
   - Open browser: http://localhost:8080
   - Go to Voice & Chat tab
   - Check connection status

3. **Check browser console:**
   - Press F12
   - Go to Console tab
   - Look for errors

4. **Restart server:**
   ```cmd
   cd scripts
   start.bat
   ```

---

### Motion Control Issues

#### Web interface sliders don't move robot

**Symptoms:**
- Sliders move in web interface
- Robot servos don't move
- No error messages

**Solution:**

1. **Verify motion control backend is running:**
   ```cmd
   curl http://localhost:5000/status
   ```
   Should return `{"status": "ok", ...}`

2. **Check servo files are created:**
   ```cmd
   dir "%USERPROFILE%\Documents\ARC\HTTP Server Root\Servo_D*.txt"
   ```
   Files should update when you move sliders

3. **Check ARC is reading files:**
   - In ARC, verify HTTP Server Custom is enabled
   - Check ARC script is polling servo files

4. **Test servo directly:**
   ```cmd
   curl -X POST http://localhost:5000/api/servo -H "Content-Type: application/json" -d "{\"servo_id\": 0, \"position\": 90, \"port\": \"D0\"}"
   ```
   Robot servo D0 should move to 90°

#### Emergency stop not working

**Symptoms:**
- E-STOP button doesn't disable servos

**Solution:**

1. **Check E-STOP file:**
   ```cmd
   type "%USERPROFILE%\Documents\ARC\HTTP Server Root\Genesis_EStop.txt"
   ```
   Should contain "1" when pressed

2. **Check ARC script:**
   - Verify ARC is monitoring `Genesis_EStop.txt`
   - Check script disables servos on E-STOP

3. **Manual E-STOP:**
   - In ARC, use **Script Manager**
   - Run: `EZB.Servo.DisableAll()`

---

### Camera Issues

#### Camera feed not displaying

**Symptoms:**
- Black screen or placeholder image
- "Camera offline" message

**Solution:**

1. **Check camera is connected:**
   - Open ARC
   - Verify **Camera Device** skill is active
   - Check camera preview in ARC

2. **Check Live Stream Broadcast:**
   - Verify **Live Stream Broadcast** skill is enabled
   - Check port 8097:
     ```cmd
     curl -I http://localhost:8097/live
     ```
     Should return `HTTP/1.1 200 OK`

3. **Check web interface:**
   - Open browser: http://localhost:8080
   - Press F12 → Console
   - Look for camera errors

4. **Test stream directly:**
   ```cmd
   curl http://localhost:8097/live
   ```
   Should return video data

---

### Performance Issues

#### Slow web interface

**Symptoms:**
- Web page loads slowly
- Sliders lag
- High CPU usage

**Solution:**

1. **Reduce update rate:**
   - In web interface, reduce polling interval
   - Camera: 100ms → 200ms
   - Variables: 100ms → 500ms

2. **Close other applications:**
   - Free up CPU and RAM
   - Close unnecessary browser tabs

3. **Check browser:**
   - Use Chrome or Edge (best performance)
   - Clear browser cache
   - Disable unnecessary extensions

4. **Reduce servo count:**
   - If controlling 18 servos, try reducing to essential ones
   - Update web interface to only show needed servos

#### Voice & Chat slow responses

**Symptoms:**
- AI responses take >5 seconds
- Commands still fast (<1ms)

**Solution:**

1. **Check internet connection:**
   ```cmd
   ping api.anthropic.com
   ```
   Should be <100ms

2. **Check API status:**
   - Go to https://status.anthropic.com/
   - Verify no outages

3. **Use smaller model:**
   - If using Claude, try `claude-3-haiku-20240307` (faster)
   - Update `voice-chat-server-v2.py` model setting

4. **Commands still work fast:**
   - Remember: commands use rule-based parsing (<1ms)
   - Only conversation uses AI (1-2s typical)

---

## 📞 Getting Help

### Still Having Issues?

1. **Run diagnostics:**
   ```cmd
   cd scripts
   ./diagnose.sh
   ```

2. **Check logs:**
   - Motion control: Check terminal output from `start-genesis.bat`
   - Voice & chat: Check terminal output from `start.bat`

3. **Check documentation:**
   - [README.md](../README.md) - Complete guide
   - [QUICKSTART.md](QUICKSTART.md) - 5-minute setup
   - [ARCHITECTURE.md](ARCHITECTURE.md) - System design

4. **GitHub Issues:**
   - Go to: https://github.com/bffrobots/genesis-mission-control/issues
   - Search for similar issues
   - Create new issue with:
     - Error messages
     - Diagnostic output
     - Steps to reproduce

### Information to Include

When reporting issues, include:

1. **System info:**
   ```cmd
   python --version
   ver
   ```

2. **Diagnostic output:**
   ```cmd
   cd scripts
   ./diagnose.sh
   ```

3. **Error messages:**
   - Copy exact error text
   - Include terminal output

4. **Steps to reproduce:**
   - What were you doing?
   - What commands did you run?
   - What did you expect vs what happened?

---

**Last Updated:** July 5, 2026  
**Version:** 2.0.0
