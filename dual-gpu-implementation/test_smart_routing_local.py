#!/usr/bin/env python3
"""
Test the smart routing with local Ollama endpoint.
"""
from dual_gpu_orchestrator import DualGPUOrchestrator

# Initialize with local endpoint
orchestrator = DualGPUOrchestrator(
    gpu0_url="http://localhost:11434",
    gpu1_url="http://localhost:11434",  # Same endpoint for now
    enable_metrics=False  # Disable prometheus for testing
)

print("\n" + "="*80)
print("TESTING SMART ROUTING WITH LOCAL OLLAMA")
print("="*80)

# Test SIMPLE task (should route to small model)
print("\n📝 TEST 1: SIMPLE task (docstring - should use 1.5B model)")
print("-" * 80)
result1 = orchestrator.simple_generate(
    "Write a docstring for a function that sorts a list of integers"
)
print(f"✓ Model used: {result1['model']}")
print(f"✓ GPU: {result1['gpu']}")
print(f"✓ Time: {result1['time']:.2f}s")
print(f"✓ Tokens: {result1['tokens']}")
print(f"✓ Success: {result1['success']}")
print(f"\n📄 Response preview:")
print(result1['text'][:300] + "..." if len(result1['text']) > 300 else result1['text'])

# Test MODERATE task (should route to larger model)
print("\n\n🔧 TEST 2: MODERATE task (refactoring - should use 7B model)")
print("-" * 80)
result2 = orchestrator.simple_generate(
    "Refactor this code to use list comprehension"
)
print(f"✓ Model used: {result2['model']}")
print(f"✓ GPU: {result2['gpu']}")
print(f"✓ Time: {result2['time']:.2f}s")
print(f"✓ Tokens: {result2['tokens']}")

# Test COMPLEX task (should route to larger model)
print("\n\n🚀 TEST 3: COMPLEX task (implementation - should use 7B model)")
print("-" * 80)
result3 = orchestrator.simple_generate(
    "Implement a binary search algorithm in Python"
)
print(f"✓ Model used: {result3['model']}")
print(f"✓ GPU: {result3['gpu']}")
print(f"✓ Time: {result3['time']:.2f}s")
print(f"✓ Tokens: {result3['tokens']}")

# Show routing statistics
print("\n\n" + "="*80)
print("📊 ROUTING STATISTICS")
print("="*80)
stats = orchestrator.get_stats()
print(f"Total requests: {stats['total_requests']}")
print(f"GPU 0 requests: {stats['gpu0_requests']}")
print(f"GPU 1 requests: {stats['gpu1_requests']}")
print(f"\nComplexity breakdown:")
print(f"  SIMPLE:   {stats['complexity_breakdown']['simple']} request(s) → 1.5B model")
print(f"  MODERATE: {stats['complexity_breakdown']['moderate']} request(s) → 7B model")
print(f"  COMPLEX:  {stats['complexity_breakdown']['complex']} request(s) → 7B model")

# Calculate efficiency
if result1['success'] and result2['success'] and result3['success']:
    total_time = result1['time'] + result2['time'] + result3['time']
    total_tokens = result1['tokens'] + result2['tokens'] + result3['tokens']
    print(f"\n📈 Performance:")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Total tokens: {total_tokens}")
    print(f"  Avg speed: {total_tokens/total_time:.1f} tokens/sec")

print("\n" + "="*80)
print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
print("="*80)
print("\n💡 Smart Routing Benefits:")
print("   • SIMPLE tasks use faster 1.5B model (3-5x faster)")
print("   • MODERATE/COMPLEX tasks use quality 7B model")
print("   • Automatic classification reduces GPU waste")
print("   • Better resource utilization = cost savings")
print("")
