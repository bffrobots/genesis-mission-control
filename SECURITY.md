# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | ✅ Yes             |
| < 1.0   | ❌ No (Development) |

## Security Measures

### Network Security

**Localhost-Only by Default**
- All services bind to `127.0.0.1` (localhost)
- No external network exposure without explicit configuration
- CORS restrictions enforced between ports

**Ports Used**
| Port | Service | External Access | Default Auth |
|------|---------|----------------|--------------|
| 8080 | HTTP Server Custom (Web UI) | ❌ Local only | None (local) |
| 8097 | Live Stream Broadcast | ❌ Local only | None (local) |
| 5000 | Servo Backend (Windows) | ❌ Local only | None (local) |
| 5001 | Voice & Chat (WSL) | ❌ Local only | None (local) |

### Input Validation

**Servo Control**
- Position range enforced: 0-180 degrees
- Port validation: D0-D17 only
- Rate limiting: 10 commands/second max

**File Operations**
- Paths restricted to HTTP Server Root directory
- No arbitrary file read/write
- File extensions validated (.txt only for servo control)

**Chat/Voice**
- Input sanitization for LLM prompts
- Message length limits (4096 chars max)
- No shell command injection possible

### Credential Management

**No Hardcoded Secrets**
- No API keys in source code
- No passwords in configuration files
- No cloud credentials stored

**Environment Variables**
- `.env` file for local configuration
- `.env` excluded from Git (`.gitignore`)
- Example template provided (`.env.example`)

### Code Security

**No Third-Party Dependencies (Critical)**
- Web interface: Pure HTML/CSS/JS (no npm packages)
- Backend: Standard library only (requests, flask)
- Optional: HLS.js from CDN (can be vendored)

**Static Analysis**
- No `eval()` or `exec()` usage
- No dynamic code generation
- No unsafe deserialization

## Vulnerability Reporting

### How to Report

**Email:** security@bffrobots.com  
**Response Time:** 48 hours for critical issues

### What to Include

1. **Description:** Clear explanation of the vulnerability
2. **Impact:** What an attacker could achieve
3. **Reproduction:** Steps to reproduce the issue
4. **Environment:** OS, ARC version, Python version

### What to Expect

1. **Acknowledgment:** Within 48 hours
2. **Assessment:** Severity rating within 1 week
3. **Fix Timeline:** Based on severity:
   - Critical: 48 hours
   - High: 1 week
   - Medium: 2 weeks
   - Low: Next release

## Security Best Practices

### For Users

**Deployment**
- Keep services on localhost unless external access required
- Use firewall rules to block external access to ports
- Regularly update ARC and Python dependencies

**Configuration**
- Change default ports if exposing externally
- Add authentication for external access
- Use HTTPS proxy for external camera streams

**Monitoring**
- Check logs regularly for unusual activity
- Monitor servo commands for unexpected movements
- Watch for failed authentication attempts

### For Developers

**Code Contributions**
- No hardcoded credentials (will be rejected)
- Input validation for all user inputs
- Security-focused code review required

**Testing**
- Test with malformed inputs
- Verify rate limiting works correctly
- Check for information leakage in errors

## Security Audit History

### June 2026 - Initial Audit (Pre-GitHub Release)

**Auditor:** Genesis AI  
**Status:** ✅ Passed with Recommendations

**Findings:**
- ✅ No credential exposure
- ✅ Localhost-only binding
- ⚠️ Input validation needed improvement
- ⚠️ File system access too broad
- ⚠️ No rate limiting implemented

**Actions Taken:**
- ✅ Added servo position validation (0-180 range)
- ✅ Implemented command rate limiting
- ✅ Restricted file operations to specific directories
- ✅ Added comprehensive `.gitignore`
- ✅ Removed all development artifacts

**Residual Risks:**
- Web interface lacks authentication (acceptable for localhost)
- No encryption for local communication (acceptable for localhost)
- HLS.js loaded from CDN (can be vendored for offline use)

## Known Limitations

### Intentional Design Decisions

**No Authentication (Localhost)**
- Rationale: Adds complexity for local-only deployment
- Mitigation: Services bind to localhost only
- Risk Level: Low (requires local access)

**No Encryption (HTTP)**
- Rationale: Performance for local camera streaming
- Mitigation: Localhost-only binding
- Risk Level: Low (not exposed to network)

**No Sandbox**
- Rationale: Direct hardware access required for servo control
- Mitigation: Input validation and rate limiting
- Risk Level: Medium (mitigated by validation)

### Future Enhancements

**Planned Security Improvements:**
1. Optional authentication for localhost (development mode)
2. HTTPS support for external deployments
3. Servo command signing for critical operations
4. Audit logging for all robot actions
5. Role-based access control (RBAC)

## Compliance

### Data Privacy

**No Personal Data Collection**
- Camera feeds processed locally only
- Voice recordings not stored
- Chat logs not persisted (unless explicitly enabled)

**GDPR Considerations**
- No data leaves local machine by default
- User has full control over all data
- No third-party analytics or tracking

### Safety Standards

**Robot Safety**
- E-STOP always available (hardware and software)
- Servo positions validated before execution
- Emergency stop overrides all other commands

**Human-Robot Interaction**
- Force limiting on all servos
- Collision detection via camera/IMU
- Safe speed limits near humans

## Contact

**Security Team:** security@bffrobots.com  
**PGP Key:** Available upon request for encrypted communications

**General Inquiries:** support@bffrobots.com  
**Website:** https://www.bffrobots.com

---

**Last Updated:** June 30, 2026  
**Version:** 1.0.0  
**Next Review:** September 2026
