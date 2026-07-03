# Tablet Testing Guide

Test Genesis Mission Control on a tablet PC without Ollama installed.

## Quick Start (Tablet PC)

### Option 1: Rule-Based Mode (No Ollama Required)

**Perfect for testing on tablets!**

1. **Install Python dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

2. **Start Servo Backend:**
   ```cmd
   scripts\start_genesis.bat
   ```

3. **Start Voice & Chat (works without Ollama!):**
   ```cmd
   scripts\start_voice_chat.bat
   ```
   
   You'll see:
   ```
   ⚠️  Ollama not available: ...
      Running in RULE-BASED MODE only
      Commands will work, but open conversation will not
   ```

4. **Access Web Interface:**
   ```
   http://localhost:8080
   ```

5. **Test Commands:**
   - "stand" → Robot stands
   - "sit" → Robot sits
   - "wave" → Robot waves
   - "dance" → Robot dances
   - "move servo 0 to 90 degrees" → Moves specific servo

### Option 2: Full AI Mode (With Ollama)

If you want full conversation:

1. **Install Ollama for Windows:**
   - Download: https://ollama.com/download
   - Run installer

2. **Pull model:**
   ```cmd
   ollama pull llama3.1
   ```

3. **Start Voice & Chat:**
   ```cmd
   scripts\start_voice_chat.bat
   ```

---

## Working Commands (No Ollama Needed)

| Command | Action |
|---------|--------|
| "stand" | Executes STAND pose |
| "sit" | Executes SIT pose |
| "wave" | Executes WAVE animation |
| "dance" | Executes DANCE animation |
| "bow" | Executes BOW motion |
| "walk" | Executes WALK gait |
| "stop" | Stops current action |
| "neutral" | Returns to neutral pose |
| "move servo 0 to 90 degrees" | Moves servo D0 to 90° |
| "navigate to kitchen" | Sets navigation target |

---

## Troubleshooting

### "Request timeout - server not responding"

**Cause:** Voice chat server not running

**Fix:**
```cmd
scripts\start_voice_chat.bat
```

### "Ollama connection timeout"

**Cause:** Ollama not installed or not running

**Fix:** Either:
1. Install Ollama: https://ollama.com/download
2. OR ignore - rule-based commands still work!

### "Cannot connect to ARC"

**Cause:** ARC HTTP Server not running

**Fix:**
1. Open ARC
2. Enable HTTP Server Custom skill
3. Ensure port is 8080

### "Servo backend not responding"

**Cause:** Servo backend not running

**Fix:**
```cmd
scripts\start_genesis.bat
```

---

## Test All Connections

```cmd
scripts\TEST_CONNECTIONS.bat
```

Expected output:
```
✅ ARC: OK
✅ Camera: OK
✅ Servo Backend: OK
✅ Voice Chat: OK
⚠️  Ollama: NOT RUNNING (optional)
```

---

## Tablet-Specific Tips

### Performance

- Close other browser tabs
- Use Chrome or Edge (best performance)
- Disable browser extensions if laggy

### Touch Interface

- All buttons are touch-friendly (min 44px)
- Sliders work with touch
- Chat input supports touch keyboard

### Battery Saving

- Reduce camera FPS in settings
- Close unused tabs
- Lower screen brightness

---

## Console Logs

Press F12 to see detailed logs:

```
[Voice & Chat] Initializing...
[Voice & Chat] ✅ WebSocket connected
[Voice & Chat] Response: "Executing stand..." (intent: stand)
[Voice & Chat] ✅ Sent to ARC: $Genesis_Command = {...}
```

---

## Next Steps

After testing on tablet:

1. ✅ Verify all commands work
2. ✅ Test servo control
3. ✅ Check camera feed
4. ✅ Test voice chat responses
5. ✅ Deploy to GitHub

---

**Last Updated:** June 30, 2026  
**Version:** 1.0.0
