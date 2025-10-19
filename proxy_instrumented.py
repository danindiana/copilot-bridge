#!/usr/bin/env python3
"""
Enhanced Copilot Bridge with Token-Savings Instrumentation

Logs every request as JSON for Prometheus/Grafana monitoring.
Tracks tokens saved, cost saved, latency, and routing decisions.
"""
import httpx
import json
import sys
import time
from datetime import datetime, timezone

# Configuration
OLLAMA_BASE = "http://192.168.1.138:11434"
GITHUB_COPILOT_BASE = "https://api.githubcopilot.com"  # Placeholder
CLOUD_COST_PER_1K_TOKENS = 0.02  # Baseline: $0.02/1K tokens

# Keywords that trigger LOCAL routing
LOCAL_KEYWORDS = [
    "docstring", "comment", "explain", "document", "lint",
    "type hint", "format", "summarize", "rename", "simple"
]

def estimate_tokens(text: str) -> int:
    """
    Rough token estimation: ~1.3 words per token for English.
    This is conservative; actual count may vary.
    """
    return int(len(text.split()) * 1.3)

def route_decision(prompt: str) -> str:
    """
    Determine if request should go LOCAL or CLOUD.
    LOCAL: Simple, routine tasks (docstrings, comments, explanations)
    CLOUD: Complex, specialized tasks (refactoring, architecture, debugging)
    """
    prompt_lower = prompt.lower()
    if any(kw in prompt_lower for kw in LOCAL_KEYWORDS):
        return "local"
    return "cloud"

def log_request(route: str, tokens_in: int, tokens_out: int, latency_ms: int, model: str, task: str = "general"):
    """
    Emit structured JSON log for Prometheus ingestion.
    Logs to stderr to keep stdout clean for actual responses.
    """
    cost_saved = 0.0
    if route == "local":
        # Calculate savings vs cloud baseline
        total_tokens = tokens_in + tokens_out
        cost_saved = (total_tokens / 1000) * CLOUD_COST_PER_1K_TOKENS
    
    log_entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "route": route,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "total_tokens": tokens_in + tokens_out,
        "latency_ms": latency_ms,
        "model": model,
        "task": task,
        "cost_saved_usd": round(cost_saved, 4)
    }
    
    # Write to stderr (can be piped to exporter or log aggregator)
    print(json.dumps(log_entry), file=sys.stderr, flush=True)

def call_local(prompt: str, model: str = "qwen2.5-coder:7b-instruct-q8_0") -> tuple[str, int]:
    """
    Route request to local Ollama instance.
    Returns: (response_text, latency_ms)
    """
    start = time.time()
    
    with httpx.Client(timeout=60.0) as client:
        response = client.post(
            f"{OLLAMA_BASE}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        result = response.json()
        answer = result.get("response", "")
    
    latency_ms = int((time.time() - start) * 1000)
    return answer, latency_ms

def call_cloud(prompt: str, github_token: str = None) -> tuple[str, int]:
    """
    Route request to GitHub Copilot cloud API.
    Returns: (response_text, latency_ms)
    
    NOTE: This is a placeholder. Actual GitHub Copilot API integration
          requires proper authentication and endpoint configuration.
    """
    start = time.time()
    
    # Placeholder: In production, replace with actual GitHub Copilot API call
    answer = "[CLOUD RESPONSE PLACEHOLDER] This would be routed to GitHub Copilot."
    
    latency_ms = int((time.time() - start) * 1000)
    return answer, latency_ms

def process_request(prompt: str, task: str = "general") -> str:
    """
    Main request handler with instrumentation.
    """
    # Estimate input tokens
    tokens_in = estimate_tokens(prompt)
    
    # Decide routing
    route = route_decision(prompt)
    
    # Execute request
    if route == "local":
        model = "qwen2.5-coder:7b-instruct-q8_0"
        answer, latency_ms = call_local(prompt, model)
    else:
        model = "github-copilot-cloud"
        answer, latency_ms = call_cloud(prompt)
    
    # Estimate output tokens
    tokens_out = estimate_tokens(answer)
    
    # Log for metrics
    log_request(route, tokens_in, tokens_out, latency_ms, model, task)
    
    return answer

# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Instrumented Copilot Bridge")
    parser.add_argument("--prompt", type=str, help="Prompt to send")
    parser.add_argument("--task", type=str, default="general", help="Task type (docstring, refactor, etc.)")
    args = parser.parse_args()
    
    if args.prompt:
        result = process_request(args.prompt, args.task)
        print(result)
    else:
        # Demo mode: show sample requests
        print("╔" + "═"*76 + "╗")
        print("║" + " "*18 + "INSTRUMENTED COPILOT BRIDGE DEMO" + " "*26 + "║")
        print("╚" + "═"*76 + "╝")
        print()
        
        demos = [
            ("Write a docstring for a function that calculates fibonacci numbers", "docstring"),
            ("Explain how quicksort works with complexity analysis", "explain"),
            ("Refactor this legacy code to use modern Python async/await patterns", "refactor"),
        ]
        
        for prompt, task in demos:
            print(f"\n📝 Task: {task}")
            print(f"💬 Prompt: {prompt[:60]}...")
            result = process_request(prompt, task)
            print(f"✅ Response: {result[:100]}...")
            print()
        
        print("─"*78)
        print("💡 Check stderr for JSON logs (pipe to exporter.py or Loki)")
        print("─"*78)
