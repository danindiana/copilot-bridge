# Frequently Asked Questions (FAQ)

## General Questions

### What is Copilot Bridge?

Copilot Bridge is a hybrid AI routing system that intelligently directs coding requests between local Ollama models (free, fast, private) and cloud services (expensive, powerful). It saves 70-90% of AI coding costs by routing simple tasks locally while sending complex tasks to the cloud.

### Why should I use this instead of just GitHub Copilot?

**Cost savings**: $40/developer/month at 90% local routing  
**Privacy**: 70-90% of your code never leaves your network  
**Speed**: Local inference is often faster (3-5s vs 8-10s cloud)  
**Vendor independence**: No lock-in to GitHub/OpenAI  
**Learning**: Understand how AI coding assistance actually works

### Is this production-ready?

Yes! Version 1.0.0 includes:
- Tested routing logic (proxy_instrumented.py)
- KPI instrumentation (Prometheus metrics)
- Meta-reasoning quality audit (R&G)
- Comprehensive documentation
- 14 commits of iterative development

## Technical Questions

### What hardware do I need?

**Minimum:**
- NVIDIA GPU with 8GB VRAM (e.g., RTX 3060, RTX 4060)
- 16GB system RAM
- 50GB disk space for models

**Recommended:**
- NVIDIA RTX 4080 (16GB VRAM) - our benchmark hardware
- 32GB system RAM
- 100GB SSD for models

**Cloud alternative:** Run Ollama on a cloud VM with GPU (AWS g4dn, GCP T4, etc.)

### What models does it use?

**Primary coding:**
- `qwen2.5-coder:7b-instruct-q8_0` (8.1 GB) - main workhorse

**Chat/edit:**
- `llama3.1:8b` (4.9 GB) - general purpose

**Advanced tasks:**
- `gpt-oss:20b` (13 GB) - meta-reasoning, summaries

**Autocomplete:**
- `qwen2.5-coder:1.5b-base` (986 MB) - fast completions

**Embeddings:**
- `nomic-embed-text` (274 MB) - semantic search

### Can I use other models?

Yes! Edit `proxy_instrumented.py` and change the model names:

```python
# In route_request() function
model = "your-model-name"  # e.g., "codellama:13b"
```

Any Ollama-compatible model works.

### Can I use cloud models for everything?

Yes, but you lose the cost savings. To force cloud routing:

```python
# In proxy_instrumented.py, comment out LOCAL_KEYWORDS
LOCAL_KEYWORDS = []  # Routes everything to cloud
```

## Architecture Questions

### Why remove Continue.dev?

Continue.dev was useful for initial smoke testing but adds **no value** in production:

**Problems:**
- Middleware overhead (200-500ms routing latency)
- Black box (no instrumentation access)
- Config complexity (YAML/JSON hell)
- No meta-reasoning support

**Our approach:**
- Direct Ollama API calls (<10ms latency)
- Full observability (JSON logs → Prometheus)
- Pure Python (no external config)
- Supports R&G two-stage pipeline

**Result:** 98% faster routing with complete control.

See [ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md) for full rationale.

### What is "context beats compute"?

Our **empirical finding**: Same 20B model, same hardware, different context sizes:

| Context Size | Output | Time | Quality |
|--------------|--------|------|---------|
| 116 words    | 280w   | 4.9s | 3/10 😞 |
| 654 words (5.6× more) | 262w | 3.7s | 9/10 🎉 |

**Result:** Richer context → 24% faster + dramatically better quality

**Why?** Model confidence increases with context, reducing sampling uncertainty.

**Implication:** Don't need bigger models, need better prompts (when inference is free).

See [CONTEXT_EXPERIMENT.md](CONTEXT_EXPERIMENT.md) for full methodology.

### What is meta-reasoning (R&G)?

**Rosencrantz & Guildenstern** is a two-stage quality audit:

1. **Stage 1:** Large model (gpt-oss:20b) generates draft
2. **Stage 2:** Small model (qwen:7b) audits the draft

**Audit provides:**
- Quality scores (relevance, structure, specificity, actionability)
- Hallucination risk assessment
- Strengths and weaknesses
- Counterfactuals (alternative perspectives)
- Recommendation: ship / revise / regenerate

**Time overhead:** Only 14% (audit: ~8s vs generation: ~90s)

**Value:** Catches poor outputs before you ship them.

See [META_REASONING.md](META_REASONING.md) for details.

## Cost & Savings Questions

### How much does this actually save?

**10 developers, M6 projection (90% local):**

| Scenario | Monthly Cost | Annual Cost |
|----------|--------------|-------------|
| All cloud (baseline) | $440 | $5,280 |
| With Copilot Bridge | $44 | **$528** |
| **Savings** | **$396/month** | **$4,752/year** |

**ROI:** 3-month payback on $1,200 GPU investment.

See [TOKEN_SAVINGS_ROADMAP.md](TOKEN_SAVINGS_ROADMAP.md) for month-by-month plan.

### What's the electricity cost?

**RTX 4080 running 8 hours/day:**
- Power draw: ~250W under load
- Daily usage: 2 kWh
- Monthly cost: ~$6 (at $0.10/kWh)

**Net savings:** $396 - $6 = **$390/month** after electricity.

### Do I still need GitHub Copilot subscription?

**Two options:**

1. **Hybrid (recommended):** Keep Copilot for complex tasks, route simple tasks locally
   - Savings: 70-90% cost reduction
   - Best of both worlds

2. **Local only:** Cancel Copilot, use local models exclusively
   - Savings: 100% cost reduction
   - Slight quality trade-off on complex tasks

## Setup & Usage Questions

### How long does setup take?

**5 minutes** if you follow [QUICKSTART.md](QUICKSTART.md):

1. Install Ollama (1 min)
2. Pull models (2 min with fast connection)
3. Clone repo + install deps (1 min)
4. Run demo (1 min)

### Do I need to run anything in the background?

**For basic usage:** No, just run demos directly

**For KPI dashboard:**
```bash
python3 exporter.py &  # Background metrics exporter
docker-compose up -d   # Prometheus + Grafana stack
```

### How do I know it's working?

Run the interactive demo:

```bash
cd examples
python3 demo_showcase.py
```

Select any demo (e.g., #7 Type Hints). If you see output in 3-5 seconds with cost $0.00, it's working!

### Can I use this in VS Code?

**Current state:** No direct VS Code integration (we removed Continue.dev)

**Workaround options:**
1. Run demos in integrated terminal
2. Copy-paste code to/from demo scripts
3. Build custom VS Code extension using our routing logic

**Future:** VS Code extension planned for v1.1.0

## Performance Questions

### How fast are local models?

**Typical latency** (RTX 4080):
- Docstrings: 2-3s
- Type hints: 3-4s
- Code explanation: 4-6s
- Refactoring: 5-8s
- Q&A: 10-20s
- Meta-reasoning: 90-120s (large model)

**vs Cloud:** Similar or better (no network latency)

### What if local model is too slow?

**Options:**

1. **Use smaller model:**
   ```bash
   ollama pull qwen2.5-coder:1.5b  # Faster, lower quality
   ```

2. **Upgrade GPU:** RTX 4090 is ~40% faster than 4080

3. **Route to cloud:** Edit LOCAL_KEYWORDS to exclude slow tasks

4. **Use quantization:** Already using q8_0 (8-bit), could try q4 (4-bit) for 2× speed

### Can I run multiple models simultaneously?

Yes, but **memory limits apply:**

RTX 4080 (16GB VRAM) can hold:
- qwen:7b (8 GB) + llama3.1:8b (5 GB) = 13 GB ✅
- gpt-oss:20b (13 GB) alone ✅
- All 3 at once = 26 GB ❌ (exceeds VRAM)

Ollama automatically loads/unloads models as needed.

## Troubleshooting

### "Connection refused" when running demos

**Cause:** Ollama not running

**Fix:**
```bash
# Check if Ollama is running
ollama list

# If not, start it
ollama serve
```

### "Model not found" error

**Cause:** Model not downloaded

**Fix:**
```bash
ollama pull qwen2.5-coder:7b-instruct-q8_0
ollama pull llama3.1:8b
```

### Python import errors

**Cause:** Missing dependencies

**Fix:**
```bash
pip install -r requirements.txt
```

### Demos hang or timeout

**Cause:** Model taking too long (possibly CPU mode)

**Fix:**
```bash
# Verify GPU is detected
ollama list  # Should show models
nvidia-smi   # Should show GPU utilization when running

# If CPU mode, check CUDA installation
python3 -c "import torch; print(torch.cuda.is_available())"
```

### Quality is poor compared to Copilot

**Cause:** Insufficient context

**Fix:** See [CONTEXT_EXPERIMENT.md](CONTEXT_EXPERIMENT.md) - provide richer prompts:
- Include surrounding code
- Add comments explaining intent
- Specify constraints and requirements
- Provide examples of desired output

**Remember:** Context beats compute when inference is free.

## Contributing Questions

### How can I contribute?

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Bug reporting guidelines
- Development setup
- Code style (PEP 8, type hints, docstrings)
- Pull request process
- Testing expectations

**High-priority contributions:**
- Additional refactoring test samples
- Performance optimizations
- VS Code extension
- Web UI for R&G audits
- Documentation improvements

### I found a bug, what should I do?

1. **Check GitHub Issues:** Might already be reported
2. **Create issue** with:
   - Python version
   - Ollama version
   - Operating system
   - Steps to reproduce
   - Error messages / stack traces

### Can I use this commercially?

**Yes!** MIT License is permissive:
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use

**Only requirement:** Include MIT license text in distributions.

## Philosophy Questions

### Why local AI instead of cloud?

**Economic inversion:**

**Cloud:** Pay per token → incentive to minimize context → weak prompts → poor quality

**Local:** $0 per token → incentive to maximize context → rich prompts → excellent quality

This is **structural arbitrage**, not marginal improvement.

### What's the long-term vision?

**v1.0:** Hybrid routing (current)  
**v1.1:** PyPI package, Docker image, web UI  
**v2.0:** Adaptive routing based on quality scores  
**v3.0:** Full enterprise deployment (K8s, Helm, SLAs)

**Ultimate goal:** Prove that owning your AI infrastructure is more cost-effective, private, and performant than cloud-only approaches.

### Is this just for hobbyists?

**No!** Production use cases:

- **Startups:** Flatten cloud bills while scaling
- **Enterprises:** Meet data residency requirements
- **Consulting firms:** No vendor lock-in, portable
- **Research labs:** Reproducible, auditable AI
- **Solo devs:** Learn how AI really works

**CFO-approved:** See [CFO_EMAIL_TEMPLATE.md](CFO_EMAIL_TEMPLATE.md) for business case.

---

## Still have questions?

- **GitHub Discussions:** https://github.com/yourusername/copilot-bridge/discussions
- **GitHub Issues:** https://github.com/yourusername/copilot-bridge/issues
- **Documentation:** [README.md](README.md), [QUICKSTART.md](QUICKSTART.md), [LESSONS_LEARNED.md](LESSONS_LEARNED.md)

---

**Built with ❤️ to answer: "Can local AI really replace cloud services?" (Spoiler: Yes, for 70-90% of tasks!)**
