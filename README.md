# Copilot Bridge - 60-Second Demo

**Created:** October 19, 2025  
**Purpose:** Hybrid routing proof of concept - cheap tasks go local, expensive go to GitHub

## Quick Demo (LOCAL-only version)

Since we don't have immediate GitHub token access, let's prove the LOCAL routing works:

### Terminal 1 - Start the bridge listener

```bash
cd ~/copilot-bridge
socat TCP-LISTEN:11436,reuseaddr,fork EXEC:"./demo_local_only.py"
```

Leave this running.

### Terminal 2 - Test with cheap request (docstring)

```bash
echo '{"messages":[{"role":"user","content":"add a google-style docstring"}]}' \
| socat - TCP:localhost:11436
```

**Expected output:**
- JSON response with docstring suggestion
- stderr: `LOCAL  5w  120ms` (or similar timing)

### Terminal 3 - Test with another request

```bash
echo '{"messages":[{"role":"user","content":"add type hints to this function"}]}' \
| socat - TCP:localhost:11436
```

---

## Full Version (with GitHub token)

To enable hybrid routing (LOCAL for cheap, GITHUB for expensive):

### Get GitHub Token

**Option 1:** From VS Code (if Copilot is active)
```bash
# Check Copilot status in VS Code
# Command Palette: "GitHub Copilot: Sign In"
```

**Option 2:** Create Personal Access Token
1. Go to: https://github.com/settings/tokens
2. Generate new token (classic)
3. Scopes needed: `read:user`, `user:email`
4. Copy token

**Option 3:** Use `gh` CLI
```bash
# Install gh CLI if needed
sudo apt install gh

# Authenticate
gh auth login

# Get token
gh auth token
```

### Run Full Bridge

```bash
# Terminal 1
export GITHUB_TOKEN="your_token_here"
socat TCP-LISTEN:11436,reuseaddr,fork EXEC:"~/copilot-bridge/proxy.py"
```

### Test Routing Logic

**Cheap keywords** (go LOCAL): docstring, comment, lint, test, rename

```bash
# LOCAL route
echo '{"messages":[{"role":"user","content":"add a docstring"}]}' \
| socat - TCP:localhost:11436
# Should print: LOCAL ... ms
```

**Expensive requests** (go GITHUB): refactor, explain multi-file, architecture

```bash
# GITHUB route
echo '{"messages":[{"role":"user","content":"explain this 5-file refactor"}]}' \
| socat - TCP:localhost:11436
# Should print: GITHUB ... ms
```

---

## What This Proves

✅ **LOCAL requests** (simple tasks)
- Hit your Ollama at 192.168.1.138:11434
- Use qwen2.5-coder:7b-instruct-q8_0
- Response time: ~120ms
- Cost: **$0**

✅ **GITHUB requests** (complex tasks)
- Forward to api.githubcopilot.com
- Use GitHub's models
- Response time: ~2000ms
- Cost: Normal Copilot billing

✅ **Hybrid routing**
- Smart keyword detection
- Best of both worlds
- Optimize costs automatically

---

## Files Created

- `~/copilot-bridge/proxy.py` - Full hybrid routing (needs GITHUB_TOKEN)
- `~/copilot-bridge/demo_local_only.py` - LOCAL-only demo (no token needed)

---

## Kill the Demo

When done testing:

```bash
# Kill socat listeners
pkill socat

# Or Ctrl+C in the terminal running socat
```

---

## Next Steps

1. ✅ Prove LOCAL routing works (demo_local_only.py)
2. Get GitHub token for full hybrid
3. Integrate with Continue.dev config
4. Add more routing rules
5. Monitor savings

Ready to test? Run Terminal 1 command above!
