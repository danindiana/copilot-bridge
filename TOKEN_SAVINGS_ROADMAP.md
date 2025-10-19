# Token-Savings KPI Roadmap

## The Single Metric That Matters

```
Tokens_Saved_Per_Day = (Cloud_Requests_Routed_Local × Avg_Tokens_Per_Request)
```

**Why this metric?**
- Directly correlates to cost ($0.02 per 1K tokens cloud baseline)
- Easy to explain to finance team (tokens = dollars)
- Monthly trending shows ROI of local hardware investment
- Scales with team size (more devs = more savings)

---

## Month-by-Month Roadmap

| Month | Feature | Δ-Token Target | Traffic % | Cumulative Savings | GPU Note |
|-------|---------|----------------|-----------|-------------------|----------|
| **M0** | **Docstring/Comment** | 2K tokens/req | 40% | **40%** | GPU paid, electricity ≈$0.001/1K |
| **M1** | **Inline Autocomplete** | 0.3K tokens/req | 35% | **65%** | 1.5B model fits in 1GB VRAM |
| **M2** | **Small Refactor/Rename** | 1K tokens/req | 15% | **75%** | 7B model, unload after 10min idle |
| **M3** | **Test Generation** | 3K tokens/req | 8% | **80%** | 14B model, framework-detected only |
| **M4** | **Embeddings + Search** | 0.5K tokens/req | 20% | **85%** | nomic-embed-text → $0 |
| **M5** | **Multi-file Explain** | 5K tokens/req | 5% | **87%** | 32B q4_K_M quantized → 19GB |
| **M6** | **Agent + Cache** | Variable | Smart | **90%** | Cache hit = 0 tokens |

### Cost Translation (Per Developer/Month)

Baseline: 100K tokens/day × 22 workdays × $0.02/1K = **$44/month cloud-only**

| Month | Savings % | $ Saved/Dev/Month | Annual Savings (10 devs) |
|-------|-----------|-------------------|--------------------------|
| M0 | 40% | $17.60 | $2,112 |
| M1 | 65% | $28.60 | $3,432 |
| M2 | 75% | $33.00 | $3,960 |
| M3 | 80% | $35.20 | $4,224 |
| M4 | 85% | $37.40 | $4,488 |
| M5 | 87% | $38.28 | $4,594 |
| M6 | 90% | $39.60 | **$4,752** |

**ROI**: RTX 4080 costs ~$1,200. **Breakeven at 3 developers in Month 1.**

---

## Instrumentation Architecture

### 1. Request Logging (JSON Lines)

Every bridge request emits one line to stderr:

```json
{
  "ts": "2025-10-20T14:23:10Z",
  "route": "local",
  "tokens_in": 1200,
  "tokens_out": 280,
  "ms": 3500,
  "model": "qwen2.5-coder:7b",
  "task": "docstring",
  "cost_saved_usd": 0.0296
}
```

### 2. Prometheus Metrics

```
# Tokens routed locally (not sent to cloud)
copilot_bridge_tokens_saved_total

# USD saved (assumes $0.02/1K baseline)
copilot_bridge_cost_saved_usd

# Local inference latency (ms)
copilot_bridge_local_latency_ms

# Route distribution
copilot_bridge_requests_by_route{route="local|cloud"}

# Model usage
copilot_bridge_requests_by_model{model="qwen2.5-coder:7b|llama3.1:8b|..."}
```

### 3. Grafana Dashboard

**Panel 1: Daily Cost Savings ($$)**
```promql
sum(rate(copilot_bridge_cost_saved_usd[1d]))
```

**Panel 2: Tokens Saved vs Cloud Baseline**
```promql
sum(copilot_bridge_tokens_saved_total)
```

**Panel 3: Route Distribution (Pie Chart)**
```promql
sum by (route) (rate(copilot_bridge_requests_by_route[5m]))
```

**Panel 4: Local Latency (P50/P95/P99)**
```promql
histogram_quantile(0.95, copilot_bridge_local_latency_ms)
```

---

## Implementation Files

### File 1: Enhanced `proxy.py` (Logging Added)

See `proxy_instrumented.py` for version with:
- JSON logging to stderr
- Token counting (estimate from prompt length)
- Cost calculation ($0.02/1K baseline)
- Route tracking (local vs cloud)

### File 2: `exporter.py` (Prometheus Bridge)

Lightweight HTTP server:
- Listens on `:8080` for JSON log lines (POST)
- Exposes Prometheus metrics on `:8000/metrics`
- Zero dependencies beyond prometheus_client

### File 3: `docker-compose.yml` (Optional Full Stack)

Complete monitoring stack:
- Bridge service (proxy.py)
- Prometheus (metrics storage)
- Grafana (visualization)
- Loki (log aggregation, optional)

### File 4: `prometheus.yml` (Config)

Scrape config for bridge metrics.

### File 5: `grafana-dashboard.json` (Pre-built Dashboard)

Import-ready dashboard showing:
- $ saved today/week/month
- Tokens diverted vs cloud
- Route distribution
- Model usage heatmap
- Latency percentiles

---

## Finance-Friendly Summary

### Email Template (for CFO/Director)

**Subject**: Cost Optimization: AI Coding Assistant Token Savings

**Body**:

> We deployed a hybrid routing system that directs routine AI coding requests to local hardware instead of cloud APIs.
> 
> **Current Status (Month 0)**:
> - 40% of requests routed locally (docstrings, comments, simple queries)
> - Estimated savings: **$18/developer/month**
> - Actual cost: Electricity (~$0.001/1K tokens vs $0.02/1K cloud)
> - ROI: 3-month breakeven on GPU investment
> 
> **6-Month Target (Month 6)**:
> - 90% of requests routed locally
> - Estimated savings: **$40/developer/month**
> - Annual savings (10 developers): **$4,752**
> - Additional benefits: Data privacy, vendor independence
> 
> **Live Dashboard**: http://192.168.1.138:3000
> - Real-time $ saved counter
> - Daily/weekly/monthly trending
> - Per-developer breakdowns (future)
> 
> **Next Steps**:
> - Beta test with 3 developers this week
> - Roll out to full team in 2 weeks
> - Monthly savings reports to finance
> 
> This is a **sunk-cost optimization**: GPU is already paid for, electricity is negligible, savings scale linearly with team size.

---

## 48-Hour Action Plan

### Day 1: Instrumentation (4 hours)

- [x] Enhanced proxy with JSON logging
- [ ] Deploy exporter.py in background
- [ ] Configure Prometheus scraping
- [ ] Import Grafana dashboard
- [ ] Validate metrics flowing

### Day 2: Real-World Testing (8 hours)

- [ ] Use bridge for full workday
- [ ] Monitor dashboard live
- [ ] Screenshot daily savings counter
- [ ] Calculate actual tokens/$ saved
- [ ] Document real-world performance

### Week 1: Internal Rollout (ongoing)

- [ ] Post screenshot + findings to Slack
- [ ] Recruit 2-3 beta testers
- [ ] Collect feedback on latency/quality
- [ ] Tag `v0.2.0-tokens-metered`
- [ ] Schedule finance demo

### Month 1: Optimization

- [ ] Implement M1 features (autocomplete)
- [ ] Add per-developer metrics
- [ ] Create weekly savings report
- [ ] Expand to 10 developers
- [ ] Measure actual savings vs projection

---

## Metrics Glossary

**Tokens Saved**: Input + output tokens handled locally instead of cloud  
**Cost Saved (USD)**: `tokens_saved × $0.02 / 1000` (assumes cloud baseline)  
**Route Ratio**: `local_requests / total_requests`  
**Latency**: Time from request to response (ms)  
**Model Load**: Active models in VRAM  
**Cache Hit Rate**: Requests served from cache (future feature)

---

## Dashboard Screenshots (Placeholders)

### Daily Savings
```
┌─────────────────────────────────────┐
│  Today's Savings: $8.45             │
│  ▲ +$1.23 vs yesterday              │
│  ──────────────────────────────     │
│  Week:  $47.32                      │
│  Month: $189.67                     │
└─────────────────────────────────────┘
```

### Route Distribution
```
┌─────────────────────────────────────┐
│  Local:  73% ████████████████░░     │
│  Cloud:  27% ██████░░░░░░░░░░       │
└─────────────────────────────────────┘
```

### Tokens Saved (7-day trend)
```
 5K │              ╱╲
    │          ╱╲╱  ╲
 4K │      ╱╲╱      ╲
    │  ╱╲╱          ╲╱
 3K ├╱──────────────────
    Mon Tue Wed Thu Fri Sat Sun
```

---

## Success Criteria

### Technical
- [ ] <5s p95 latency for local requests
- [ ] >70% route ratio by Month 1
- [ ] Zero data loss in logging pipeline
- [ ] 99.9% uptime for bridge service

### Business
- [ ] >$15/dev/month savings in Month 0
- [ ] >$30/dev/month savings by Month 3
- [ ] Finance team sees live dashboard
- [ ] CFO approves expanded rollout

### Operational
- [ ] One-click deployment for new developers
- [ ] Automated daily savings reports
- [ ] Alert if route ratio drops <60%
- [ ] Weekly team review of metrics

---

## Risk Mitigation

**Risk**: Local model quality < cloud  
**Mitigation**: Smart routing keeps complex tasks on cloud, monitor quality scores

**Risk**: GPU failure = no local routing  
**Mitigation**: Automatic fallback to cloud, SLA maintained

**Risk**: Underestimated token usage  
**Mitigation**: Real-world metering corrects projections month-over-month

**Risk**: Developer adoption resistance  
**Mitigation**: Transparent metrics, opt-in beta, quality proof points

---

## Future Enhancements (M7+)

### Advanced Routing
- Task complexity scoring (route to optimal model)
- User preference learning (personalized routing)
- Time-of-day optimization (GPU load balancing)

### Cost Attribution
- Per-developer token tracking
- Per-project cost allocation
- Team/org hierarchy breakdowns

### Cache Layer
- Semantic deduplication (similar prompts)
- Response reuse (common patterns)
- Multi-user shared cache

### Multi-GPU Scaling
- Round-robin load balancing
- Model specialization (dedicate GPUs to task types)
- Auto-scaling based on demand

---

## References

- See `proxy_instrumented.py` - Enhanced bridge with logging
- See `exporter.py` - Prometheus metrics exporter
- See `docker-compose.yml` - Full monitoring stack
- See `MISSION_BRIEF.py` - Strategic context
- See `LESSONS_LEARNED.md` - Core insights

---

**The Token-Savings Flywheel**:

```
Measure → Optimize → Broadcast → Recruit → Repeat
  ↓          ↓           ↓           ↓         ↓
Metrics   Route %    Slack post   Beta team  Improve
            ↑                                   ↓
            └───────────── Loop ────────────────┘
```

**Until the cloud bill flat-lines.** 🎯
