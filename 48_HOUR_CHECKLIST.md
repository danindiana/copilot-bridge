# 48-Hour Action Checklist

**Goal**: Get instrumentation live, collect real data, show CFO the falling cost line.

---

## Day 1: Deploy & Instrument (4-6 hours)

### Morning (2-3 hours)

- [ ] **Install dependencies**
  ```bash
  pip install prometheus-client httpx
  ```

- [ ] **Start Prometheus exporter** (background)
  ```bash
  cd ~/copilot-bridge
  python3 exporter.py > exporter.log 2>&1 &
  echo $! > exporter.pid
  ```

- [ ] **Verify exporter is running**
  ```bash
  curl http://localhost:8000/metrics | head -20
  # Should see copilot_bridge_* metrics
  ```

- [ ] **Test instrumented bridge**
  ```bash
  python3 test_instrumentation.py
  # All tests should pass
  ```

### Afternoon (2-3 hours)

- [ ] **Update Continue.dev to use instrumented bridge** (if applicable)
  - OR: Run bridge manually for today's coding tasks

- [ ] **Generate test traffic**
  ```bash
  # Example: 10 sample requests
  for task in "docstring" "explain" "comment" "lint" "summarize"; do
    echo "Testing $task..."
    python3 proxy_instrumented.py \
      --prompt "Sample $task request for testing" \
      --task "$task" 2>> logs.jsonl
    sleep 2
  done
  ```

- [ ] **Send logs to exporter**
  ```bash
  cat logs.jsonl | while read line; do
    curl -X POST http://localhost:8080 -d "$line"
  done
  ```

- [ ] **Verify metrics updated**
  ```bash
  curl http://localhost:8000/metrics | grep copilot_bridge_tokens_saved
  # Should show non-zero count
  ```

- [ ] **Commit instrumentation**
  ```bash
  git add logs.jsonl exporter.log
  git commit -m "Day 1: Live instrumentation deployed, initial metrics collected"
  ```

---

## Day 2: Real-World Use & Reporting (6-8 hours)

### Morning (3-4 hours): Use Bridge for Actual Work

- [ ] **Route ALL AI requests through instrumented bridge today**
  - Docstrings for new functions
  - Code explanations
  - Bug detection
  - Refactoring suggestions

- [ ] **Log every interaction**
  ```bash
  # Keep this running in tmux/screen
  tail -f logs.jsonl | tee -a daily_usage.jsonl
  ```

- [ ] **Monitor live metrics**
  ```bash
  watch -n 5 'curl -s http://localhost:8000/metrics | grep -E "(tokens_saved|cost_saved|requests_by)"'
  ```

### Midday (1 hour): Collect Screenshots

- [ ] **Screenshot Prometheus metrics**
  - Open http://localhost:8000/metrics in browser
  - Capture tokens_saved, cost_saved counters

- [ ] **Create simple graph** (if Grafana not running)
  ```bash
  # Quick Python script to plot savings over time
  cat > plot_savings.py <<'EOF'
  import json
  import matplotlib.pyplot as plt
  from datetime import datetime
  
  times, savings = [], []
  with open('logs.jsonl') as f:
      for line in f:
          d = json.loads(line)
          times.append(datetime.fromisoformat(d['ts']))
          savings.append(d['cost_saved_usd'])
  
  cumulative = [sum(savings[:i+1]) for i in range(len(savings))]
  
  plt.figure(figsize=(10, 6))
  plt.plot(times, cumulative, linewidth=2)
  plt.title('Cumulative Cost Savings - Day 2', fontsize=16)
  plt.xlabel('Time')
  plt.ylabel('USD Saved')
  plt.grid(alpha=0.3)
  plt.tight_layout()
  plt.savefig('savings_day2.png', dpi=150)
  print("Saved to savings_day2.png")
  EOF
  
  python3 plot_savings.py
  ```

### Afternoon (2-3 hours): Analysis & Communication

- [ ] **Calculate actual metrics**
  ```bash
  cat > analyze_usage.py <<'EOF'
  import json
  
  total_tokens = 0
  total_cost_saved = 0.0
  local_count = 0
  cloud_count = 0
  total_latency = 0
  
  with open('daily_usage.jsonl') as f:
      lines = [json.loads(line) for line in f]
  
  for entry in lines:
      total_tokens += entry.get('total_tokens', 0)
      total_cost_saved += entry.get('cost_saved_usd', 0)
      
      if entry['route'] == 'local':
          local_count += 1
          total_latency += entry.get('latency_ms', 0)
      else:
          cloud_count += 1
  
  total_requests = local_count + cloud_count
  avg_latency = total_latency / local_count if local_count else 0
  
  print(f"""
  DAY 2 REAL-WORLD RESULTS
  {'='*50}
  
  Total Requests:        {total_requests}
  Local (saved):         {local_count} ({local_count/total_requests*100:.1f}%)
  Cloud (fallback):      {cloud_count} ({cloud_count/total_requests*100:.1f}%)
  
  Tokens Saved:          {total_tokens:,}
  Cost Saved:            ${total_cost_saved:.2f}
  
  Avg Local Latency:     {avg_latency:.0f}ms
  
  MONTHLY PROJECTION (22 workdays):
  Tokens/month:          {total_tokens * 22:,}
  Savings/month:         ${total_cost_saved * 22:.2f}
  """)
  EOF
  
  python3 analyze_usage.py > day2_results.txt
  cat day2_results.txt
  ```

- [ ] **Draft Slack message** (internal announcement)
  ```markdown
  🎯 Token-Saver Update: Day 2 Results
  
  Just wrapped a full workday routing AI coding requests through our local GPU instead of cloud APIs.
  
  **Results**:
  • XX requests handled (YY% local, ZZ% cloud)
  • $X.XX saved today
  • Projected: $XXX/month savings per developer
  • Zero quality degradation, <5s latency
  
  **Live Dashboard**: http://192.168.1.138:3000
  
  Looking for 2-3 beta testers to try this next week. DM me if interested!
  
  [Attach: savings_day2.png screenshot]
  ```

- [ ] **Commit results**
  ```bash
  git add daily_usage.jsonl day2_results.txt savings_day2.png
  git commit -m "Day 2: Real-world usage data, $X.XX saved, YY% local routing"
  git tag v0.2.0-tokens-metered
  ```

---

## Post-48h: Week 1 Actions

- [ ] **Post to internal Slack** (with screenshot)
  - Share day2_results.txt findings
  - Invite beta testers
  - Link to live dashboard

- [ ] **Recruit 2-3 beta testers**
  - Provide setup instructions (QUICKSTART.md)
  - Ask them to log usage for 1 week
  - Collect feedback on quality/latency

- [ ] **Schedule finance demo** (Week 2)
  - Show live dashboard to CFO/Director
  - Present CFO_EMAIL_TEMPLATE.md findings
  - Request approval for team-wide rollout

- [ ] **Weekly savings report** (automated)
  ```bash
  cat > weekly_report.sh <<'EOF'
  #!/bin/bash
  echo "Weekly Token Savings Report"
  echo "==========================="
  echo ""
  python3 analyze_usage.py
  echo ""
  echo "Dashboard: http://192.168.1.138:3000"
  EOF
  
  chmod +x weekly_report.sh
  
  # Add to cron (every Monday 9am)
  # 0 9 * * 1 /home/smduck/copilot-bridge/weekly_report.sh | mail -s "Weekly Token Savings" finance@company.com
  ```

---

## Success Criteria

After 48 hours, you should have:

✅ **Technical**:
- [ ] Exporter running and collecting metrics
- [ ] At least 10 real requests logged
- [ ] Metrics visible at http://localhost:8000/metrics
- [ ] Zero errors in exporter.log

✅ **Data**:
- [ ] Actual tokens saved count (>1,000)
- [ ] Actual cost saved (>$0.10)
- [ ] Route ratio measured (target: >40% local)
- [ ] Latency benchmarks (<5s p95)

✅ **Communication**:
- [ ] Screenshot of savings graph
- [ ] Internal Slack post drafted
- [ ] CFO email ready to send
- [ ] 2-3 beta testers recruited

✅ **Business**:
- [ ] Finance team aware of initiative
- [ ] Demo scheduled for Week 2
- [ ] Monthly projection calculated
- [ ] ROI validated (vs $1,200 GPU cost)

---

## Troubleshooting

**Exporter won't start**:
```bash
# Check if port is in use
lsof -i :8000
lsof -i :8080

# Kill existing process
kill $(cat exporter.pid)

# Restart
python3 exporter.py > exporter.log 2>&1 &
```

**Metrics not incrementing**:
```bash
# Verify logs are being sent
curl -X POST http://localhost:8080 \
  -d '{"ts":"2025-10-20T12:00:00Z","route":"local","tokens_in":100,"tokens_out":50,"total_tokens":150,"latency_ms":2000,"model":"test","task":"test","cost_saved_usd":0.003}'

# Check exporter.log for errors
tail -f exporter.log
```

**Bridge errors**:
```bash
# Test Ollama connection
curl http://192.168.1.138:11434/api/tags

# Test instrumented bridge
python3 proxy_instrumented.py --prompt "test" --task "test"

# Check stderr for JSON log
python3 proxy_instrumented.py --prompt "test" 2>&1 | grep '{'
```

---

## Quick Reference Commands

```bash
# Start exporter
python3 exporter.py > exporter.log 2>&1 &

# Test bridge
python3 test_instrumentation.py

# Check metrics
curl http://localhost:8000/metrics | grep copilot_bridge

# Analyze logs
python3 analyze_usage.py

# Weekly report
./weekly_report.sh

# Stop exporter
kill $(cat exporter.pid)
```

---

**REMEMBER**: The goal is to show the CFO a **falling cost line**. Focus on:
1. Collecting real data (not projections)
2. Creating visual proof (graphs, screenshots)
3. Communicating in business terms ($$, not tokens)

**You've got this.** 🚀
