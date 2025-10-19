# Meta-Reasoning: Rosencrantz & Guildenstern

**Two-stage local inference with quality audit**

## Concept

Named after Shakespeare's characters who observe and comment on the main action, this module implements a two-stage AI pipeline:

1. **Large Model (Hamlet)**: Generates initial draft response
2. **Small Model (R&G)**: Audits the draft with meta-commentary

The auditor provides objective quality scores and recommendations without regenerating the content.

## Architecture

```
User Prompt + Context
        ↓
┌───────────────────────────────────────┐
│  STAGE 1: LARGE MODEL GENERATION     │
│  Model: gpt-oss:20b                  │
│  Context: 32K tokens                 │
│  Time: ~60-90s                       │
│  Output: Draft response              │
└───────────────────────────────────────┘
        ↓
┌───────────────────────────────────────┐
│  STAGE 2: SMALL MODEL AUDIT          │
│  Model: qwen2.5-coder:7b             │
│  Context: 8K tokens                  │
│  Time: ~5-10s                        │
│  Output: Quality audit + scores      │
└───────────────────────────────────────┘
        ↓
    Final Result:
    • Draft text
    • Quality scores (0-10)
    • Strengths/Weaknesses
    • Counterfactuals
    • Recommendation
```

## Quality Dimensions

The audit model scores five dimensions:

1. **Relevance** (30% weight): How well does it answer the prompt?
2. **Structure** (20% weight): Is it well-organized and clear?
3. **Specificity** (20% weight): Concrete details vs vague generalities?
4. **Actionability** (30% weight): Can the user act on this information?
5. **Hallucination Risk**: Low / Medium / High - unsupported claims?

**Overall Quality** = Weighted average of scores 1-4

## Output Format

```json
{
  "relevance_score": 8.5,
  "structure_score": 9.0,
  "specificity_score": 7.0,
  "actionability_score": 8.0,
  "hallucination_risk": "low",
  "strengths": [
    "Clear structure with numbered steps",
    "Good real-world examples",
    "Actionable recommendations"
  ],
  "weaknesses": [
    "Could be more specific on edge cases",
    "Missing performance considerations"
  ],
  "counterfactuals": [
    "Alternative: Could consider async approach instead",
    "Missing perspective: Security implications not addressed"
  ],
  "overall_quality": 8.2,
  "recommendation": "ship"
}
```

## Recommendations

- **ship** (≥8.0 overall, low hallucination): High quality, ready to use
- **revise** (6.0-7.9 overall): Good but improvable
- **regenerate** (<6.0 overall): Below threshold, try again with more context
- **manual_review**: Parsing error, human review needed

## Usage

### Interactive Demo

```bash
cd ~/copilot-bridge
python3 rosencrantz_guildenstern.py
```

Choose from example prompts or enter your own. The system will:
1. Generate draft with large model
2. Audit with small model
3. Display scores, strengths, weaknesses, counterfactuals
4. Provide recommendation

### Programmatic Usage

```python
from rosencrantz_guildenstern import RosencrantzGuildenstern

rg = RosencrantzGuildenstern()

# Full pipeline
result = rg.generate_with_audit(
    prompt="Explain Python decorators",
    context="User is a junior developer"
)

# Access components
draft_text = result['draft']['text']
audit_scores = result['audit']
recommendation = result['recommendation']

# Or run stages separately
draft = rg.generate_draft(prompt, context)
audit = rg.audit_draft(prompt, draft['text'])
```

## Why This Works

### Cost Efficiency
- **Large model**: 20B params, ~90s, expensive if cloud ($0.02/1K × 2K = $0.04)
- **Small model**: 7B params, ~8s, cheap if cloud ($0.01/1K × 1K = $0.01)
- **Total local**: $0.00 for both

### Quality Assurance
- Small model provides objective scoring framework
- Identifies specific weaknesses (not just "it's good/bad")
- Suggests alternative perspectives (counterfactuals)
- Reduces hallucination risk by catching unsupported claims

### Speed
- Audit takes only ~10% of generation time (8s vs 90s)
- Provides high-value feedback without regenerating
- Enables iterative refinement without full re-runs

## Example Output

```
╔════════════════════════════════════════════════════════════════════════════╗
║                    META-REASONING AUDIT REPORT                             ║
╚════════════════════════════════════════════════════════════════════════════╝

📊 QUALITY SCORES:
   • Relevance:      8.5/10
   • Structure:      9.0/10
   • Specificity:    7.0/10
   • Actionability:  8.0/10
   • Overall:        8.2/10

🎯 HALLUCINATION RISK: ✅ LOW

✅ STRENGTHS:
   • Clear structure with numbered steps
   • Good real-world examples
   • Actionable recommendations

⚠️  WEAKNESSES:
   • Could be more specific on edge cases
   • Missing performance considerations

🔄 COUNTERFACTUALS (Alternative Perspectives):
   • Alternative: Could consider async approach instead
   • Missing perspective: Security implications not addressed

💡 RECOMMENDATION: 🚀 SHIP

⏱️  Audit Time: 8.3s
══════════════════════════════════════════════════════════════════════════════
```

## Strategic Value

### For Developers
- Immediate quality feedback without waiting for code review
- Specific improvement suggestions (not vague "make it better")
- Learn from counterfactuals (what the AI didn't consider)
- Confidence score before committing code

### For Organizations
- Quality gate for AI-generated content
- Audit trail for compliance/review
- Reduced hallucination incidents
- Enables "trust but verify" workflow

### For Cost Optimization
- Prevents poor outputs from reaching production
- Reduces need for expensive cloud regeneration
- Small model audit << cost of fixing downstream bugs
- Local implementation = $0 marginal cost

## Comparison: Meta-Reasoning vs Single-Stage

| Metric | Single-Stage | Meta-Reasoning | Improvement |
|--------|--------------|----------------|-------------|
| Generation Time | 90s | 90s | Same |
| Audit Time | 0s | 8s | +8s overhead |
| Quality Visibility | None | 5 scores + narrative | ✅ Full transparency |
| Hallucination Detection | Manual | Automated | ✅ Systematic |
| Counterfactuals | None | 2-3 alternatives | ✅ Expanded thinking |
| Recommendation | None | ship/revise/regenerate | ✅ Decision support |
| Total Cost | $0.00 | $0.00 | Same (local) |

**Net Value**: 9% time overhead for comprehensive quality audit + decision framework

## Integration with Copilot Bridge

Can be used as optional quality gate:

```python
# In proxy_instrumented.py
from rosencrantz_guildenstern import RosencrantzGuildenstern

if task_type == "generation" and enable_audit:
    rg = RosencrantzGuildenstern()
    result = rg.generate_with_audit(prompt, context)
    
    if result['recommendation'] == 'regenerate':
        # Try again with more context
        enhanced_context = get_additional_context()
        result = rg.generate_with_audit(prompt, enhanced_context)
    
    return result['draft']['text'], result['audit']
```

## Future Enhancements

1. **Iterative Refinement**: Use audit feedback to regenerate improved draft
2. **Multi-Auditor Ensemble**: Use 2-3 small models, aggregate scores
3. **Domain-Specific Scoring**: Custom quality dimensions per task type
4. **Learning from Audits**: Train classifier to predict audit scores from draft
5. **Human-in-the-Loop**: Flag low scores for manual review before shipping

## Philosophy

> "We're actors — we're the opposite of people!"  
> — Rosencrantz & Guildenstern Are Dead, Tom Stoppard

The audit model doesn't create, it observes and comments. This separation of concerns enables:
- **Objective evaluation** (no bias from authorship)
- **Systematic quality framework** (not vibes-based)
- **Cheap verification** (small model << large model cost)
- **Actionable feedback** (specific weaknesses, not generic praise)

In a world where AI generates content at scale, **meta-reasoning is the quality control layer that makes it trustworthy.**
