#!/usr/bin/env python3
"""
Copilot-Bridge Proxy with Dual-GPU Support

Enhanced proxy that routes requests across two GPUs:
- GPU 0 (RTX 4080): Complex tasks, large models
- GPU 1 (Quadro M4000): Simple tasks, small models

Features:
- Automatic complexity detection and routing
- Concurrent draft + audit execution
- Prometheus metrics for both GPUs
- Fallback to cloud if local fails
"""
import os
import json
import httpx
import asyncio
import sys
import time
from typing import Dict, Any, Optional
from dual_gpu_orchestrator import DualGPUOrchestrator, TaskComplexity

# Configuration
LOCAL_GPU0 = os.getenv("OLLAMA_GPU0_URL", "http://192.168.1.138:11434")
LOCAL_GPU1 = os.getenv("OLLAMA_GPU1_URL", "http://192.168.1.138:11435")
GITHUB_API = "https://api.githubcopilot.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Thresholds
MAX_LOCAL_TOKENS = 8192  # Context limit for local models
CLOUD_FALLBACK_ENABLED = os.getenv("CLOUD_FALLBACK", "true").lower() == "true"

# Initialize dual-GPU orchestrator
orchestrator = DualGPUOrchestrator(
    gpu0_url=LOCAL_GPU0,
    gpu1_url=LOCAL_GPU1,
    enable_metrics=True
)


def should_route_to_cloud(payload: Dict[str, Any]) -> tuple[bool, str]:
    """
    Determine if request should go to cloud.
    
    Returns:
        (should_use_cloud, reason)
    """
    messages = payload.get("messages", [])
    if not messages:
        return False, "no_messages"
    
    last_msg = messages[-1].get("content", "")
    
    # Count approximate tokens (rough estimate: 1 token ≈ 4 chars)
    total_chars = sum(len(m.get("content", "")) for m in messages)
    approx_tokens = total_chars // 4
    
    if approx_tokens > MAX_LOCAL_TOKENS:
        return True, f"context_too_large_{approx_tokens}_tokens"
    
    # Check for cloud-only keywords
    cloud_keywords = [
        "gpt-4", "claude", "latest model", "most advanced",
        "proprietary", "openai"
    ]
    
    if any(kw in last_msg.lower() for kw in cloud_keywords):
        return True, "cloud_specific_request"
    
    return False, "can_handle_locally"


async def route_to_cloud(payload: Dict[str, Any]) -> str:
    """Route request to GitHub Copilot cloud."""
    if not GITHUB_TOKEN:
        return json.dumps({
            "error": "GITHUB_TOKEN not set, cannot route to cloud"
        })
    
    t0 = time.time()
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{GITHUB_API}/chat/completions",
                headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
                json=payload,
                timeout=60.0
            )
            elapsed = int((time.time() - t0) * 1000)
            
            print(f"☁️  CLOUD route: {elapsed}ms", file=sys.stderr)
            return response.text
            
        except Exception as e:
            return json.dumps({
                "error": f"Cloud routing failed: {str(e)}"
            })


def route_to_local_dual_gpu(
    prompt: str,
    use_audit: bool = False,
    concurrent: bool = True
) -> Dict[str, Any]:
    """
    Route request to local dual-GPU setup.
    
    Args:
        prompt: User's request
        use_audit: Whether to run meta-reasoning audit
        concurrent: Run draft + audit in parallel
    
    Returns:
        Response dict with completion
    """
    t0 = time.time()
    
    if use_audit:
        # Use dual-GPU orchestrator for draft + audit
        response = orchestrator.generate_with_audit(
            prompt=prompt,
            concurrent=concurrent
        )
        
        # Format as OpenAI-compatible response
        content = f"{response.draft}\n\n---\n**Meta-Analysis:**\n{response.audit['text']}"
        
        elapsed = int((time.time() - t0) * 1000)
        print(
            f"🎭 DUAL-GPU route: {elapsed}ms "
            f"(draft={response.draft_time:.1f}s on GPU{response.draft_gpu}, "
            f"audit={response.audit_time:.1f}s on GPU{response.audit_gpu}, "
            f"concurrent={concurrent})",
            file=sys.stderr
        )
        
    else:
        # Simple single-GPU generation
        result = orchestrator.simple_generate(prompt)
        content = result['text']
        
        elapsed = int((time.time() - t0) * 1000)
        print(
            f"🚀 LOCAL route: {elapsed}ms "
            f"(model={result['model']} on GPU{result['gpu']})",
            file=sys.stderr
        )
    
    return {
        "choices": [{
            "delta": {
                "content": content
            }
        }]
    }


async def main():
    """Main proxy handler."""
    # Read request payload from stdin
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {str(e)}"}))
        return
    
    messages = payload.get("messages", [])
    if not messages:
        print(json.dumps({"error": "No messages in payload"}))
        return
    
    last_msg = messages[-1].get("content", "")
    
    # Step 1: Check if we should route to cloud
    use_cloud, reason = should_route_to_cloud(payload)
    
    if use_cloud and CLOUD_FALLBACK_ENABLED:
        result = await route_to_cloud(payload)
        print(result)
        return
    
    # Step 2: Classify task complexity for local routing
    complexity = orchestrator.classify_task(last_msg)
    
    # Step 3: Determine if we should use meta-reasoning audit
    use_audit = complexity in [TaskComplexity.MODERATE, TaskComplexity.COMPLEX]
    
    # Enable concurrent execution for complex tasks
    concurrent = complexity == TaskComplexity.COMPLEX
    
    # Step 4: Route to local dual-GPU
    try:
        result = route_to_local_dual_gpu(
            prompt=last_msg,
            use_audit=use_audit,
            concurrent=concurrent
        )
        print(json.dumps(result))
        
    except Exception as e:
        if CLOUD_FALLBACK_ENABLED:
            print(f"⚠️  Local failed ({str(e)}), falling back to cloud", file=sys.stderr)
            result = await route_to_cloud(payload)
            print(result)
        else:
            print(json.dumps({"error": f"Local routing failed: {str(e)}"}))


if __name__ == "__main__":
    asyncio.run(main())
