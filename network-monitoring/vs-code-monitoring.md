# VS Code Copilot Network Monitoring

Methods for monitoring actual GitHub Copilot network activity in VS Code.

## Method 1: VS Code Developer Tools

### Open DevTools
1. Open VS Code
2. Press `Ctrl+Shift+I` (Linux/Windows) or `Cmd+Option+I` (Mac)
3. Go to the **Network** tab
4. Start using Copilot (chat, completions, etc.)

### Filter Network Requests
Filter by domain to see Copilot-specific traffic:
- `copilot`
- `github.com`
- `api.githubcopilot.com`
- `api.github.com`

### What to Look For
- **Request URLs**: Endpoints being called
- **Headers**: Authentication tokens, API versions
- **Payload**: Request/response data (may be encrypted)
- **Timing**: Network latency, response times
- **Status codes**: Success/failure indicators

## Method 2: VS Code Network Logging

### Enable Network Logging
```bash
# Start VS Code with network logging
code --log net --log-level trace

# Specify custom log directory
code --log-net-log=/tmp/copilot-network.json
```

### View Logs
```bash
# Default log location
ls -la ~/.config/Code/logs/

# View most recent logs
tail -f ~/.config/Code/logs/*/network.log
```

## Method 3: System-Level Network Monitoring

### Using tcpdump (Requires root)
```bash
# Capture HTTPS traffic
sudo tcpdump -i any -w copilot-traffic.pcap 'host api.githubcopilot.com'

# Analyze with Wireshark
wireshark copilot-traffic.pcap
```

### Using mitmproxy
```bash
# Install
pip install mitmproxy

# Run proxy
mitmproxy -p 8080

# Configure VS Code to use proxy
export https_proxy=http://localhost:8080
code
```

## Method 4: VS Code Extension API

### Create a Monitoring Extension
```javascript
// extension.js
const vscode = require('vscode');

function activate(context) {
    // Monitor Copilot API calls
    const disposable = vscode.commands.registerCommand(
        'copilot.monitor',
        function () {
            vscode.window.showInformationMessage('Monitoring Copilot activity...');
            
            // Hook into network requests
            // (requires appropriate VS Code APIs)
        }
    );
    
    context.subscriptions.push(disposable);
}

module.exports = { activate };
```

## Method 5: Browser-based Monitoring (Copilot Chat)

### Chrome DevTools for VS Code Web
If using VS Code in browser (vscode.dev or github.dev):

1. Press `F12` to open browser DevTools
2. Go to **Network** tab
3. Filter by `copilot` or `github`
4. Monitor API calls in real-time

## Copilot API Endpoints

Common endpoints you'll see:

### Completions
```
POST https://api.githubcopilot.com/completions
```

### Chat
```
POST https://api.githubcopilot.com/chat/completions
```

### Authentication
```
GET https://api.github.com/copilot_internal/v2/token
```

### Telemetry
```
POST https://copilot-telemetry.githubusercontent.com/telemetry
```

## Sample Network Request Structure

### Request Headers
```
Authorization: Bearer <token>
X-Request-Id: <uuid>
X-Github-Api-Version: 2023-07-07
Content-Type: application/json
```

### Request Body (Completion)
```json
{
  "prompt": "function calculateFibonacci",
  "max_tokens": 500,
  "temperature": 0.5,
  "top_p": 1,
  "n": 1,
  "stream": true
}
```

### Response Headers
```
Content-Type: application/json
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1697654321
```

## Privacy & Security Notes

⚠️ **Important Considerations:**

1. **Token Security**: Never log or share authentication tokens
2. **Code Privacy**: Be careful logging request/response bodies containing your code
3. **Rate Limits**: Monitor but don't abuse API calls
4. **Terms of Service**: Ensure monitoring complies with GitHub's ToS

## Automated Monitoring Script

### Simple Log Parser
```bash
#!/bin/bash
# monitor-copilot.sh

LOG_DIR="$HOME/.config/Code/logs"
LATEST_LOG=$(ls -t "$LOG_DIR"/*/console.log | head -1)

echo "Monitoring Copilot activity in: $LATEST_LOG"
tail -f "$LATEST_LOG" | grep -i "copilot" --line-buffered | while read line; do
    echo "[$(date '+%H:%M:%S')] $line"
done
```

Make executable:
```bash
chmod +x monitor-copilot.sh
./monitor-copilot.sh
```

## Integration with copilot-bridge

### Proxy Configuration
To route VS Code Copilot through your instrumented proxy:

1. Set environment variables:
   ```bash
   export HTTPS_PROXY=http://localhost:8080
   export NO_PROXY=localhost,127.0.0.1
   ```

2. Modify `proxy_instrumented.py` to proxy GitHub Copilot requests

3. Start VS Code with proxy:
   ```bash
   HTTPS_PROXY=http://localhost:8080 code
   ```

## Troubleshooting

### No Network Logs Appearing
- Ensure VS Code has network activity (use Copilot features)
- Check log level: `code --log-level trace`
- Verify log directory permissions

### Cannot See HTTPS Content
- HTTPS traffic is encrypted end-to-end
- Use mitmproxy with certificate installation for decryption
- Or use VS Code's internal logging (already decrypted)

### Performance Impact
- Network logging can slow down VS Code
- Use filtering to reduce log volume
- Disable logging when not needed

## Resources

- [VS Code Logging Documentation](https://code.visualstudio.com/docs/supporting/troubleshooting#_logging)
- [GitHub Copilot API (unofficial)](https://github.com/features/copilot)
- [mitmproxy Documentation](https://docs.mitmproxy.org/)
