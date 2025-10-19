#!/usr/bin/env python3
"""
Prometheus Exporter for Copilot Bridge Token Savings

Lightweight HTTP server that:
1. Receives JSON log lines (POST to :8080)
2. Updates Prometheus metrics
3. Exposes metrics on :8000/metrics

Zero external dependencies beyond prometheus_client.

Usage:
    python3 exporter.py &
    # Bridge sends logs to http://localhost:8080
    # Prometheus scrapes http://localhost:8000/metrics
"""
import sys
import json
import http.server
import socketserver
from prometheus_client import Counter, Gauge, Histogram, start_http_server

# Prometheus Metrics
TOKENS_SAVED = Counter(
    'copilot_bridge_tokens_saved_total',
    'Total tokens routed locally instead of cloud'
)

COST_SAVED = Counter(
    'copilot_bridge_cost_saved_usd',
    'Total USD saved by routing locally (baseline: $0.02/1K tokens)'
)

REQUESTS_BY_ROUTE = Counter(
    'copilot_bridge_requests_by_route',
    'Request count by routing decision',
    ['route']
)

REQUESTS_BY_MODEL = Counter(
    'copilot_bridge_requests_by_model',
    'Request count by model',
    ['model']
)

REQUESTS_BY_TASK = Counter(
    'copilot_bridge_requests_by_task',
    'Request count by task type',
    ['task']
)

LOCAL_LATENCY = Histogram(
    'copilot_bridge_local_latency_ms',
    'Local inference latency in milliseconds',
    buckets=[100, 500, 1000, 2000, 3000, 5000, 10000, 30000]
)

TOKENS_IN = Gauge(
    'copilot_bridge_last_tokens_in',
    'Last request input token count'
)

TOKENS_OUT = Gauge(
    'copilot_bridge_last_tokens_out',
    'Last request output token count'
)

def process_log_line(line: str):
    """
    Parse JSON log line and update metrics.
    
    Expected format:
    {
      "ts": "2025-10-20T14:23:10Z",
      "route": "local",
      "tokens_in": 1200,
      "tokens_out": 280,
      "total_tokens": 1480,
      "latency_ms": 3500,
      "model": "qwen2.5-coder:7b",
      "task": "docstring",
      "cost_saved_usd": 0.0296
    }
    """
    try:
        data = json.loads(line)
        
        route = data.get("route", "unknown")
        tokens_in = data.get("tokens_in", 0)
        tokens_out = data.get("tokens_out", 0)
        total_tokens = data.get("total_tokens", 0)
        latency_ms = data.get("latency_ms", 0)
        model = data.get("model", "unknown")
        task = data.get("task", "general")
        cost_saved = data.get("cost_saved_usd", 0.0)
        
        # Update counters
        REQUESTS_BY_ROUTE.labels(route=route).inc()
        REQUESTS_BY_MODEL.labels(model=model).inc()
        REQUESTS_BY_TASK.labels(task=task).inc()
        
        if route == "local":
            TOKENS_SAVED.inc(total_tokens)
            COST_SAVED.inc(cost_saved)
            LOCAL_LATENCY.observe(latency_ms)
        
        # Update gauges (last values)
        TOKENS_IN.set(tokens_in)
        TOKENS_OUT.set(tokens_out)
        
        print(f"✓ Processed: {route} | {task} | {total_tokens} tokens | ${cost_saved:.4f} saved", flush=True)
        
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON: {line[:100]}... | Error: {e}", file=sys.stderr, flush=True)
    except Exception as e:
        print(f"✗ Error processing line: {e}", file=sys.stderr, flush=True)

class LogHandler(http.server.BaseHTTPRequestHandler):
    """
    HTTP handler for receiving log lines.
    Expects POST requests with JSON log lines in body.
    """
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        # Process each line (supports batch sending)
        for line in body.strip().split('\n'):
            if line:
                process_log_line(line)
        
        # Return 204 No Content (success, no response body)
        self.send_response(204)
        self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default HTTP logging (too verbose)
        pass

if __name__ == "__main__":
    print("╔" + "═"*76 + "╗")
    print("║" + " "*20 + "COPILOT BRIDGE PROMETHEUS EXPORTER" + " "*22 + "║")
    print("╚" + "═"*76 + "╝")
    print()
    
    # Start Prometheus metrics server
    print("📊 Starting Prometheus metrics server on :8000/metrics")
    start_http_server(8000)
    
    # Start log ingestion server
    print("📥 Starting log ingestion server on :8080 (POST JSON logs here)")
    print()
    print("🔗 URLs:")
    print("   • Metrics:  http://localhost:8000/metrics")
    print("   • Logs:     POST to http://localhost:8080")
    print()
    print("⏳ Waiting for log lines...")
    print("─"*78)
    
    # Allow socket reuse (avoid 'address already in use' errors)
    socketserver.TCPServer.allow_reuse_address = True
    
    # Create and start server
    with socketserver.TCPServer(("", 8080), LogHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down exporter...")
            sys.exit(0)
