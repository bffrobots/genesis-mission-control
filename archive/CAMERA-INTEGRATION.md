# Camera Integration - Live Stream Broadcast

## Overview

The Camera & Vision tab now uses ARC's **Live Stream Broadcast** skill (port 8097) to display live camera feedback from the humanoid robot using HLS video streaming.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Web Browser (http://localhost:8080)                        │
│                                                             │
│  Camera & Vision Tab                                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  <video>                                              │   │
│  │    <source src="http://localhost:8097/live"          │   │
│  │              type="application/x-mpegURL" />         │   │
│  │  </video>                                             │   │
│  │                                                       │   │
│  │  • HLS video streaming (adaptive bitrate)            │   │
│  │  • Low latency (~1-2 seconds)                        │   │
│  │  • Smooth playback with hardware acceleration        │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTP HLS Stream
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  ARC Live Stream Broadcast (Port 8097)                      │
│                                                             │
│  • HLS protocol (HTTP Live Streaming)                       │
│  • Adaptive bitrate streaming                               │
│  • Cross-browser compatible                                 │
│  • Can be accessed externally with router config            │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  ARC Camera Device Skill                                    │
│                                                             │
│  • Captures frames from USB camera                          │
│  • Provides frames to Live Stream Broadcast                 │
└──────────────────┬──────────────────────────────────────────┘
                   │ USB
                   ▼
          ┌─────────────────┐
          │  USB Camera     │
          │  (640x480)      │
          └─────────────────┘
```

## Setup Steps

### 1. Add Required ARC Skills

In ARC, ensure you have these skills active:

1. **Camera Device** (Skill ID: 16120)
   - Configure your USB camera
   - Set resolution: 640x480 or higher
   - Set FPS: 30 recommended

2. **Live Stream Broadcast** (from Skill Store)
   - Port: 8097 (default)
   - Stream path: /live
   - Enable: ✓
   - Configure camera source

3. **HTTP Server Custom** (Skill ID: 16126)
   - Port: 8080
   - Root Directory: `C:\Users\Perseus\Documents\ARC\HTTP Server Root\`
   - Enable: ✓

### 2. Verify Camera Stream in ARC

Before testing in the web interface:

1. Open ARC project
2. Double-click **Live Stream Broadcast** skill
3. Verify stream URL shows: `http://localhost:8097/live`
4. Click "Open in Browser" to test directly

### 3. Deploy Web Interface

The updated `index.html` is deployed to:
```
C:\Users\Perseus\Documents\ARC\HTTP Server Root\index.html
```

If you need to redeploy:
```bash
cp /home/genesis/.hermes/skills/robotics/genesis-mission-control/references/web-interface-index.html \
   "/mnt/c/Users/Perseus/Documents/ARC/HTTP Server Root/index.html"
```

### 4. Test Live Camera Feed

1. Open browser: `http://localhost:8080`
2. Click **Camera & Vision** in sidebar
3. Verify live camera feed displays in video player
4. Check latency (should be < 2 seconds)

## Video Element Reference

### Basic Usage
```html
<video id="live-camera-stream" 
       controls 
       autoplay 
       muted 
       playsinline 
       style="width:100%;height:100%;object-fit:cover;">
  <source src="http://localhost:8097/live" 
          type="application/x-mpegURL" />
  Your browser does not support HLS video playback.
</video>
```

### Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `controls` | ✗ | Show play/pause/volume controls |
| `autoplay` | ✗ | Start playing automatically |
| `muted` | ✗ | Mute audio (required for autoplay in most browsers) |
| `playsinline` | ✗ | Play inline on mobile (not fullscreen) |
| `src` | ✓ | HLS stream URL from Live Stream Broadcast |
| `type` | ✓ | `application/x-mpegURL` for HLS |

### Examples

**Standard (with controls)**:
```html
<video controls autoplay muted playsinline>
  <source src="http://localhost:8097/live" type="application/x-mpegURL" />
</video>
```

**Fullscreen Auto-Play (no controls)**:
```html
<video autoplay muted playsinline loop 
       style="width:100%;height:100%;object-fit:cover;">
  <source src="http://localhost:8097/live" type="application/x-mpegURL" />
</video>
```

**With Fallback Image**:
```html
<video autoplay muted playsinline>
  <source src="http://localhost:8097/live" type="application/x-mpegURL" />
  <img src="/camera-offline.jpg" alt="Camera offline" />
</video>
```

## Troubleshooting

### Video Not Playing

**Symptom**: Black screen or "loading" forever

**Solutions**:
1. Verify Live Stream Broadcast skill is running on port 8097
2. Test direct stream: `http://localhost:8097/live`
3. Check browser console (F12) for errors
4. Ensure camera is active in ARC (double-click Camera Device)
5. Try different browser (Chrome/Edge recommended for HLS)

### "Your browser does not support HLS"

**Symptom**: Fallback message displays

**Solutions**:
1. Use Chrome, Edge, or Safari (native HLS support)
2. Firefox requires extension for HLS playback
3. Add hls.js library for broader compatibility:
   ```html
   <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
   <script>
     if (Hls.isSupported()) {
       var video = document.getElementById('live-camera-stream');
       var hls = new Hls();
       hls.loadSource('http://localhost:8097/live');
       hls.attachMedia(video);
     }
   </script>
   ```

### High Latency

**Symptom**: Video is delayed (> 3 seconds)

**Solutions**:
1. Reduce camera resolution in Camera Device skill
2. Check network bandwidth (use localhost for lowest latency)
3. Close other applications using camera
4. Lower stream quality in Live Stream Broadcast settings

### Stream Works Directly but Not in Web Interface

**Symptom**: `http://localhost:8097/live` works but camera tab shows black

**Solutions**:
1. Check browser console for CORS errors
2. Verify video element is properly positioned in DOM
3. Check CSS z-index (detection overlays may cover video)
4. Ensure video has explicit width/height

## Live Stream Broadcast Configuration

### Port Settings

| Setting | Default | Recommended |
|---------|---------|-------------|
| Port | 8097 | 8097 (don't conflict with HTTP Server on 8080) |
| Stream Path | /live | /live |
| Full URL | http://localhost:8097/live | http://localhost:8097/live |

### External Access

To access camera stream from outside your network:

1. **Configure Router Port Forwarding**:
   - External Port: 8097
   - Internal IP: [Your PC's local IP]
   - Internal Port: 8097
   - Protocol: TCP

2. **Update Stream URL** in web interface:
   ```html
   <source src="http://[YOUR_PUBLIC_IP]:8097/live" type="application/x-mpegURL" />
   ```

3. **Security Considerations**:
   - Add authentication if exposing publicly
   - Use HTTPS for external access (requires SSL certificate)
   - Consider VPN instead of direct exposure

## Performance Tips

### Optimal Settings for Mini BFF Genesis

**Local Network (WiFi)**:
```html
<video autoplay muted playsinline 
       style="width:100%;height:100%;object-fit:cover;">
  <source src="http://localhost:8097/live" type="application/x-mpegURL" />
</video>
```

**USB Direct Connection**:
```html
<video autoplay muted playsinline 
       style="width:100%;height:100%;object-fit:cover;">
  <source src="http://localhost:8097/live" type="application/x-mpegURL" />
</video>
```

**Battery Power (Power Saving)**:
- Reduce camera resolution in Camera Device skill
- Lower FPS in Live Stream Broadcast settings
- Consider using `<ez-camera>` tag with longer interval instead

## Integration with Detection Overlays

The detection boxes and face recognition overlays are positioned absolutely over the video:

```html
<div class="camera-placeholder">
  <!-- Live video stream -->
  <video id="live-camera-stream" autoplay muted playsinline>
    <source src="http://localhost:8097/live" type="application/x-mpegURL" />
  </video>
  
  <!-- Detection overlays (positioned with CSS) -->
  <div class="detection-box" style="left:15%;top:20%;width:25%;height:55%">
    <span class="det-label">person 94%</span>
  </div>
  
  <!-- Face recognition -->
  <div class="face-circle" style="left:20%;top:22%;width:12%;height:18%">
    <span class="face-label">John D. (95%)</span>
  </div>
</div>
```

**Note**: Overlay positions are percentages relative to the video frame. Update these dynamically based on YOLO detection results from Genesis AI backend.

## Browser Compatibility

| Browser | HLS Support | Notes |
|---------|-------------|-------|
| Chrome | ✓ Native (v67+) | Recommended |
| Edge | ✓ Native (Chromium) | Recommended |
| Safari | ✓ Native (all versions) | Best on macOS/iOS |
| Firefox | ✗ Requires extension | Install "HLS.js" extension |
| Opera | ✓ Native (Chromium) | Good alternative |

## Related Documentation

- [ARC Live Stream Broadcast](https://synthiam.com/Support/Skills/Camera/Live-Stream-Broadcast?id=18664)
- [ARC Camera Device](https://synthiam.com/Support/Skills/Camera/Camera-Device?id=16120)
- [ARC HTTP Server Custom](https://synthiam.com/Support/Skills/Remote-Control/HTTP-Server-Custom?id=16126)
- [HLS Protocol Specification](https://developer.apple.com/documentation/http_live_streaming)
- [Genesis Web Interface Deployment Skill](../genesis-web-interface-deployment/SKILL.md)

## Version History

- **v1.1.0** (June 30, 2026): Updated to use Live Stream Broadcast (port 8097) with HLS video streaming - lower latency, smoother playback
- **v1.0.0** (June 30, 2026): Initial camera integration guide
