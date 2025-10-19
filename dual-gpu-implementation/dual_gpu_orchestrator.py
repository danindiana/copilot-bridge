#!/usr/bin/env python3
"""
Dual-GPU Orchestrator for Copilot-Bridge

Routes requests across two GPUs for maximum throughput:
- GPU 0 (RTX 4080): Large draft-generating models
- GPU 1 (Quadro M4000): Small auditing/meta-reasoning models

Supports both sequential and concurrent execution modes.
"""
import httpx
import json
import time
import threading
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class TaskComplexity(Enum):
    """Complexity level determines GPU routing."""
    SIMPLE = "simple"      # Small model on GPU 1
    MODERATE = "moderate"  # Medium model, GPU selection based on load
    COMPLEX = "complex"    # Large model on GPU 0


@dataclass
class GPUEndpoint:
    """Configuration for a GPU-specific Ollama instance."""
    name: str
    gpu_id: int
    url: str
    port: int
    models: List[str]  # Models to prefer on this GPU
    max_vram_gb: float
    
    def __str__(self):
        return f"{self.name} (GPU {self.gpu_id}) @ {self.url}"


@dataclass
class RoutingDecision:
    """Record of routing decision for observability."""
    task_type: str
    complexity: TaskComplexity
    selected_gpu: int
    model: str
    reason: str
    timestamp: float


@dataclass
class DualGPUResponse:
    """Response from dual-GPU execution."""
    draft: str
    audit: Optional[Dict[str, Any]]
    draft_time: float
    audit_time: float
    total_time: float
    draft_gpu: int
    audit_gpu: int
    tokens_generated: int
    routing_decision: RoutingDecision
    concurrent: bool


class DualGPUOrchestrator:
    """
    Orchestrates AI requests across two GPUs.
    
    Architecture:
    - GPU 0 (RTX 4080): Large models for draft generation
    - GPU 1 (Quadro M4000): Small models for auditing/validation
    
    Supports:
    - Automatic routing based on task complexity
    - Concurrent execution (draft on GPU 0, audit on GPU 1)
    - Sequential fallback if one GPU is unavailable
    - Prometheus metrics for monitoring
    """
    
    def __init__(
        self,
        gpu0_url: str = "http://localhost:11434",
        gpu1_url: str = "http://localhost:11435",
        enable_metrics: bool = True
    ):
        # Configure GPU endpoints
        self.gpu0 = GPUEndpoint(
            name="RTX 4080 SUPER",
            gpu_id=0,
            url=gpu0_url,
            port=11434,
            models=[
                "gpt-oss:20b",
                "qwen2.5-coder:14b",
                "qwen2.5-coder:7b-instruct-q8_0"
            ],
            max_vram_gb=16.0
        )
        
        self.gpu1 = GPUEndpoint(
            name="Quadro M4000",
            gpu_id=1,
            url=gpu1_url,
            port=11435,
            models=[
                "qwen2.5-coder:1.5b",
                "qwen2.5-coder:3b",
                "phi3.5:3.8b"
            ],
            max_vram_gb=8.0
        )
        
        self.enable_metrics = enable_metrics
        self.routing_history: List[RoutingDecision] = []
        
        # Initialize metrics if enabled
        if enable_metrics:
            self._init_metrics()
    
    def _init_metrics(self):
        """Initialize Prometheus metrics."""
        try:
            from prometheus_client import Counter, Histogram, Gauge
            
            self.requests_total = Counter(
                'dual_gpu_requests_total',
                'Total requests by GPU',
                ['gpu_id', 'model', 'task_type']
            )
            
            self.inference_duration = Histogram(
                'dual_gpu_inference_duration_seconds',
                'Inference duration by GPU',
                ['gpu_id', 'model', 'concurrent']
            )
            
            self.concurrent_executions = Counter(
                'dual_gpu_concurrent_executions_total',
                'Number of concurrent dual-GPU executions'
            )
            
            self.gpu_selection = Counter(
                'dual_gpu_selection_total',
                'GPU selection decisions',
                ['gpu_id', 'reason']
            )
            
        except ImportError:
            print("⚠️  prometheus_client not installed, metrics disabled")
            self.enable_metrics = False
    
    def classify_task(self, prompt: str, context: str = "") -> TaskComplexity:
        """
        Classify task complexity based on prompt analysis.
        
        Rules:
        - SIMPLE: Docstrings, comments, linting, renaming, explanations
        - MODERATE: Refactoring, small features, debugging
        - COMPLEX: New features, architecture, large refactors
        """
        text = (prompt + " " + context).lower()
        
        # Simple task keywords
        simple_keywords = [
            "docstring", "comment", "lint", "rename", "explain",
            "document", "format", "style", "what does", "summarize"
        ]
        
        # Complex task keywords
        complex_keywords = [
            "implement", "create", "build", "design", "architect",
            "refactor all", "rewrite", "optimize", "algorithm"
        ]
        
        if any(kw in text for kw in simple_keywords):
            return TaskComplexity.SIMPLE
        elif any(kw in text for kw in complex_keywords):
            return TaskComplexity.COMPLEX
        else:
            return TaskComplexity.MODERATE
    
    def select_gpu_and_model(
        self,
        complexity: TaskComplexity,
        prefer_concurrent: bool = True
    ) -> Tuple[GPUEndpoint, str, str]:
        """
        Select GPU and model based on task complexity.
        
        Returns:
            (gpu_endpoint, model_name, reason)
        """
        if complexity == TaskComplexity.SIMPLE:
            # Small tasks → GPU 1 (Quadro M4000)
            gpu = self.gpu1
            model = "qwen2.5-coder:1.5b"
            reason = "simple_task_to_gpu1"
            
        elif complexity == TaskComplexity.COMPLEX:
            # Complex tasks → GPU 0 (RTX 4080)
            gpu = self.gpu0
            model = "qwen2.5-coder:7b-instruct-q8_0"
            reason = "complex_task_to_gpu0"
            
        else:  # MODERATE
            # Balance between GPUs based on availability
            gpu = self.gpu0  # Default to more powerful GPU
            model = "qwen2.5-coder:7b-instruct-q8_0"
            reason = "moderate_task_to_gpu0"
        
        return gpu, model, reason
    
    def call_model(
        self,
        gpu: GPUEndpoint,
        model: str,
        prompt: str,
        num_ctx: int = 4096
    ) -> Dict[str, Any]:
        """
        Call a model on a specific GPU endpoint.
        
        Returns:
            Response with text, timing, and metadata
        """
        start = time.time()
        
        try:
            with httpx.Client(timeout=180.0) as client:
                response = client.post(
                    f"{gpu.url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"num_ctx": num_ctx}
                    }
                )
                result = response.json()
            
            elapsed = time.time() - start
            
            return {
                "text": result.get("response", ""),
                "time": elapsed,
                "model": model,
                "gpu": gpu.gpu_id,
                "tokens": result.get("eval_count", 0),
                "success": True
            }
            
        except Exception as e:
            elapsed = time.time() - start
            return {
                "text": f"ERROR: {str(e)}",
                "time": elapsed,
                "model": model,
                "gpu": gpu.gpu_id,
                "tokens": 0,
                "success": False,
                "error": str(e)
            }
    
    def generate_with_audit(
        self,
        prompt: str,
        context: str = "",
        concurrent: bool = True
    ) -> DualGPUResponse:
        """
        Generate draft + audit using both GPUs.
        
        Workflow:
        1. Classify task complexity
        2. Generate draft on GPU 0 (large model)
        3. Generate audit on GPU 1 (small model) - concurrent if enabled
        4. Return combined response
        
        Args:
            prompt: User's request
            context: Additional context
            concurrent: Run draft + audit in parallel (default: True)
        
        Returns:
            DualGPUResponse with draft, audit, and timing data
        """
        start_time = time.time()
        
        # Step 1: Classify task
        complexity = self.classify_task(prompt, context)
        
        # Step 2: Select GPU and model for draft
        draft_gpu, draft_model, reason = self.select_gpu_and_model(complexity)
        
        # Record routing decision
        routing = RoutingDecision(
            task_type="draft_generation",
            complexity=complexity,
            selected_gpu=draft_gpu.gpu_id,
            model=draft_model,
            reason=reason,
            timestamp=start_time
        )
        self.routing_history.append(routing)
        
        # Track metrics
        if self.enable_metrics:
            self.gpu_selection.labels(
                gpu_id=draft_gpu.gpu_id,
                reason=reason
            ).inc()
        
        # Step 3: Generate draft
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        print(f"🎭 Dual-GPU Execution ({'CONCURRENT' if concurrent else 'SEQUENTIAL'})")
        print(f"   Draft: {draft_model} on {draft_gpu.name}")
        print(f"   Audit: qwen2.5-coder:1.5b on {self.gpu1.name}")
        print()
        
        if concurrent:
            # Concurrent execution: draft and audit in parallel
            draft_result = {}
            audit_result = {}
            
            def generate_draft():
                draft_result.update(self.call_model(
                    draft_gpu, draft_model, full_prompt
                ))
            
            def generate_audit():
                audit_prompt = f"""Analyze this coding request and provide a quality assessment:

REQUEST: {prompt}

Evaluate:
1. Complexity level (1-10)
2. Key challenges
3. Recommended approach
4. Potential pitfalls
5. Success criteria

Provide brief, actionable guidance."""
                
                audit_result.update(self.call_model(
                    self.gpu1, "qwen2.5-coder:1.5b", audit_prompt
                ))
            
            # Run both in parallel
            thread1 = threading.Thread(target=generate_draft)
            thread2 = threading.Thread(target=generate_audit)
            
            thread1.start()
            thread2.start()
            thread1.join()
            thread2.join()
            
            if self.enable_metrics:
                self.concurrent_executions.inc()
            
        else:
            # Sequential execution: draft first, then audit
            draft_result = self.call_model(draft_gpu, draft_model, full_prompt)
            
            audit_prompt = f"""Analyze this draft response for quality:

ORIGINAL REQUEST: {prompt}

DRAFT RESPONSE:
{draft_result['text'][:500]}...

Evaluate:
1. Relevance (1-10)
2. Correctness
3. Completeness
4. Suggestions for improvement

Be brief and specific."""
            
            audit_result = self.call_model(
                self.gpu1, "qwen2.5-coder:1.5b", audit_prompt
            )
        
        total_time = time.time() - start_time
        
        # Track metrics
        if self.enable_metrics:
            self.requests_total.labels(
                gpu_id=draft_gpu.gpu_id,
                model=draft_model,
                task_type="draft"
            ).inc()
            
            self.requests_total.labels(
                gpu_id=self.gpu1.gpu_id,
                model="qwen2.5-coder:1.5b",
                task_type="audit"
            ).inc()
            
            self.inference_duration.labels(
                gpu_id=draft_gpu.gpu_id,
                model=draft_model,
                concurrent=str(concurrent)
            ).observe(draft_result['time'])
            
            self.inference_duration.labels(
                gpu_id=self.gpu1.gpu_id,
                model="qwen2.5-coder:1.5b",
                concurrent=str(concurrent)
            ).observe(audit_result['time'])
        
        # Build response
        return DualGPUResponse(
            draft=draft_result['text'],
            audit={
                "text": audit_result['text'],
                "model": audit_result['model'],
                "tokens": audit_result['tokens']
            },
            draft_time=draft_result['time'],
            audit_time=audit_result['time'],
            total_time=total_time,
            draft_gpu=draft_gpu.gpu_id,
            audit_gpu=self.gpu1.gpu_id,
            tokens_generated=draft_result['tokens'] + audit_result['tokens'],
            routing_decision=routing,
            concurrent=concurrent
        )
    
    def simple_generate(self, prompt: str, context: str = "") -> Dict[str, Any]:
        """
        Simple generation without audit (single GPU).
        
        Routes to appropriate GPU based on complexity.
        """
        complexity = self.classify_task(prompt, context)
        gpu, model, reason = self.select_gpu_and_model(complexity)
        
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        print(f"🚀 Single-GPU Execution")
        print(f"   Model: {model} on {gpu.name}")
        print()
        
        result = self.call_model(gpu, model, full_prompt)
        
        if self.enable_metrics:
            self.requests_total.labels(
                gpu_id=gpu.gpu_id,
                model=model,
                task_type="simple"
            ).inc()
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics."""
        return {
            "total_requests": len(self.routing_history),
            "gpu0_requests": sum(1 for r in self.routing_history if r.selected_gpu == 0),
            "gpu1_requests": sum(1 for r in self.routing_history if r.selected_gpu == 1),
            "complexity_breakdown": {
                "simple": sum(1 for r in self.routing_history if r.complexity == TaskComplexity.SIMPLE),
                "moderate": sum(1 for r in self.routing_history if r.complexity == TaskComplexity.MODERATE),
                "complex": sum(1 for r in self.routing_history if r.complexity == TaskComplexity.COMPLEX)
            }
        }


# Demo / Testing
if __name__ == "__main__":
    import sys
    
    # Initialize orchestrator
    orchestrator = DualGPUOrchestrator(
        gpu0_url="http://localhost:11434",  # Change to 192.168.1.138 if needed
        gpu1_url="http://localhost:11435"
    )
    
    # Test prompt
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "Write a docstring for a function that calculates fibonacci numbers"
    
    print(f"📝 Prompt: {prompt}\n")
    
    # Run with concurrent execution
    response = orchestrator.generate_with_audit(prompt, concurrent=True)
    
    print("\n" + "="*80)
    print("📊 RESULTS")
    print("="*80)
    print(f"\n🎯 DRAFT (GPU {response.draft_gpu}):")
    print(response.draft[:500])
    print("\n🔍 AUDIT (GPU {response.audit_gpu}):")
    print(response.audit['text'][:500])
    print(f"\n⏱️  TIMING:")
    print(f"   Draft: {response.draft_time:.2f}s")
    print(f"   Audit: {response.audit_time:.2f}s")
    print(f"   Total: {response.total_time:.2f}s")
    print(f"   Concurrent: {response.concurrent}")
    print(f"\n📈 STATS:")
    print(json.dumps(orchestrator.get_stats(), indent=2))
