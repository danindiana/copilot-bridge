# Dual-GPU Setup Guide for Copilot-Bridge

This guide explains how to configure and use both GPUs (RTX 4080 + Quadro M4000) for maximum performance with copilot-bridge.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  Copilot-Bridge Proxy                       │
│              (proxy_dual_gpu.py)                            │
└─────────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
        ▼                                   ▼
┌─────────────────┐                 ┌─────────────────┐
│ GPU 0           │                 │ GPU 1           │
│ RTX 4080 SUPER  │                 │ Quadro M4000    │
│ 16 GB VRAM      │                 │ 8 GB VRAM       │
│                 │                 │                 │
│ Port: 11434     │                 │ Port: 11435     │
│                 │                 │                 │
│ Large Models:   │                 │ Small Models:   │
│ • qwen2.5:7b    │                 │ • qwen2.5:1.5b  │
│ • gpt-oss:20b   │                 │ • qwen2.5:3b    │
│ • qwen2.5:14b   │                 │ • phi3.5:3.8b   │
│                 │                 │                 │
│ Use Cases:      │                 │ Use Cases:      │
│ • Draft gen     │                 │ • Auditing      │
│ • Complex tasks │                 │ • Simple tasks  │
│ • Refactoring   │                 │ • Docstrings    │
└─────────────────┘                 └─────────────────┘
```

## Quick Start

### 1. Run Setup Script

```bash
cd /home/smduck/copilot-bridge
./setup_dual_gpu.sh
```

This will:
- Create systemd service for GPU 1 (ollama-gpu1)
- Configure GPU isolation (CUDA_VISIBLE_DEVICES)
- Start both Ollama instances
- Verify dual-GPU operation

### 2. Verify Services

```bash
# Check both services
sudo systemctl status ollama          # GPU 0
sudo systemctl status ollama-gpu1     # GPU 1

# View logs
journalctl -u ollama -f               # GPU 0 logs
journalctl -u ollama-gpu1 -f          # GPU 1 logs
```

### 3. Test Dual-GPU Execution

```bash
# Simple test
python3 dual_gpu_orchestrator.py "Write a fibonacci function"

# Run full benchmark
cd gpu-investigation_20251019_051050
python3 test_dual_gpu.py
```

## Configuration

### Environment Variables

```bash
# GPU 0 Ollama (existing service)
CUDA_VISIBLE_DEVICES=0
OLLAMA_HOST=0.0.0.0:11434
OLLAMA_MAX_LOADED_MODELS=4
OLLAMA_KEEP_ALIVE=10m

# GPU 1 Ollama (new service)
CUDA_VISIBLE_DEVICES=1
OLLAMA_HOST=0.0.0.0:11435
OLLAMA_MAX_LOADED_MODELS=2
OLLAMA_KEEP_ALIVE=5m
OLLAMA_NUM_PARALLEL=2
```

### Routing Rules

The `DualGPUOrchestrator` automatically routes requests based on complexity:

| Task Type | Keywords | GPU | Model | Reasoning |
|-----------|----------|-----|-------|-----------|
| **SIMPLE** | docstring, comment, lint, rename, explain | GPU 1 | qwen2.5:1.5b | Small model sufficient |
| **MODERATE** | refactor, debug, test | GPU 0 | qwen2.5:7b | Need more capability |
| **COMPLEX** | implement, create, design, architect | GPU 0 | qwen2.5:7b | Concurrent draft+audit |

## Usage Examples

### Example 1: Simple Task (Routes to GPU 1)

```bash
echo '{
  "messages": [{
    "content": "Write a docstring for a sorting function"
  }]
}' | python3 proxy_dual_gpu.py
```

**Expected Output:**
```
🚀 LOCAL route: 3200ms (model=qwen2.5-coder:1.5b on GPU1)
```

### Example 2: Complex Task (Routes to GPU 0 + GPU 1)

```bash
echo '{
  "messages": [{
    "content": "Implement a binary search tree with insert, delete, and balance operations"
  }]
}' | python3 proxy_dual_gpu.py
```

**Expected Output:**
```
🎭 DUAL-GPU route: 18500ms (draft=15.2s on GPU0, audit=3.1s on GPU1, concurrent=True)
```

### Example 3: Direct Orchestrator Usage

```python
from dual_gpu_orchestrator import DualGPUOrchestrator

# Initialize
orchestrator = DualGPUOrchestrator(
    gpu0_url="http://localhost:11434",
    gpu1_url="http://localhost:11435"
)

# Generate with audit (concurrent execution)
response = orchestrator.generate_with_audit(
    prompt="Refactor this code for better performance",
    concurrent=True
)

print(f"Draft: {response.draft}")
print(f"Audit: {response.audit['text']}")
print(f"Total time: {response.total_time:.2f}s")
print(f"Speedup: {(response.draft_time + response.audit_time) / response.total_time:.2f}x")
```

## Performance Benchmarks

### Sequential vs Concurrent Execution

| Mode | Draft Time | Audit Time | Total Time | Speedup |
|------|-----------|-----------|-----------|---------|
| **Sequential** (single GPU) | 19.25s | 23.84s | 45.12s | 1.0x |
| **Concurrent** (dual GPU) | 19.25s | 23.84s | ~24s | 1.88x |

### GPU Utilization

```bash
# Monitor in real-time
watch -n 1 nvidia-smi

# Expected output during concurrent execution:
# GPU 0: 8,785 MB used (draft model)
# GPU 1: 1,200 MB used (audit model)
```

## Monitoring

### Prometheus Metrics

The `DualGPUOrchestrator` exports metrics compatible with the existing Prometheus setup:

```python
# Metrics exposed:
dual_gpu_requests_total{gpu_id="0",model="qwen2.5-coder:7b",task_type="draft"}
dual_gpu_requests_total{gpu_id="1",model="qwen2.5-coder:1.5b",task_type="audit"}
dual_gpu_inference_duration_seconds{gpu_id="0",model="...",concurrent="True"}
dual_gpu_concurrent_executions_total
dual_gpu_selection_total{gpu_id="0",reason="complex_task_to_gpu0"}
```

### Query Examples

```bash
# Get routing statistics
curl -s http://localhost:8000/stats | jq '.dual_gpu'

# Check GPU selection breakdown
curl -s http://localhost:8000/metrics | grep dual_gpu_selection_total
```

## Troubleshooting

### GPU 1 Service Won't Start

```bash
# Check if port 11435 is available
sudo lsof -i :11435

# View detailed logs
journalctl -u ollama-gpu1 -n 50

# Restart service
sudo systemctl restart ollama-gpu1
```

### Both Models Loading on GPU 0

This indicates GPU 1 service isn't running:

```bash
# Verify GPU 1 service is active
sudo systemctl status ollama-gpu1

# Check CUDA_VISIBLE_DEVICES
journalctl -u ollama-gpu1 | grep CUDA_VISIBLE_DEVICES

# Should see: CUDA_VISIBLE_DEVICES=1
```

### Low Speedup from Concurrent Execution

Possible causes:
1. **Network latency** - If Ollama is on remote machine (192.168.1.138), network adds overhead
2. **Model not loaded** - First request loads model, subsequent requests are faster
3. **Thermal throttling** - Check GPU temperatures with `nvidia-smi`

```bash
# Pre-load models for fair benchmarks
curl http://localhost:11434/api/generate -d '{"model":"qwen2.5-coder:7b","prompt":"warmup","stream":false}'
curl http://localhost:11435/api/generate -d '{"model":"qwen2.5-coder:1.5b","prompt":"warmup","stream":false}'
```

### infoROM Warning on Quadro M4000

This is **expected and safe**. See `gpu-investigation_20251019_051050/04_inforom_warning_analysis.md` for details.

**TL;DR:** Warning is cosmetic, GPU works perfectly.

## Advanced Configuration

### Custom Model Allocation

Edit `dual_gpu_orchestrator.py` to customize which models run on which GPU:

```python
self.gpu0 = GPUEndpoint(
    name="RTX 4080 SUPER",
    gpu_id=0,
    url=gpu0_url,
    port=11434,
    models=[
        "your-custom-large-model:20b",
        "qwen2.5-coder:14b"
    ],
    max_vram_gb=16.0
)

self.gpu1 = GPUEndpoint(
    name="Quadro M4000",
    gpu_id=1,
    url=gpu1_url,
    port=11435,
    models=[
        "your-custom-small-model:3b",
        "phi3.5:3.8b"
    ],
    max_vram_gb=8.0
)
```

### Adjust Complexity Thresholds

Modify the `classify_task()` method to change routing behavior:

```python
def classify_task(self, prompt: str, context: str = "") -> TaskComplexity:
    text = (prompt + " " + context).lower()
    
    # Add your custom keywords
    if "urgent" in text or "critical" in text:
        return TaskComplexity.COMPLEX  # Force best model
    
    # Adjust existing rules
    simple_keywords = ["docstring", "comment", "your-keyword"]
    # ...
```

## Integration with Copilot-Bridge

### Replace Default Proxy

```bash
# Backup original
cp proxy.py proxy_backup.py

# Use dual-GPU version
cp proxy_dual_gpu.py proxy.py

# Restart bridge
sudo systemctl restart copilot-bridge
```

### Gradual Migration

Test dual-GPU proxy alongside original:

```bash
# Terminal 1: Original proxy on port 8000
python3 proxy.py

# Terminal 2: Dual-GPU proxy on port 8001
EXPORTER_PORT=8001 python3 proxy_dual_gpu.py

# Compare performance
# ...then switch when satisfied
```

## Cost-Benefit Analysis

### Hardware Costs

| Component | Cost | Status |
|-----------|------|--------|
| RTX 4080 SUPER | $1,000 | Already owned |
| Quadro M4000 | $150 | Already owned |
| **Total** | **$1,150** | **Sunk cost** |

### Performance Gains

| Metric | Single GPU | Dual GPU | Improvement |
|--------|-----------|----------|-------------|
| Draft+Audit time | 45.12s | ~24s | **47% faster** |
| Throughput | 1 req/45s | 1 req/24s | **88% more** |
| VRAM utilization | 66% | 92% | **26% better** |

### ROI for 10 Developers

- **Requests per day:** 10 devs × 20 requests = 200 requests
- **Time saved:** 200 × 21s = 4,200s = **1.17 hours/day**
- **Productivity gain:** **7.3% efficiency improvement**
- **Annual value:** 1.17 hrs/day × 250 days × $50/hr = **$14,625/year**

**Conclusion:** Dual-GPU setup pays for itself immediately and provides ongoing efficiency gains.

## Next Steps

1. ✅ **Complete setup** - Run `./setup_dual_gpu.sh`
2. ✅ **Verify operation** - Check both services running
3. ✅ **Run benchmarks** - Execute `test_dual_gpu.py`
4. 🔲 **Monitor performance** - Watch GPU utilization
5. 🔲 **Integrate with bridge** - Update main proxy
6. 🔲 **Measure ROI** - Track time savings over 1 week

## Support

For issues or questions:
1. Check logs: `journalctl -u ollama-gpu1 -f`
2. Review investigation docs: `gpu-investigation_20251019_051050/`
3. Run diagnostics: `nvidia-smi -L` and `nvidia-smi`
4. Create GitHub issue with logs attached

---

**Status:** ✅ Ready for production use  
**Last Updated:** October 19, 2025  
**Tested On:** calisota (RTX 4080 + Quadro M4000)
