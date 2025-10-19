# Network Activity Analysis Examples

This document provides practical examples for analyzing Copilot network activity data.

## Prerequisites

1. Generate metrics data:
   ```bash
   cd ~/copilot-bridge
   python3 proxy_instrumented.py 2>network-monitoring/copilot-metrics.jsonl
   ```

2. Ensure `jq` is installed:
   ```bash
   sudo apt install jq -y
   ```

## Basic Analysis

### Total Requests
```bash
wc -l copilot-metrics.jsonl
```

### View Sample Request
```bash
head -1 copilot-metrics.jsonl | jq '.'
```

### View Latest Request
```bash
tail -1 copilot-metrics.jsonl | jq '.'
```

## Cost Analysis

### Total Cost Saved
```bash
cat copilot-metrics.jsonl | jq -s 'map(.cost_saved_usd) | add'
```

### Cost Saved by Route
```bash
cat copilot-metrics.jsonl | jq -s 'group_by(.route) | map({
  route: .[0].route,
  total_cost_saved: (map(.cost_saved_usd) | add),
  request_count: length
})'
```

### Average Cost Saved per Request
```bash
cat copilot-metrics.jsonl | jq -s 'map(.cost_saved_usd) | add / length'
```

## Performance Analysis

### Average Latency by Route
```bash
cat copilot-metrics.jsonl | jq -s 'group_by(.route) | map({
  route: .[0].route,
  avg_latency_ms: (map(.latency_ms) | add / length),
  min_latency_ms: (map(.latency_ms) | min),
  max_latency_ms: (map(.latency_ms) | max)
})'
```

### Slowest Requests
```bash
cat copilot-metrics.jsonl | jq -s 'sort_by(.latency_ms) | reverse | .[0:5] | map({latency_ms, route, task, model})'
```

### Fastest Requests
```bash
cat copilot-metrics.jsonl | jq -s 'sort_by(.latency_ms) | .[0:5] | map({latency_ms, route, task, model})'
```

## Token Usage Analysis

### Total Tokens Processed
```bash
cat copilot-metrics.jsonl | jq -s 'map(.total_tokens) | add'
```

### Token Distribution by Route
```bash
cat copilot-metrics.jsonl | jq -s 'group_by(.route) | map({
  route: .[0].route,
  total_tokens: (map(.total_tokens) | add),
  avg_tokens: (map(.total_tokens) | add / length)
})'
```

### Largest Responses (by output tokens)
```bash
cat copilot-metrics.jsonl | jq -s 'sort_by(.tokens_out) | reverse | .[0:5] | map({tokens_out, task, route, model})'
```

## Routing Analysis

### Request Count by Route
```bash
cat copilot-metrics.jsonl | jq -s 'group_by(.route) | map({
  route: .[0].route,
  count: length,
  percentage: (length / ([.[]] | length) * 100)
})'
```

### Task Type Distribution
```bash
cat copilot-metrics.jsonl | jq -s 'group_by(.task) | map({
  task: .[0].task,
  count: length
}) | sort_by(.count) | reverse'
```

### Model Usage
```bash
cat copilot-metrics.jsonl | jq -s 'group_by(.model) | map({
  model: .[0].model,
  count: length,
  avg_latency_ms: (map(.latency_ms) | add / length)
})'
```

## Time-based Analysis

### Requests per Hour
```bash
cat copilot-metrics.jsonl | jq -r '.ts' | cut -d'T' -f2 | cut -d':' -f1 | sort | uniq -c
```

### Daily Summary
```bash
cat copilot-metrics.jsonl | jq -s 'group_by(.ts | split("T")[0]) | map({
  date: .[0].ts | split("T")[0],
  requests: length,
  total_tokens: (map(.total_tokens) | add),
  cost_saved: (map(.cost_saved_usd) | add)
})'
```

## Combined Insights

### Full Summary Report
```bash
cat copilot-metrics.jsonl | jq -s '{
  total_requests: length,
  total_tokens: (map(.total_tokens) | add),
  total_cost_saved: (map(.cost_saved_usd) | add),
  avg_latency_ms: (map(.latency_ms) | add / length),
  routes: (group_by(.route) | map({route: .[0].route, count: length})),
  tasks: (group_by(.task) | map({task: .[0].task, count: length}))
}'
```

### Efficiency Metrics
```bash
cat copilot-metrics.jsonl | jq -s '{
  local_requests: (map(select(.route == "local")) | length),
  cloud_requests: (map(select(.route == "cloud")) | length),
  local_percentage: ((map(select(.route == "local")) | length) / length * 100),
  avg_local_latency: (map(select(.route == "local")) | map(.latency_ms) | add / length),
  avg_cloud_latency: (map(select(.route == "cloud")) | map(.latency_ms) | add / length)
}'
```

## Export to CSV

### Basic CSV Export
```bash
echo "timestamp,route,tokens_in,tokens_out,latency_ms,cost_saved" > metrics.csv
cat copilot-metrics.jsonl | jq -r '[.ts, .route, .tokens_in, .tokens_out, .latency_ms, .cost_saved_usd] | @csv' >> metrics.csv
```

### Full CSV Export
```bash
echo "timestamp,route,tokens_in,tokens_out,total_tokens,latency_ms,model,task,cost_saved" > metrics-full.csv
cat copilot-metrics.jsonl | jq -r '[.ts, .route, .tokens_in, .tokens_out, .total_tokens, .latency_ms, .model, .task, .cost_saved_usd] | @csv' >> metrics-full.csv
```

## Alerting Examples

### Find High Latency Requests (>5 seconds)
```bash
cat copilot-metrics.jsonl | jq 'select(.latency_ms > 5000) | {ts, latency_ms, route, task}'
```

### Find Expensive Requests (>1000 tokens)
```bash
cat copilot-metrics.jsonl | jq 'select(.total_tokens > 1000) | {ts, total_tokens, route, task}'
```

### Find Failed or Anomalous Requests
```bash
cat copilot-metrics.jsonl | jq 'select(.tokens_out == 0 or .latency_ms > 30000)'
```

## Visualization Data Preparation

### Prepare for Plotting (Python)
```bash
cat copilot-metrics.jsonl | jq -s 'map({
  timestamp: .ts,
  latency: .latency_ms,
  tokens: .total_tokens,
  route: .route
})' > plot-data.json
```

### Time Series Data
```bash
cat copilot-metrics.jsonl | jq -s 'map({
  time: .ts,
  value: .latency_ms,
  series: .route
})' > timeseries.json
```
