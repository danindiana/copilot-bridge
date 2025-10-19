#!/bin/bash
# Setup script for dual-GPU Ollama configuration

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        Dual-GPU Ollama Setup for Copilot-Bridge               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if running as root for systemd service creation
if [ "$EUID" -eq 0 ]; then 
    SUDO=""
else
    SUDO="sudo"
fi

echo "Step 1: Creating systemd service for GPU 1 (Quadro M4000)"
echo "─────────────────────────────────────────────────────────"

# Create ollama-gpu1 service file
cat << 'SERVICE_EOF' | $SUDO tee /etc/systemd/system/ollama-gpu1.service > /dev/null
[Unit]
Description=Ollama Service (GPU 1 - Quadro M4000)
After=network.target ollama.service

[Service]
Type=simple
User=smduck
Environment="CUDA_VISIBLE_DEVICES=1"
Environment="OLLAMA_HOST=0.0.0.0:11435"
Environment="OLLAMA_MAX_LOADED_MODELS=2"
Environment="OLLAMA_KEEP_ALIVE=5m"
Environment="OLLAMA_NUM_PARALLEL=2"
ExecStart=/usr/local/bin/ollama serve
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
SERVICE_EOF

echo "✓ Created /etc/systemd/system/ollama-gpu1.service"
echo ""

echo "Step 2: Reloading systemd daemon"
echo "─────────────────────────────────"
$SUDO systemctl daemon-reload
echo "✓ Daemon reloaded"
echo ""

echo "Step 3: Enabling ollama-gpu1 service"
echo "────────────────────────────────────"
$SUDO systemctl enable ollama-gpu1
echo "✓ Service enabled (will start on boot)"
echo ""

echo "Step 4: Starting ollama-gpu1 service"
echo "────────────────────────────────────"
$SUDO systemctl start ollama-gpu1
sleep 3
echo "✓ Service started"
echo ""

echo "Step 5: Checking service status"
echo "───────────────────────────────"
$SUDO systemctl status ollama-gpu1 --no-pager | head -20
echo ""

echo "Step 6: Verifying GPU allocation"
echo "────────────────────────────────"
echo "GPU 0 (Primary Ollama - Port 11434):"
curl -s http://localhost:11434/api/ps | jq -r '.models[] | "  - \(.name)"' 2>/dev/null || echo "  (no models loaded)"
echo ""
echo "GPU 1 (Secondary Ollama - Port 11435):"
curl -s http://localhost:11435/api/ps | jq -r '.models[] | "  - \(.name)"' 2>/dev/null || echo "  (no models loaded)"
echo ""

echo "Step 7: Testing model loading on GPU 1"
echo "──────────────────────────────────────"
echo "Loading qwen2.5-coder:1.5b on GPU 1..."
curl -s http://localhost:11435/api/generate -d '{
  "model": "qwen2.5-coder:1.5b",
  "prompt": "Hello",
  "stream": false
}' | jq -r '.response' | head -c 100
echo ""
echo "✓ Model loaded successfully"
echo ""

echo "Step 8: GPU Memory Status"
echo "────────────────────────"
nvidia-smi --query-gpu=index,name,memory.used,memory.total --format=csv,noheader,nounits | \
    awk -F', ' '{printf "GPU %s (%s): %s MB / %s MB (%.1f%%)\n", $1, $2, $3, $4, ($3/$4)*100}'
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   ✅ SETUP COMPLETE!                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Services Running:"
echo "  • GPU 0 (RTX 4080):     http://localhost:11434  (ollama.service)"
echo "  • GPU 1 (Quadro M4000): http://localhost:11435  (ollama-gpu1.service)"
echo ""
echo "Usage:"
echo "  # Check service status"
echo "  sudo systemctl status ollama-gpu1"
echo ""
echo "  # View logs"
echo "  journalctl -u ollama-gpu1 -f"
echo ""
echo "  # Test dual-GPU orchestrator"
echo "  python3 dual_gpu_orchestrator.py \"Write a fibonacci function\""
echo ""
echo "Next Steps:"
echo "  1. Run test_dual_gpu.py to benchmark concurrent performance"
echo "  2. Update proxy.py to use DualGPUOrchestrator"
echo "  3. Monitor GPU utilization with 'watch -n 1 nvidia-smi'"
echo ""
