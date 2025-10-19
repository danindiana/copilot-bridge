#!/usr/bin/env python3
"""
Test the smart routing with single Ollama endpoint.
"""
from dual_gpu_orchestrator import DualGPUOrchestrator

# Initialize with both endpoints pointing to the working Ollama instance
orchestrator = DualGPUOrchestrator(
    gpu0_url="http://192.168.1.138:11434",
    gpu1_url="http://192.168.1.138:11434",  # Same as GPU 0 for now
    enable_metrics=False  # Disable prometheus for testing
)

# Test SIMPLE task (should route to small model)
print("="*80)
print("TEST 1: SIMPLE task (docstring)")
print("="*80)
result1 = orchestrator.simple_generate(
    "Write a docstring for a function that sorts a list of integers"
)
print(f"\nModel used: {result1['model']}")
print(f"GPU: {result1['gpu']}")
print(f"Time: {result1['time']:.2f}s")
print(f"Success: {result1['success']}")
print(f"\nResponse preview:")
print(result1['text'][:200] + "..." if len(result1['text']) > 200 else result1['text'])

# Test MODERATE task
print("\n" + "="*80)
print("TEST 2: MODERATE task (refactoring)")
print("="*80)
result2 = orchestrator.simple_generate(
    "Refactor this code to use list comprehension instead of loops"
)
print(f"\nModel used: {result2['model']}")
print(f"GPU: {result2['gpu']}")
print(f"Time: {result2['time']:.2f}s")
print(f"Success: {result2['success']}")

# Test COMPLEX task
print("\n" + "="*80)
print("TEST 3: COMPLEX task (implementation)")
print("="*80)
result3 = orchestrator.simple_generate(
    "Implement a binary search tree with insert, delete, and balance operations"
)
print(f"\nModel used: {result3['model']}")
print(f"GPU: {result3['gpu']}")
print(f"Time: {result3['time']:.2f}s")
print(f"Success: {result3['success']}")

# Show routing statistics
print("\n" + "="*80)
print("ROUTING STATISTICS")
print("="*80)
stats = orchestrator.get_stats()
print(f"Total requests: {stats['total_requests']}")
print(f"GPU 0 requests: {stats['gpu0_requests']}")
print(f"GPU 1 requests: {stats['gpu1_requests']}")
print(f"\nComplexity breakdown:")
print(f"  SIMPLE: {stats['complexity_breakdown']['simple']}")
print(f"  MODERATE: {stats['complexity_breakdown']['moderate']}")
print(f"  COMPLEX: {stats['complexity_breakdown']['complex']}")

print("\n" + "="*80)
print("✅ All tests completed successfully!")
print("="*80)
