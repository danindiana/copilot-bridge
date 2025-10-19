# Refactoring Quality Tests

## Purpose

Compare **local model** refactoring quality vs **GitHub Copilot** (cloud) on identical code samples.

**Key Questions**:
1. Can local models match cloud quality for common refactorings?
2. Which refactoring types work best locally?
3. What's the cost/quality tradeoff?

---

## Test Methodology

### Test Corpus
- **6 realistic code samples** covering common refactoring scenarios
- **Pre-calculated token counts** (shown before each test)
- **User consent** before feeding large contexts to models

### Refactoring Categories
1. **Extract Function** - Break down monolithic code
2. **Modernize Syntax** - Legacy → modern Python idioms
3. **Add Type Hints** - Untyped → fully typed
4. **Improve Naming** - Cryptic → descriptive
5. **Error Handling** - Add try/except, validations
6. **Performance** - Optimize loops, use comprehensions

### Quality Scoring (1-10)
- **Correctness**: Does it still work? (0 = broken, 10 = perfect)
- **Readability**: Easier to understand? (1-10)
- **Pythonic**: Modern idioms used? (1-10)
- **Completeness**: All improvements applied? (1-10)
- **Overall**: Weighted average

---

## Test Files

### `test_samples.py`
Contains 6 code samples with token counts:
- `legacy_login.py` (450 tokens) - Extract functions, add types
- `data_processor.py` (680 tokens) - Modernize, add error handling
- `api_client.py` (520 tokens) - Improve naming, add validation
- `report_generator.py` (890 tokens) - Performance optimization
- `config_manager.py` (340 tokens) - Type hints, refactor logic
- `test_utils.py` (280 tokens) - Extract helpers, simplify

**Total corpus**: ~3,160 tokens

### `run_refactor_test.py`
Interactive test runner:
1. Show token count and estimated cost
2. Ask user which model to test (local/cloud/both)
3. Ask user to confirm feeding context
4. Run refactoring request
5. Display before/after side-by-side
6. Prompt user for quality scores
7. Save results to CSV

### `compare_results.py`
Analysis tool:
- Load all test results
- Compare local vs cloud scores
- Generate comparison graphs
- Calculate cost per quality point
- Output markdown report

### `test_config.yaml`
Configuration for models, prompts, scoring rubric

---

## Usage

### Quick Start (Single Test)
```bash
cd ~/copilot-bridge/refactor-quality-tests
python3 run_refactor_test.py --sample legacy_login --model local
```

### Full Suite (All Samples, Both Models)
```bash
python3 run_refactor_test.py --all --models local,cloud
```

### Interactive Mode (Recommended for First Run)
```bash
python3 run_refactor_test.py --interactive
# Will prompt for each decision
```

### Analyze Results
```bash
python3 compare_results.py
# Generates: results/comparison_report.md
```

---

## Token Transparency

Before each test, you'll see:
```
╔════════════════════════════════════════════════════════════════════════════╗
║                      REFACTORING TEST: legacy_login.py                     ║
╚════════════════════════════════════════════════════════════════════════════╝

📊 Token Analysis:
   • Sample code: 450 tokens
   • Refactoring prompt: 180 tokens
   • Total input: 630 tokens
   • Expected output: ~300 tokens
   • TOTAL CONTEXT: ~930 tokens

💰 Cost Estimate:
   • Local (qwen2.5-coder:7b): $0.000 (free)
   • Cloud (GitHub Copilot): $0.019 ($0.02/1K tokens)

⏱️  Expected Time:
   • Local: 5-8 seconds
   • Cloud: 2-4 seconds

Do you want to proceed? [y/N]
```

---

## Quality Metrics

### Scoring Dimensions

**Correctness (0-10)**:
- 0: Code doesn't run
- 5: Runs but has bugs
- 10: Perfect, no regressions

**Readability (1-10)**:
- 1: Worse than original
- 5: No improvement
- 10: Dramatically clearer

**Pythonic (1-10)**:
- 1: Still using anti-patterns
- 5: Some improvements
- 10: Textbook modern Python

**Completeness (1-10)**:
- 1: Almost nothing changed
- 5: Half of requested changes
- 10: All improvements applied

### Overall Score
```
Overall = (Correctness × 0.4) + (Readability × 0.2) + (Pythonic × 0.2) + (Completeness × 0.2)
```

---

## Expected Results

### Hypothesis

| Refactoring Type | Local Model Expected | Cloud Expected |
|------------------|---------------------|----------------|
| Extract Function | 7-8/10 | 9-10/10 |
| Modernize Syntax | 8-9/10 | 9-10/10 |
| Add Type Hints | 9-10/10 | 9-10/10 |
| Improve Naming | 6-7/10 | 8-9/10 |
| Error Handling | 7-8/10 | 8-9/10 |
| Performance | 6-7/10 | 7-8/10 |

**Local models should excel at**:
- Syntax transformations (type hints, modernization)
- Pattern-based refactoring (extract function)

**Cloud models should excel at**:
- Semantic understanding (naming, performance)
- Context-aware error handling

---

## Output Files

### `results/`
- `test_YYYYMMDD_HHMMSS.json` - Raw test results
- `comparison_report.md` - Human-readable analysis
- `quality_scores.csv` - Scores for graphing
- `cost_analysis.csv` - Cost per quality point

### `visualizations/`
- `quality_comparison.png` - Bar chart: local vs cloud
- `cost_efficiency.png` - Scatter: cost vs quality
- `category_breakdown.png` - Heatmap: scores by category

---

## Sample Output

```
═══════════════════════════════════════════════════════════════════════════════
TEST RESULTS: legacy_login.py
═══════════════════════════════════════════════════════════════════════════════

Model: qwen2.5-coder:7b (LOCAL)
Time: 6.3 seconds
Cost: $0.000

Scores:
  • Correctness:   9/10 ✓ (code runs, no bugs)
  • Readability:   8/10 ✓ (much clearer structure)
  • Pythonic:      9/10 ✓ (uses pathlib, f-strings)
  • Completeness:  7/10 ⚠ (missing some type hints)
  • OVERALL:       8.4/10

Changes Applied:
  ✓ Extracted 3 helper functions
  ✓ Added type hints to main function
  ✓ Replaced string concatenation with f-strings
  ✓ Used pathlib instead of os.path
  ⚠ Didn't add docstrings (not requested, but nice-to-have)

═══════════════════════════════════════════════════════════════════════════════
```

---

## Next Steps

1. **Run baseline tests** (all samples, local model only)
2. **Compare with cloud** (if GitHub token available)
3. **Analyze results** (generate report)
4. **Update TOKEN_SAVINGS_ROADMAP.md** with refactoring confidence scores
5. **Add best-performing refactorings to proxy routing logic**

---

## Integration with Main Project

Results feed back into:
- `TOKEN_SAVINGS_ROADMAP.md` - Update M2 projections based on actual quality
- `proxy_instrumented.py` - Add refactoring tasks to LOCAL_KEYWORDS if scores >8/10
- `LESSONS_LEARNED.md` - Document which refactorings work best locally

---

**This is empirical quality measurement, not guesswork.** 🎯
