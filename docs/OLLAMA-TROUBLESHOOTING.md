# Ollama Troubleshooting Guide

## Common Errors

### 404 Error: "intent: conversation, action:null"

**Cause:** Ollama model name mismatch or model not loaded

**Symptoms:**
- Voice & Chat dashboard shows: `Ollama error: 404 (intent: conversation, action:null)`
- Rule-based commands work (stand, sit, wave)
- AI conversation fails

**Solution:**

1. **Check available models:**
   ```bash
   curl http://localhost:11434/api/tags
   ```
   
   Expected output:
   ```json
   {
     "models": [
       {"name": "llama3.2:latest"},
       {"name": "llama3.1:latest"}
     ]
   }
   ```

2. **If no models listed, pull one:**
   ```bash
   ollama pull llama3.2
   ```
   
   Or for smaller/faster model:
   ```bash
   ollama pull llama3.2:1b
   ```

3. **Restart voice chat server:**
   ```batch
   scripts\start_voice_chat.bat
   ```
   
   You should see:
   ```
   ✅ Ollama detected: http://localhost:11434
   📦 Using model: llama3.2:latest
   Available Models: llama3.2:latest, llama3.1:latest
   ```

4. **Test connection:**
   ```bash
   curl http://localhost:5001/status
   ```
   
   Check that `ollama_available: true` and `available_models` is populated.

### Connection Timeout

**Cause:** Ollama not running or slow tablet performance

**Symptoms:**
- `Read timed out (readtimeout=30)`
- Long delays before response

**Solution:**

1. **Ensure Ollama is running:**
   ```bash
   ollama serve
   ```
   
   Or on Windows, check Task Manager for `ollama.exe`

2. **Increase timeout (already set to 120s in code):**
   ```bash
   set OLLAMA_TIMEOUT=180
   scripts\start_voice_chat.bat
   ```

3. **Use smaller model for faster response:**
   ```bash
   ollama pull llama3.2:1b
   ```

### Model Not Found

**Cause:** Configured model name doesn't match installed model

**Symptoms:**
- `Model 'llama3.1' not found`
- Server starts but uses fallback

**Solution:**

The updated server auto-detects available models and uses the first one if the configured model isn't found. You can also:

1. **Set the correct model name:**
   ```bash
   set OLLAMA_MODEL=llama3.2:latest
   scripts\start_voice_chat.bat
   ```

2. **Or pull the expected model:**
   ```bash
   ollama pull llama3.1
   ```

## Quick Diagnostic Script

Create `TEST_OLLAMA.bat`:

```batch
@echo off
echo === Ollama Diagnostic ===
echo.
echo 1. Checking Ollama service...
curl http://localhost:11434/api/tags
echo.
echo 2. Testing voice chat server...
curl http://localhost:5001/status
echo.
echo 3. Testing ARC connection...
curl http://localhost:8080
echo.
echo 4. Testing servo backend...
curl http://localhost:5000/status
echo.
echo === Done ===
pause
```

## Rule-Based Mode (Works Without Ollama)

If Ollama isn't available, the server runs in **rule-based mode**. These commands still work:

- `"stand"` - Robot stands up
- `"sit"` - Robot sits down
- `"wave"` - Robot waves hand
- `"dance"` - Robot dances
- `"bow"` - Robot bows
- `"walk"` - Robot walks
- `"stop"` - Robot stops
- `"move servo 5 to 90 degrees"` - Direct servo control
- `"navigate to kitchen"` - Navigation command

**Limitation:** Open-ended conversation won't work. You'll get:
> "I heard: 'hello'. Try commands like 'stand', 'sit', 'wave', 'dance'."

## Performance Tips for Surface Tablet

1. **Use smaller model:** `llama3.2:1b` (1B parameters, faster)
2. **Close other apps:** Free up RAM for Ollama
3. **Plug in:** Ensure tablet is charging during use
4. **SSD space:** Keep 10GB+ free for model caching
5. **First run slow:** Models load faster after first use

## Support

If issues persist:
1. Check Ollama logs: `ollama serve --debug`
2. Check voice chat logs in terminal
3. Verify all ports: 11434 (Ollama), 5001 (Voice Chat), 8080 (ARC), 5000 (Servo)
4. Restart all services in order: Ollama → Voice Chat → ARC
