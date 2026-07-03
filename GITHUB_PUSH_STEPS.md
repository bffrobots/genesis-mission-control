# GitHub Push Instructions

## Quick Push Guide

Follow these steps to push Genesis Mission Control to GitHub.

---

## Step 1: Verify Repository Exists

**Check if repo exists:**
```bash
curl -I https://github.com/bffrobots/genesis-mission-control
```

**If 404 (Not Found):** Create it first:
1. Go to: https://github.com/new
2. Repository name: `genesis-mission-control`
3. Owner: `bffrobots` (or your username)
4. **DO NOT** initialize with README
5. Click "Create repository"

---

## Step 2: Check Git Status

```bash
cd /home/genesis/.hermes/skills/robotics/genesis-mission-control

# Check current status
git status

# Should show:
# On branch master
# nothing to commit, working tree clean
```

---

## Step 3: Verify Remote URL

```bash
git remote -v

# Should show:
# origin  https://github.com/bffrobots/genesis-mission-control.git (fetch)
# origin  https://github.com/bffrobots/genesis-mission-control.git (push)
```

**If wrong, fix it:**
```bash
git remote set-url origin https://github.com/bffrobots/genesis-mission-control.git
# OR for personal account:
git remote set-url origin https://github.com/YOUR_USERNAME/genesis-mission-control.git
```

---

## Step 4: Add All Files

```bash
# Add all files to staging
git add .

# Verify what will be pushed
git status

# Should show all files as "new file" or "modified"
```

---

## Step 5: Commit

```bash
git commit -m "v1.0.0 - Initial release: Genesis Mission Control

Features:
- 18 DOF motion control via web interface
- Live camera feed (HLS streaming)
- Voice & chat integration (Whisper + Ollama)
- Agentic AI platform support (Hermes, LangChain, AutoGen, CrewAI)
- OpenClaw hardware integration
- Claude Code autonomous coding
- Synthiam ARC App available

Documentation:
- 7 comprehensive guides
- Security audit passed
- Installation & troubleshooting guides

Files: 21
Size: 480KB
License: MIT"
```

---

## Step 6: Push to GitHub

### Option A: Using Personal Access Token (Recommended)

```bash
git push -u origin master
```

**When prompted:**
- **Username:** Your GitHub username
- **Password:** Paste your **Personal Access Token** (NOT GitHub password)

**Get token:** https://github.com/settings/tokens
- Click "Generate new token (classic)"
- Scope: ✅ `repo` (full control)
- Expiration: 1 year
- Copy token and use as password

---

### Option B: Using GitHub CLI

```bash
# Install if needed
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg

# Authenticate
gh auth login

# Push
git push -u origin master
```

---

### Option C: Using SSH (If Configured)

```bash
# Change remote to SSH
git remote set-url origin git@github.com:bffrobots/genesis-mission-control.git

# Push
git push -u origin master
```

---

## Step 7: Verify Push

**Check on GitHub:**
1. Go to: https://github.com/bffrobots/genesis-mission-control
2. Verify all files are there
3. Check README displays correctly

**Test clone:**
```bash
# In a different directory
git clone https://github.com/bffrobots/genesis-mission-control.git
cd genesis-mission-control
ls -la
```

---

## Step 8: Create GitHub Release

1. Go to: https://github.com/bffrobots/genesis-mission-control/releases/new
2. **Tag version:** `v1.0.0`
3. **Release title:** `Genesis Mission Control v1.0.0`
4. **Description:**
   ```markdown
   ## 🎉 Initial Release

   ### Features
   - 18 DOF motion control via web interface
   - Live camera feed with HLS streaming
   - Voice & chat integration (Whisper + Ollama)
   - Agentic AI platform support
   - Synthiam ARC App available

   ### Documentation
   - 7 comprehensive guides
   - Security audit passed
   - Installation & troubleshooting

   ### Downloads
   - ARC App: https://synthiam.com/Community/Apps/Genesis_Mission_Control-23372

   ### Quick Start
   ```bash
   git clone https://github.com/bffrobots/genesis-mission-control.git
   cd genesis-mission-control
   pip install -r requirements.txt
   ./scripts/start_genesis.sh
   ```
   ```
5. Click "Publish release"

---

## Troubleshooting

### Permission Denied (403)

**Error:** `remote: Permission to bffrobots/genesis-mission-control.git denied to [user]`

**Solution:** Use personal account instead:
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/genesis-mission-control.git
git push -u origin master
```

### Repository Not Found (404)

**Error:** `remote: Repository not found`

**Solution:** Create repository first:
1. https://github.com/new
2. Name: `genesis-mission-control`
3. Create, then push

### Authentication Failed

**Error:** `fatal: Authentication failed`

**Solution:**
1. Generate new token: https://github.com/settings/tokens
2. Use token as password (not GitHub password)
3. Or use SSH: `git remote set-url origin git@github.com:...`

### Wrong Branch

**Error:** `error: src refspec main does not match any`

**Solution:** Use `master` branch:
```bash
git push -u origin master
```

---

## Post-Push Checklist

- [ ] Verify all 21 files on GitHub
- [ ] Check README renders correctly
- [ ] Test clone works
- [ ] Create release v1.0.0
- [ ] Add topic tags: `robotics`, `humanoid-robot`, `ai-agents`, `synthiam`, `arc`
- [ ] Share on Synthiam community
- [ ] Update ARC App description with GitHub link

---

## Quick Reference

```bash
# Full push sequence
cd /home/genesis/.hermes/skills/robotics/genesis-mission-control
git add .
git commit -m "v1.0.0 - Initial release"
git push -u origin master

# Enter GitHub username
# Enter Personal Access Token
```

---

**Last Updated:** June 30, 2026  
**Version:** 1.0.0
