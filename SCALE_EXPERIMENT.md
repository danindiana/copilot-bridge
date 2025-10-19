# Scale Experiment: Quality vs Context Size

## Objective
Map the **quality-vs-context efficiency frontier** for local AI models.

**Goal**: Find optimal context size for different task types.

---

## Experimental Design

### Model Configuration
- **Model**: gpt-oss:20b (20.9B parameters, MXFP4)
- **Max Context**: 131,072 tokens
- **Active Context**: 4,096 tokens
- **Task**: Generate executive summary of copilot-bridge project

### Test Matrix

| Test # | Context Size | Est. Tokens | Expected Quality | Expected Time |
|--------|--------------|-------------|------------------|---------------|
| 1 (baseline) | 116 words | ~150 | 3/10 | 4.9s ✅ DONE |
| 2 (proven) | 654 words | ~850 | 9/10 | 3.7s ✅ DONE |
| 3 | 1,000 words | ~1,300 | 9-10/10 | 3-4s (predicted) |
| 4 | 2,500 words | ~3,250 | 10/10 | 4-5s (predicted) |
| 5 | 5,000 words | ~6,500 | 10/10 | 6-8s (predicted) |
| 6 | 10,000 words | ~13,000 | 10/10 or plateau | 10-15s (predicted) |

### Context Sources

**1,000 words** (Test #3):
- All current content from proven_600word_context.txt (595 words)
- + Detailed code snippets from proxy.py and examples/demo_showcase.py (~400 words)
- Focus: Architecture + implementation details

**2,500 words** (Test #4):
- Above + full git log with commit messages (~300 words)
- + Complete demo outputs (all 8 scenarios) (~800 words)
- + Detailed integration steps and troubleshooting (~800 words)
- Focus: Complete project lifecycle

**5,000 words** (Test #5):
- Above + full content of all markdown documentation files (~2,000 words)
- + Comparative analysis vs cloud services (~500 words)
- Focus: Business case + technical depth

**10,000 words** (Test #6):
- Above + full source code of key files (~3,000 words)
- + Extended use cases and future roadmap (~2,000 words)
- Focus: Everything (stress test context limits)

---

## Metrics to Track

### Quantitative
- **Generation Time**: Seconds from request to completion
- **Input Size**: Words, characters, estimated tokens
- **Output Size**: Words, characters, estimated tokens
- **Compression Ratio**: Output words / Input words

### Qualitative (Scored 1-10)
- **Technical Accuracy**: Correct model names, metrics, architecture
- **Specificity**: Concrete examples vs vague statements
- **Business Insight**: Cost analysis, value proposition, competitive advantage
- **Readability**: Professional tone, clear structure, engaging prose
- **Actionability**: Practical next steps, clear recommendations

### Overall Quality Score (1-10)
Average of the 5 qualitative metrics.

---

## Hypothesis

### Expected Curve Shape

```
Quality
10 |                    ╭───────────────  (plateau)
 9 |              ╭─────╯
 8 |          ╭───╯
 7 |      ╭───╯
 6 |  ╭───╯
 5 | ╱
 4 |╱
 3 ╱
 2 |
 1 |
   └──────────────────────────────────────> Context Size
   0      1K     2K     3K     4K     5K+    (words)
   
   ZONES:
   • 0-500:   Steep gains (high ROI)
   • 500-2K:  Diminishing returns
   • 2K-5K:   Plateau (marginal gains)
   • 5K+:     Potential decline (information overload?)
```

### Predictions

1. **Sweet Spot**: 600-1,500 words
   - Enough detail for specificity
   - Fast enough for production use (3-5s)
   - Quality: 8-10/10

2. **Diminishing Returns**: 1,500-3,000 words
   - Marginal quality improvement
   - Slower generation (5-8s)
   - May not justify extra effort

3. **Plateau or Decline**: 3,000+ words
   - No quality improvement (model can't utilize excess)
   - Slower generation (8-15s)
   - Risk of information overload (model loses focus)

4. **Context Limit**: ~4,000 tokens (~3,000 words)
   - Hard limit of active context window
   - Beyond this: truncation or error

---

## Success Criteria

### Experiment is successful if we can:
1. ✅ Plot a clear quality-vs-size curve
2. ✅ Identify optimal context range for this model
3. ✅ Quantify diminishing returns threshold
4. ✅ Provide actionable guidance (e.g., "use 600-1,000 words for summaries")

### Bonus findings:
- Speed paradox holds at larger sizes (more context = faster?)
- Synthesis ratio changes with size (compression vs expansion)
- Specific context types matter (code vs docs vs metrics)

---

## Implementation Plan

### Phase 1: Context Preparation (1 hour)
- [ ] Create 1,000-word context file
- [ ] Create 2,500-word context file
- [ ] Create 5,000-word context file
- [ ] Create 10,000-word context file
- [ ] Validate all files (word count, structure)

### Phase 2: Experiment Execution (2 hours)
- [ ] Run Test #3 (1,000 words)
- [ ] Run Test #4 (2,500 words)
- [ ] Run Test #5 (5,000 words)
- [ ] Run Test #6 (10,000 words)
- [ ] Record all metrics (time, size, output)

### Phase 3: Quality Evaluation (1 hour)
- [ ] Score all outputs (1-10 across 5 dimensions)
- [ ] Calculate overall quality scores
- [ ] Compare outputs side-by-side
- [ ] Identify patterns and insights

### Phase 4: Analysis & Visualization (2 hours)
- [ ] Plot quality vs context size curve
- [ ] Plot generation time vs context size
- [ ] Calculate efficiency metrics (quality per second)
- [ ] Write findings and recommendations
- [ ] Create shareable graphs (PNG/SVG)

### Phase 5: Documentation (1 hour)
- [ ] Update SCALE_EXPERIMENT.md with results
- [ ] Create EFFICIENCY_FRONTIER.md with graphs
- [ ] Update README.md with key findings
- [ ] Commit all results to git

**Total Effort**: 6-7 hours

---

## Deliverables

### 1. SCALE_EXPERIMENT_RESULTS.md
- Complete methodology
- All raw data (inputs, outputs, timings)
- Quality scores with justifications
- Comparative analysis

### 2. EFFICIENCY_FRONTIER.png
- Quality vs Context Size graph
- Generation Time vs Context Size graph
- Quality per Second (efficiency) graph
- Annotated with recommendations

### 3. Updated Templates
- Optimal context templates for different tasks:
  - `template_summary_optimal.txt` (sweet spot size)
  - `template_documentation_extended.txt` (if larger is better)
  - `template_quick_wins.txt` (minimal but effective)

### 4. RECOMMENDATIONS.md
- Task-based guidance (e.g., "For X task, use Y words")
- Model-specific insights (gpt-oss:20b optimal range)
- Cost-benefit analysis (time vs quality tradeoffs)

---

## Risk Assessment

### Low Risk
- Running experiments (non-destructive, reproducible)
- Time investment (6-7 hours, contained)
- Cost ($0, local inference)

### Medium Risk
- Context limits (may hit 4096 token ceiling)
  - Mitigation: Test incrementally, stop if errors
- Quality scoring (subjective)
  - Mitigation: Use rubric, multiple dimensions, examples

### High Risk
- None identified

---

## Expected Impact

### Internal Value
- Data-driven context sizing (stop guessing)
- Optimal templates for production use
- Efficiency benchmarks for future models

### External Value
- Open-source research (first of its kind?)
- Visual proof (graph beats wall of text)
- Citeable reference for community

### Marketing Value
- "We plotted the curve so you don't have to"
- Thought leadership positioning
- v1.0.0 release centerpiece

---

## Timeline

**If starting today:**
- Hour 1-2: Context preparation
- Hour 3-4: Run experiments
- Hour 5: Quality evaluation
- Hour 6-7: Analysis + graphs
- Hour 8: Documentation

**Total**: 1 day of focused work

**Alternative**: Spread over 2-3 days (2-3 hours/day)

---

## Next Steps

Ready to execute? Options:

**A. Full Protocol** (6-7 hours)
- Run all 4 new tests (1K, 2.5K, 5K, 10K)
- Complete analysis and graphing
- Publish findings in v1.0.0

**B. Incremental** (2-3 hours)
- Run Test #3 (1,000 words) only
- Validate hypothesis (does quality improve?)
- Decide whether to continue based on results

**C. Hybrid** (4-5 hours)
- Run Tests #3 and #4 (1K, 2.5K)
- Plot partial curve
- Extrapolate remaining points if pattern is clear

---

## Conclusion

This experiment transforms anecdotal evidence ("more context seems better") into **quantitative science** ("600-1,000 words is optimal for summaries").

The efficiency frontier graph becomes the **visual proof** that context beats compute.

**Ready when you are.** 🚀
