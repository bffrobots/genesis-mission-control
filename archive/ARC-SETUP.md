# 🤖 ARC PROJECT SETUP GUIDE - Genesis Motion Control

## ⚠️ ERROR: Required Skills Missing

You need to add these skills to your ARC project **in this exact order**:

---

## ✅ Required ARC Skills (Add in Order)

### **1. Servo Configuration** ⭐ FIRST!

**Why**: Controls physical servos (D0-D17)

**How to Add**:
1. In ARC, click **"Add Skill"** button
2. Search for **"Servo Configuration"**
3. Click to add it
4. **Configure servos D0-D17**:
   - Click each port (D0, D1, D2... D17)
   - Set **Min**: 30 (or your servo's min)
   - Set **Max**: 150 (or your servo's max)
   - Set **Center**: 90
   - **Check "Enabled"** for each port
5. Click **"Start"** button on the skill

**Verify**: You should see 18 servo sliders in the skill window

---

### **2. HTTP Server Custom**

**Why**: Serves web interface and handles variable commands

**How to Add**:
1. Click **"Add Skill"**
2. Search for **"HTTP Server Custom"**
3. Add it
4. **Configure**:
   - Port: **8080**
   - Root Directory: `C:\Users\Perseus\Documents\ARC\HTTP Server Root\`
   - Check **"Enable"**
5. Click **"Start"**

**Verify**: Open browser to `http://localhost:8080/index.html`

---

### **3. Script Collection**

**Why**: Runs GenesisBridge script

**How to Add**:
1. Click **"Add Skill"**
2. Search for **"Script Collection"**
3. Add it
4. **Add GenesisBridge script**:
   - Click **"Add Script"**
   - Name: `GenesisBridge`
   - Paste the script code (below)
   - Click **Save**
5. **Start the script**

**Verify**: Console shows "Genesis Bridge starting..."

---

### **4. Variable Watch** (Optional but Recommended)

**Why**: Monitor servo variables in real-time

**How to Add**:
1. Click **"Add Skill"**
2. Search for **"Variable Watch"**
3. Add it
4. **Add variables to watch**:
   - `$Servo_D0`
   - `$Servo_D1`
   - ... (add all through `$Servo_D17`)
   - `$GenesisBridge_Log`

**Verify**: You'll see variable values update when commands arrive

---

## 📝 GenesisBridge Script (Final Working Version)

**Copy this into Script Collection**:

```javascript
// GenesisBridge.js - Servo Control
print("Genesis Bridge starting...");

// Initialize servo variables
var i = 0;
while (i < 18) {
    var varName = "$Servo_D" + i;
    setVar(varName, -1);
    i = i + 1;
}
print("Initialized D0-D17");

// Check all servos once
var servoIndex = 0;
while (servoIndex < 18) {
    var varName = "$Servo_D" + servoIndex;
    var targetPos = getVar(varName);
    
    if (targetPos != -1 && targetPos != 0 && targetPos != "") {
        var port = "D" + servoIndex;
        var position = parseInt(targetPos);
        
        if (position >= 0 && position <= 180) {
            print("Servo " + port + " -> " + position);
            
            // Use ControlCommand with correct skill name
            controlCommand("Servo Configuration", "SetPosition", port, position, 50);
            
            setVar(varName, -1);
        }
    }
    
    servoIndex = servoIndex + 1;
}

print("Servo check complete - waiting for next command");
```

---

## 🧪 Test Setup

### **Test 1: Verify Servo Configuration**
1. Open **Servo Configuration** skill
2. You should see sliders for D0-D17
3. Move slider D0 manually
4. **Servo D0 should move physically**

If this works → Servos are configured correctly ✅

### **Test 2: Verify HTTP Server**
```bash
curl http://localhost:8080/index.html
```
Should return HTML → HTTP Server working ✅

### **Test 3: Verify Genesis Backend**
```bash
curl http://localhost:5000/api/status
```
Should return JSON → Backend working ✅

### **Test 4: Test Script**
1. Start **GenesisBridge** script
2. Console should show:
   ```
   Genesis Bridge starting...
   Initialized D0-D17
   Servo check complete - waiting for next command
   ```

### **Test 5: Move Servo via API**
```cmd
curl -X POST http://localhost:5000/api/command ^
  -H "Content-Type: application/json" ^
  -d "{\"type\":\"move_servo\",\"data\":{\"port\":\"D0\",\"position\":90}}"
```

**Expected**:
- Backend logs: `Servo command sent: D0 -> 90°`
- Script console: `Servo D0 -> 90`
- **Physical servo D0 moves to 90°** 🎉

---

## 🔧 Troubleshooting

### **"Servo Configuration skill does not exist"**
→ Add Servo Configuration skill first (see Step 1)

### **"EZB.Servo is undefined"**
→ Use `controlCommand()` not `EZB.Servo.SetPosition()`

### **"Sleep is not defined"**
→ Don't use Sleep() - script runs once and repeats via Script Collection

### **"setInterval is not defined"**
→ ARC doesn't support browser JavaScript functions

### **"True is not defined"**
→ Use lowercase `true` or `1` instead of `True`

### **Script runs but servos don't move**
1. Check Servo Configuration is **started** (green light)
2. Verify servos D0-D17 are **enabled** (checkboxes checked)
3. Check Variable Watch shows `$Servo_D0` changing to 90

### **Web interface shows "Internal Server Error"**
→ Genesis backend not running. Start with:
```cmd
cd C:\Users\Roberto\Genesis_Mission_Control
python main_robust.py
```

---

## 📊 Complete Skill Order

Your ARC project should have these skills **in this order** (top to bottom):

1. **Servo Configuration** ⭐ (Must be first!)
2. **HTTP Server Custom**
3. **Script Collection**
4. **Variable Watch** (optional)

**Start all skills** (green play button on each)

---

## 🎯 Success Checklist

- [ ] Servo Configuration skill added and started
- [ ] Servos D0-D17 enabled in configuration
- [ ] HTTP Server Custom running on port 8080
- [ ] Script Collection running GenesisBridge script
- [ ] Variable Watch showing servo variables
- [ ] Genesis backend running on port 5000
- [ ] Web interface loads at `http://localhost:8080/index.html`
- [ ] Test API command moves physical servo
- [ ] Web slider moves physical servo

---

## 🚀 After Setup Works

Once basic servo control works, we can add:

1. **Auto Position frames** (STAND, SIT, WAVE, DANCE)
2. **Pose library** in web interface
3. **Motion recording** and playback
4. **Voice commands** through Genesis AI
5. **Camera integration** for vision
6. **Walking gaits** for locomotion

---

**Add Servo Configuration skill first, then test again!** 🤖✨
