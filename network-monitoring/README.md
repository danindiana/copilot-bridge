# Network Activity Monitoring Guide

This folder contains tools and documentation for monitoring Copilot network activity.

## Overview

Monitor network requests, tokens, latency, and cost savings for Copilot interactions using the instrumented proxy.

## Quick Start

### View Live Network Activity

```bash
cd ~/copilot-bridge
python3 proxy_instrumented.py 2>&1 1>/dev/null | jq '.'
```

### Metrics Captured

Each log entry includes:
- **Timestamp** (`ts`) - When the request occurred
- **Route** - `local` (Ollama) or `cloud` (GitHub Copilot)
- **Tokens In/Out** - Request and response token counts
- **Total Tokens** - Combined token usage
- **Latency (ms)** - Response time in milliseconds
- **Model** - Which model processed the request
- **Task Type** - Category of request (docstring, explain, refactor, etc.)
- **Cost Saved (USD)** - Money saved vs cloud baseline ($0.02/1K tokens)

## Usage Examples

### 1. Pretty-formatted Live View
```bash
python3 proxy_instrumented.py 2>&1 1>/dev/null | jq '.'
```

### 2. Filter Specific Fields
```bash
python3 proxy_instrumented.py 2>&1 1>/dev/null | jq '{route, latency_ms, cost_saved_usd}'
```

### 3. Save Logs to File
```bash
python3 proxy_instrumented.py 2>network-monitoring/copilot-metrics.jsonl
```

### 4. Analyze Total Cost Savings
```bash
cat copilot-metrics.jsonl | jq -s 'map(.cost_saved_usd) | add'
```

### 5. Count Requests by Route
```bash
cat copilot-metrics.jsonl | jq -s 'group_by(.route) | map({route: .[0].route, count: length})'
```

### 6. Average Latency by Route
```bash
cat copilot-metrics.jsonl | jq -s 'group_by(.route) | map({route: .[0].route, avg_latency: (map(.latency_ms) | add / length)})'
```

## Sample Output

```json
{
  "ts": "2025-10-19T09:02:02.654724+00:00",
  "route": "local",
  "tokens_in": 13,
  "tokens_out": 189,
  "total_tokens": 202,
  "latency_ms": 3008,
  "model": "qwen2.5-coder:7b-instruct-q8_0",
  "task": "docstring",
  "cost_saved_usd": 0.004
}
```

## Integration Options

### With Prometheus/Grafana
Use `exporter.py` to expose metrics:
```bash
python3 proxy_instrumented.py 2>&1 | python3 exporter.py
```

### With Log Aggregation (Loki, etc.)
Pipe stderr to your log aggregator:
```bash
python3 proxy_instrumented.py 2>&1 | your-log-forwarder
```

## Files in This Folder

- `README.md` - This guide
- `monitoring-commands.sh` - Useful monitoring commands
- `analysis-examples.md` - Data analysis examples
- `copilot-metrics.jsonl` - Saved metrics (generated)

## Requirements

- Python 3.8+
- `jq` for JSON formatting: `sudo apt install jq -y`
- Running Ollama instance at `http://192.168.1.138:11434`

## Related Files

- `../proxy_instrumented.py` - Main instrumented proxy
- `../exporter.py` - Prometheus metrics exporter
- `../prometheus.yml` - Prometheus configuration
- `../docker-compose.yml` - Monitoring stack setup
