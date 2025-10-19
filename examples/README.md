# Examples Directory

This directory contains example scripts demonstrating various Copilot Bridge features.

## 🎯 Interactive Demos

### `demo_showcase.py`
**8 interactive demonstrations** of local AI capabilities:

```bash
python3 demo_showcase.py
```

Demos included:
1. **Generate Documentation** - Google-style docstrings (~3s, $0.00)
2. **Code Explanation** - Algorithm analysis with complexity (~5s, $0.00)
3. **Text Summarization** - Condense technical content (~4s, $0.00)
4. **Question & Answer** - Technical concepts (TCP vs UDP) (~16s, $0.00)
5. **Code Generation** - Binary search implementation (~7s, $0.00)
6. **Bug Detection** - Find issues in code (~5s, $0.00)
7. **Add Type Hints** - Python type annotations (~3s, $0.00)
8. **Code Refactoring** - Pythonic improvements (~6s, $0.00)

**Key Features:**
- Real-time timing measurement
- Cost comparison (local $0.00 vs cloud ~$0.02-0.05)
- Copy-paste friendly output
- No API keys required

---

### `rosencrantz_guildenstern.py`
**Meta-reasoning quality audit** - Two-stage pipeline where a small model critiques the large model's output:

```bash
python3 rosencrantz_guildenstern.py
```

**How it works:**
1. **Stage 1**: Large model (gpt-oss:20b) generates draft response
2. **Stage 2**: Small model (qwen2.5-coder:7b) audits the draft

**Output includes:**
- Quality scores (relevance, structure, specificity, actionability)
- Hallucination risk assessment
- Strengths and weaknesses
- Counterfactuals (alternative perspectives)
- Recommendation: ship / revise / regenerate

**Example Test Cases:**
- Code explanation (Python GIL)
- Architecture decision (microservices vs monolith)
- Refactoring advice

**Time overhead:** Only 14% (audit: ~8s vs generation: ~90s)

---

### `generate_mega_summary_32k.py`
**Large context window experiment** - Generate comprehensive summary using gpt-oss:20b with 32K context:

```bash
python3 generate_mega_summary_32k.py
```

**What it does:**
- Feeds entire project context (~1,500 words) to gpt-oss:20b
- Uses full 32,768 token context window
- Generates executive-level summary
- Saves output to `MEGA_SUMMARY_32K_YYYYMMDD_HHMMSS.md`

**Key insight:** Demonstrates that larger context → better quality synthesis (not just expansion)

**Expected time:** 60-120 seconds (large context processing)

---

### `demo_local_only.py`
**Simple LOCAL-only proof of concept** - Basic version without GitHub token:

```bash
./demo_local_only.py
```

**Use case:** Quick smoke test to verify Ollama connectivity

---

## 🚀 Quick Start

### Prerequisites

1. **Ollama running** with models:
   ```bash
   ollama pull qwen2.5-coder:7b-instruct-q8_0
   ollama pull llama3.1:8b
   ollama pull gpt-oss:20b  # For meta-reasoning
   ```

2. **Python dependencies**:
   ```bash
   cd ..
   pip install -r requirements.txt
   ```

### Run Examples

**Interactive demos:**
```bash
python3 demo_showcase.py
# Select demo 1-8 from menu
```

**Meta-reasoning audit:**
```bash
python3 rosencrantz_guildenstern.py
# Select test case or enter custom prompt
```

**Large context summary:**
```bash
python3 generate_mega_summary_32k.py
# Confirm to feed ~1,500 words to model
```

---

## 📊 Example Outputs

### Demo Showcase Output
```
╔════════════════════════════════════════════════════════╗
║              LOCAL AI CODING DEMOS                     ║
╚════════════════════════════════════════════════════════╝

DEMO #7: Add Type Hints
═══════════════════════════════════════════════════════════

Original Code:
def calculate_total(items, tax_rate):
    subtotal = sum(item['price'] for item in items)
    return subtotal * (1 + tax_rate)

✅ Enhanced with type hints in 3.2 seconds
💰 Cost: $0.00 (vs $0.02 cloud)

Result:
from typing import List, Dict

def calculate_total(
    items: List[Dict[str, float]], 
    tax_rate: float
) -> float:
    subtotal = sum(item['price'] for item in items)
    return subtotal * (1 + tax_rate)
```

### Meta-Reasoning Output
```
╔════════════════════════════════════════════════════════╗
║        META-REASONING AUDIT REPORT                     ║
╚════════════════════════════════════════════════════════╝

📊 QUALITY SCORES:
   • Relevance:      8.5/10
   • Structure:      9.0/10
   • Specificity:    7.0/10
   • Actionability:  8.0/10
   • Overall:        8.2/10

🎯 HALLUCINATION RISK: ✅ LOW

✅ STRENGTHS:
   • Clear structure with examples
   • Good balance of theory and practice
   • Actionable recommendations

⚠️  WEAKNESSES:
   • Could be more specific on edge cases
   • Missing performance considerations

🔄 COUNTERFACTUALS:
   • Alternative: Consider async approach
   • Missing: Security implications

💡 RECOMMENDATION: 🚀 SHIP
```

---

## 🎓 Learning Path

**Beginner:** Start with `demo_showcase.py`
- See what local models can do
- Get comfortable with Ollama
- Understand routing benefits

**Intermediate:** Try `rosencrantz_guildenstern.py`
- Learn meta-reasoning concept
- See quality audit in action
- Understand strengths/weaknesses analysis

**Advanced:** Experiment with `generate_mega_summary_32k.py`
- Test large context windows
- See synthesis vs expansion
- Validate "context beats compute" principle

---

## 🔗 Related Documentation

- **[../README.md](../README.md)** - Project overview
- **[../QUICKSTART.md](../QUICKSTART.md)** - Setup guide
- **[../META_REASONING.md](../META_REASONING.md)** - R&G deep dive
- **[../CONTEXT_EXPERIMENT.md](../CONTEXT_EXPERIMENT.md)** - Scientific methodology
- **[../LESSONS_LEARNED.md](../LESSONS_LEARNED.md)** - Strategic insights

---

## 💡 Tips

- **Timing varies** based on hardware (RTX 4080 benchmarks)
- **Cost is always $0.00** for local inference
- **Quality improves** with richer context (see CONTEXT_EXPERIMENT.md)
- **Meta-reasoning** catches hallucinations before you ship
- **Interactive mode** is best for learning

---

**Built with ❤️ to demonstrate that local AI is fast, free, and high-quality.**
