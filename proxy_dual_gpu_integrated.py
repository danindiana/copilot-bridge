#!/usr/bin/env python3
"""
Copilot Bridge with Dual-GPU Smart Routing Integration

This proxy combines:
- Original routing logic (local/cloud decisions)
- Dual-GPU smart routing (SIMPLE/MODERATE/COMPLEX classification)
- Prometheus instrumentation for monitoring
- Token savings tracking

Usage:
    python3 proxy_dual_gpu_integrated.py --prompt "Write a docstring" --task docstring
    
Environment variables:
    GITHUB_TOKEN          - GitHub API token (required for cloud routing)
    ENABLE_DUAL_GPU       - Enable dual-GPU routing (default: true)
    GPU0_URL              - GPU 0 Ollama endpoint (default: http://localhost:11434)
    GPU1_URL              - GPU 1 Ollama endpoint (default: http://localhost:11434)
    OLLAMA_BASE           - Fallback Ollama URL if dual-GPU disabled
"""

import os
import sys
import json
import time
import httpx
import argparse
from datetime import datetime, timezone
from typing import Tuple, Optional

# Try to import dual-GPU orchestrator
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dual-gpu-implementation'))
    from dual_gpu_orchestrator import DualGPUOrchestrator, TaskComplexity
    DUAL_GPU_AVAILABLE = True
except ImportError:
    DUAL_GPU_AVAILABLE = False
    print("⚠️  Dual-GPU orchestrator not found - falling back to single-model routing", file=sys.stderr)

# ============================================================================
# CONFIGURATION
# ============================================================================

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ENABLE_DUAL_GPU = os.getenv("ENABLE_DUAL_GPU", "true").lower() in ("true", "1", "yes")
GPU0_URL = os.getenv("GPU0_URL", "http://localhost:11434")
GPU1_URL = os.getenv("GPU1_URL", "http://localhost:11434")
OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://192.168.1.138:11434")
GITHUB_COPILOT_BASE = "https://api.githubcopilot.com"

CLOUD_COST_PER_1K_TOKENS = 0.02  # $0.02 per 1K tokens baseline

# Keywords that trigger LOCAL routing (vs cloud)
LOCAL_KEYWORDS = [
    "docstring", "comment", "explain", "document", "lint",
    "type hint", "format", "summarize", "rename", "simple"
]

# ============================================================================
# DUAL-GPU ORCHESTRATOR INITIALIZATION
# ============================================================================

orchestrator = None
if ENABLE_DUAL_GPU and DUAL_GPU_AVAILABLE:
    try:
        orchestrator = DualGPUOrchestrator(
            gpu0_url=GPU0_URL,
            gpu1_url=GPU1_URL,
            enable_metrics=True
        )
        print(f"✅ Dual-GPU orchestrator initialized", file=sys.stderr)
        print(f"   GPU 0: {GPU0_URL}", file=sys.stderr)
        print(f"   GPU 1: {GPU1_URL}", file=sys.stderr)
    except Exception as e:
        print(f"⚠️  Failed to initialize dual-GPU orchestrator: {e}", file=sys.stderr)
        print(f"   Falling back to single-model routing", file=sys.stderr)
        orchestrator = None

# ============================================================================
# UTILITIES
# ============================================================================

def estimate_tokens(text: str) -> int:
    """Rough token estimation: ~1.3 words per token"""
    return int(len(text.split()) * 1.3)

def should_route_local(prompt: str) -> bool:
    """Determine if request should go LOCAL or CLOUD"""
    prompt_lower = prompt.lower()
    return any(kw in prompt_lower for kw in LOCAL_KEYWORDS)

def log_request(
    route: str,
    tokens_in: int,
    tokens_out: int,
    latency_ms: int,
    model: str,
    task: str = "general",
    complexity: Optional[str] = None,
    gpu_used: Optional[str] = None
):
    """Emit structured JSON log for Prometheus ingestion"""
    cost_saved = 0.0
    if route == "local":
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
        "cost_saved_usd": round(cost_saved, 4),
        "dual_gpu_enabled": orchestrator is not None,
        "complexity": complexity,
        "gpu_used": gpu_used
    }
    
    print(json.dumps(log_entry), file=sys.stderr, flush=True)

# ============================================================================
# ROUTING HANDLERS
# ============================================================================

def call_local_single_model(prompt: str, model: str = "qwen2.5-coder:7b-instruct-q8_0") -> Tuple[str, int, str]:
    """
    Route request to local Ollama (single model, no dual-GPU).
    Returns: (response_text, latency_ms, gpu_info)
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
    return answer, latency_ms, "single-gpu"

def call_local_dual_gpu(prompt: str) -> Tuple[str, int, str, str, str]:
    """
    Route request via dual-GPU orchestrator.
    Returns: (response_text, latency_ms, complexity, gpu_info, model_used)
    """
    start = time.time()
    
    # Classify task to determine complexity and routing
    complexity = orchestrator.classify_task(prompt)
    gpu, model, reason = orchestrator.select_gpu_and_model(complexity)
    
    # Call the model
    result = orchestrator.call_model(gpu, model, prompt)
    
    latency_ms = int((time.time() - start) * 1000)
    
    complexity_str = complexity.name if hasattr(complexity, 'name') else str(complexity)
    gpu_info = f"{gpu.name} (GPU {gpu.gpu_id})"
    
    return (
        result.get("text", ""),
        latency_ms,
        complexity_str,
        gpu_info,
        model
    )

def call_cloud(prompt: str) -> Tuple[str, int]:
    """
    Route request to GitHub Copilot cloud API.
    Returns: (response_text, latency_ms)
    """
    if not GITHUB_TOKEN:
        return "[ERROR: GITHUB_TOKEN not set - cannot route to cloud]", 0
    
    start = time.time()
    
    # Placeholder for actual GitHub Copilot API integration
    answer = "[CLOUD RESPONSE PLACEHOLDER] This would be routed to GitHub Copilot."
    
    latency_ms = int((time.time() - start) * 1000)
    return answer, latency_ms

# ============================================================================
# MAIN REQUEST PROCESSOR
# ============================================================================

def process_request(prompt: str, task: str = "general") -> str:
    """
    Main request handler with dual-GPU smart routing and instrumentation.
    
    Flow:
    1. Estimate input tokens
    2. Decide local vs cloud
    3. If local + dual-GPU enabled → use orchestrator
    4. If local + dual-GPU disabled → use single model
    5. If cloud → route to GitHub Copilot
    6. Log metrics
    """
    tokens_in = estimate_tokens(prompt)
    
    # Step 1: Decide local vs cloud
    route_to_local = should_route_local(prompt)
    
    if route_to_local:
        # LOCAL routing
        if orchestrator:
            # Use dual-GPU orchestrator
            try:
                answer, latency_ms, complexity, gpu_info, model = call_local_dual_gpu(prompt)
                tokens_out = estimate_tokens(answer)
                
                log_request(
                    route="local",
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    latency_ms=latency_ms,
                    model=model,
                    task=task,
                    complexity=complexity,
                    gpu_used=gpu_info
                )
                
                return answer
                
            except Exception as e:
                print(f"⚠️  Dual-GPU routing failed: {e}", file=sys.stderr)
                print(f"   Falling back to single-model routing", file=sys.stderr)
                # Fall through to single-model routing
        
        # Single-model fallback
        model = "qwen2.5-coder:7b-instruct-q8_0"
        answer, latency_ms, gpu_info = call_local_single_model(prompt, model)
        tokens_out = estimate_tokens(answer)
        
        log_request(
            route="local",
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            latency_ms=latency_ms,
            model=model,
            task=task,
            gpu_used=gpu_info
        )
        
        return answer
    
    else:
        # CLOUD routing
        answer, latency_ms = call_cloud(prompt)
        tokens_out = estimate_tokens(answer)
        
        log_request(
            route="cloud",
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            latency_ms=latency_ms,
            model="github-copilot",
            task=task
        )
        
        return answer

# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Copilot Bridge with Dual-GPU Smart Routing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 proxy_dual_gpu_integrated.py --prompt "Write a docstring for a sort function"
  python3 proxy_dual_gpu_integrated.py --prompt "Refactor this code" --task refactor
  ENABLE_DUAL_GPU=false python3 proxy_dual_gpu_integrated.py --prompt "Explain this"
        """
    )
    
    parser.add_argument("--prompt", type=str, help="Prompt to send to AI")
    parser.add_argument("--task", type=str, default="general", help="Task type (docstring, refactor, etc.)")
    parser.add_argument("--demo", action="store_true", help="Run demo with sample requests")
    
    args = parser.parse_args()
    
    if args.demo:
        run_demo()
    elif args.prompt:
        result = process_request(args.prompt, args.task)
        print("\n" + "="*75)
        print("RESPONSE:")
        print("="*75)
        print(result)
    else:
        parser.print_help()

def run_demo():
    """Run demo with sample requests"""
    print("╔" + "═"*75 + "╗")
    print("║" + " "*18 + "COPILOT BRIDGE - DUAL-GPU DEMO" + " "*25 + "║")
    print("╚" + "="*75 + "╝\n")
    
    print(f"Dual-GPU Enabled: {orchestrator is not None}")
    print(f"GPU 0 URL: {GPU0_URL}")
    print(f"GPU 1 URL: {GPU1_URL}\n")
    
    test_prompts = [
        ("Write a docstring for a function that sorts a list", "docstring"),
        ("Refactor this code to improve performance", "refactor"),
        ("Implement a binary search algorithm", "implement"),
    ]
    
    for prompt, task in test_prompts:
        print(f"\n{'─'*75}")
        print(f"Prompt: {prompt}")
        print(f"Task: {task}")
        print(f"{'─'*75}")
        
        result = process_request(prompt, task)
        print(f"Response preview: {result[:100]}...")

if __name__ == "__main__":
    main()
