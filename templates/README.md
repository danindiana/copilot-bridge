# Context Templates

## Purpose
Pre-built context templates for maximizing local AI output quality.

**Key Insight**: Context is free when you own the hardware—use it ruthlessly.

---

## Available Templates

### `proven_600word_context.txt` ✅ Validated
**Stats**: 595 words, 138 lines, 4079 chars, ~774 tokens  
**Performance**: 
- Generation time: 3.7s (24% faster than minimal context)
- Output quality: 9/10 (professional publication-grade)
- Proven with gpt-oss:20b on project summary task

**Contents**:
- Project statistics (files, lines, commits)
- Technical architecture (models, routing logic)
- Feature demonstrations (all 8 demos with timing)
- Integration success metrics
- Cost analysis and achievements

**Use Cases**:
- Executive summaries
- Project README generation
- Technical blog posts
- Documentation synthesis
- Investor pitches

**Usage**:
```python
context = open('templates/proven_600word_context.txt').read()
prompt = f"{context}\n\nTask: {your_specific_request}"
# Feed to local model → get professional output
```

---

## Template Design Principles

### 1. **Specificity Over Brevity**
❌ "We have 8 demos"  
✅ "8 interactive demonstrations: Google-style docstring generation (3s), algorithm explanation with complexity analysis (5s), TCP vs UDP Q&A (16s)..."

### 2. **Metrics, Not Claims**
❌ "Fast performance"  
✅ "3-5 second latency, 70% local handling, $0.00 per request"

### 3. **Structure for Skimming**
```
PROJECT CONTEXT:
  - Stats first (numbers grab attention)
  - Tech stack (models, tools)

TECHNICAL ARCHITECTURE:
  - Components (proxy, models, routing)
  - Decision logic (keywords, fallback)

DEMONSTRATIONS:
  - Each demo with timing
  - Actual outputs (proof)

RESULTS:
  - Metrics (cost, speed, quality)
  - Business value (savings, security)
```

### 4. **Show, Don't Tell**
Include actual outputs, git logs, timing metrics—not vague descriptions.

---

## Creating New Templates

### Context Gathering Checklist

**Project Info** (30 words):
- [ ] Name, purpose, one-line description
- [ ] Repository stats (files, lines, commits)
- [ ] Tech stack (languages, frameworks, models)

**Architecture** (100 words):
- [ ] System components (services, modules)
- [ ] Data flow (inputs → processing → outputs)
- [ ] Key design decisions (why this approach?)

**Features** (200 words):
- [ ] Core capabilities (what can it do?)
- [ ] Demo scenarios (concrete examples)
- [ ] Timing metrics (performance proof)

**Results** (100 words):
- [ ] Success metrics (uptime, accuracy, speed)
- [ ] Cost analysis (vs alternatives)
- [ ] Business impact (savings, productivity)

**Next Steps** (50 words):
- [ ] Future enhancements
- [ ] Integration opportunities
- [ ] Scaling considerations

**Total**: ~480 words (sweet spot for quality/speed tradeoff)

### Template Validation Process

1. **Baseline Test**: Run with minimal context (100 words)
   - Measure: generation time, output length, quality score
   
2. **Enhanced Test**: Run with your template (400-600 words)
   - Measure: same metrics
   - Compare: should see quality ↑, time ↓ or ≈

3. **Quality Check**:
   - [ ] Specific details (model names, exact metrics)?
   - [ ] Professional tone (suitable for external use)?
   - [ ] Actionable insights (not just description)?
   
4. **Iterate**: If quality < 7/10, add more specifics and re-test

---

## Context Size Guidelines

Based on empirical testing with gpt-oss:20b (4096 token context):

| Context Size | Use Case | Expected Quality | Notes |
|--------------|----------|------------------|-------|
| 100 words | Quick iterations | 3/10 | Generic, needs retry |
| **600 words** | **Standard** | **9/10** | **Sweet spot** ✅ |
| 1,000 words | Complex projects | 9-10/10 | Diminishing returns |
| 5,000 words | Whitepaper generation | Unknown | Needs testing |
| 10,000 words | Full codebase context | Unknown | May exceed limits |

**Rule of thumb**: Start at 500-700 words for most tasks.

---

## Quality Metrics

### How to Score Output (1-10)

**1-3 (Poor)**: Generic, could apply to any project, no specifics  
**4-6 (Mediocre)**: Some details, but vague, needs significant editing  
**7-8 (Good)**: Specific, professional, minor edits needed  
**9-10 (Excellent)**: Publication-ready, insightful, no edits needed

### Example Comparisons

**3/10 Output** (minimal context):
> "This project is a coding assistant that uses AI models. It saves costs by using local inference."

**9/10 Output** (rich context):
> "Copilot Bridge routes 70% of routine tasks to qwen2.5-coder:7b-instruct-q8_0 locally (3-5s, $0), while deferring complex refactoring to cloud APIs, achieving 70-80% cost reduction vs all-cloud approaches."

**The difference**: Specific models, exact percentages, concrete timing, clear value prop.

---

## Template Library Goals

### Short-term (Next Week)
- [x] `proven_600word_context.txt` - Project summary template
- [ ] `codebase_architecture_context.txt` - For explaining system design
- [ ] `api_documentation_context.txt` - For generating API docs
- [ ] `troubleshooting_context.txt` - For debugging help

### Medium-term (Next Month)
- [ ] Domain-specific templates (web, data, ML)
- [ ] Task-specific templates (refactoring, testing, documentation)
- [ ] Integration templates (VS Code snippets, CLI tools)

### Long-term (Next Quarter)
- [ ] Auto-generate templates from project structure
- [ ] Context optimization tools (find minimal effective size)
- [ ] Quality prediction (estimate output score from context)

---

## Best Practices

### DO:
✅ Include exact metrics, model names, timings  
✅ Show actual outputs/results (proof over claims)  
✅ Structure with headers (easy to skim)  
✅ Update templates as project evolves  
✅ Test each template before committing  

### DON'T:
❌ Use vague language ("fast", "efficient", "powerful")  
❌ Skip metrics (readers want numbers)  
❌ Write walls of text (use bullet points)  
❌ Copy-paste without adapting to your project  
❌ Forget to validate quality improvement  

---

## Contributing

Found a great template? Share it!

1. Test with your local model (before/after comparison)
2. Document quality improvement (X/10 → Y/10)
3. Measure generation time (should be ≈ or faster)
4. Add to `/templates/` with descriptive name
5. Update this README with stats

---

## References

- See `CONTEXT_EXPERIMENT.md` for full methodology
- See `LESSONS_LEARNED.md` for strategic implications
- See `generate_improved_summary.py` for usage example

---

**Remember**: Context is free on local hardware. Use it ruthlessly. 🚀
