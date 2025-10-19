# Architecture Decisions

## Why No Continue.dev in Production Stack?

### Initial Role (Smoke Test Phase)
- **Purpose**: Verify local Ollama models work with VS Code
- **Result**: ✅ Successful (Google-style docstring generation)
- **Timeline**: Day 1, testing phase only

### Why We Removed It

1. **Adds No Value Over Direct Ollama Calls**
   - Continue.dev: VS Code → Extension → Ollama API
   - Our approach: Python → Ollama API directly
   - **Elimination**: Removes middleware layer

2. **Slower Than Direct API**
   - Continue.dev routing: ~200-500ms overhead
   - Direct httpx call: <10ms
   - **Win**: 98% faster routing decisions

3. **No Control Over Routing Logic**
   - Continue.dev: Fixed keyword matching
   - Our proxy: Custom LOCAL_KEYWORDS list, token estimation, cost tracking
   - **Win**: Full control over hybrid routing

4. **Can't Instrument**
   - Continue.dev: No access to internal metrics
   - Our bridge: JSON logs → Prometheus → Grafana
   - **Win**: Complete observability

5. **No Meta-Reasoning Support**
   - Continue.dev: Single-stage generation only
   - Our R&G module: Two-stage with quality audit
   - **Win**: Built-in quality assurance

6. **Config Complexity**
   - Continue.dev: YAML/JSON config hell (we debugged this)
   - Our approach: Pure Python, no external config
   - **Win**: Simpler, more maintainable

### Current Architecture (Post-Continue.dev)

```
Developer Request
        ↓
┌───────────────────────────────────┐
│  proxy_instrumented.py            │
│  - Keyword routing                │
│  - Token estimation               │
│  - JSON logging                   │
└───────────────────────────────────┘
        ↓
    ┌───┴────┐
    ↓        ↓
┌────────┐ ┌──────────┐
│ LOCAL  │ │  CLOUD   │
│ Ollama │ │ GitHub   │
└────────┘ └──────────┘
    ↓
┌───────────────────────────────────┐
│  rosencrantz_guildenstern.py      │
│  - Large model generation         │
│  - Small model audit              │
│  - Quality scores                 │
└───────────────────────────────────┘
    ↓
┌───────────────────────────────────┐
│  exporter.py                      │
│  - JSON logs → Prometheus         │
│  - Metrics dashboard              │
└───────────────────────────────────┘
```

**Zero dependency on Continue.dev.**

### Smoke Test Artifacts Kept for Historical Reference

Files preserved in `smoke-test-phase/`:
- `test_docstring.py` - Proof that local models work
- `SMOKE_TEST_RESULTS.md` - Initial validation
- Continue.dev config troubleshooting notes

These prove the concept worked but are not part of production.

### Decision Summary

| Component | Status | Reason |
|-----------|--------|--------|
| Continue.dev Extension | ❌ Removed | Middleware overhead, no value |
| Direct Ollama API | ✅ Production | Fast, controllable, instrumentable |
| proxy_instrumented.py | ✅ Production | Custom routing + KPI tracking |
| rosencrantz_guildenstern.py | ✅ Production | Meta-reasoning quality gate |
| exporter.py | ✅ Production | Prometheus metrics |

**Principle**: Eliminate all middleware that doesn't add measurable value.

### What We Gained by Removing Continue.dev

1. **Faster**: Direct API calls (~10ms vs 200-500ms)
2. **Simpler**: No config.json/config.yaml debugging
3. **Observable**: Full control over logging/metrics
4. **Flexible**: Can add R&G, custom routing, cost tracking
5. **Maintainable**: Pure Python, no VS Code extension dependencies

### Lesson Learned

> "Use tools to validate concepts, then build production systems that own the full stack."

Continue.dev proved local models work. Mission accomplished. Now we own the entire pipeline.
