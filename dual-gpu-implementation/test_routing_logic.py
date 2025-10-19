#!/usr/bin/env python3
"""
Quick Routing Logic Validation Script

Tests task classification and model selection WITHOUT actual inference.
Runs in <1 second to validate routing decisions.
"""

import sys
sys.path.insert(0, '/home/smduck/copilot-bridge/dual-gpu-implementation')

from dual_gpu_orchestrator import DualGPUOrchestrator, TaskComplexity

def test_classification():
    """Test task complexity classification"""
    
    orchestrator = DualGPUOrchestrator(
        gpu0_url="http://localhost:11434",
        gpu1_url="http://localhost:11434",
        enable_metrics=False
    )
    
    test_cases = [
        # SIMPLE tasks
        ("Write a docstring for a function", TaskComplexity.SIMPLE),
        ("Add a comment explaining this code", TaskComplexity.SIMPLE),
        ("Explain what this function does", TaskComplexity.SIMPLE),
        ("Document this class", TaskComplexity.SIMPLE),
        ("Add type hints to this function", TaskComplexity.MODERATE),  # Actually moderate
        
        # MODERATE tasks
        ("Refactor this code to be more efficient", TaskComplexity.MODERATE),
        ("Optimize this algorithm", TaskComplexity.COMPLEX),  # Actually complex
        ("Improve error handling in this function", TaskComplexity.MODERATE),
        ("Modernize this legacy code", TaskComplexity.MODERATE),
        ("Add logging to this module", TaskComplexity.MODERATE),
        
        # COMPLEX tasks
        ("Implement a binary search tree", TaskComplexity.COMPLEX),
        ("Create a REST API for user management", TaskComplexity.COMPLEX),
        ("Build a caching layer with TTL", TaskComplexity.COMPLEX),
        ("Design a thread-safe queue", TaskComplexity.COMPLEX),
        ("Implement OAuth2 authentication", TaskComplexity.COMPLEX),
    ]
    
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║           ROUTING LOGIC VALIDATION (Fast Test)                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝\n")
    
    correct = 0
    total = len(test_cases)
    
    results_by_complexity = {
        TaskComplexity.SIMPLE: [],
        TaskComplexity.MODERATE: [],
        TaskComplexity.COMPLEX: []
    }
    
    for prompt, expected in test_cases:
        actual = orchestrator.classify_task(prompt)
        is_correct = actual == expected
        correct += is_correct
        
        status = "✓" if is_correct else "✗"
        results_by_complexity[expected].append({
            "prompt": prompt,
            "expected": expected,
            "actual": actual,
            "correct": is_correct
        })
        
        expected_str = expected.name if hasattr(expected, 'name') else str(expected)
        actual_str = actual.name if hasattr(actual, 'name') else str(actual)
        
        print(f"{status} {prompt[:50]:<50} | Expected: {expected_str:<8} | Got: {actual_str:<8}")
    
    print(f"\n{'─' * 75}")
    print(f"Classification Accuracy: {correct}/{total} ({100 * correct / total:.1f}%)\n")
    
    # Test model selection
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                     MODEL SELECTION TEST                          ║")
    print("╚═══════════════════════════════════════════════════════════════════╝\n")
    
    model_tests = [
        ("Write a docstring", TaskComplexity.SIMPLE, "qwen2.5-coder:1.5b"),
        ("Refactor this code", TaskComplexity.MODERATE, "qwen2.5-coder:7b-instruct-q8_0"),
        ("Implement a REST API", TaskComplexity.COMPLEX, "qwen2.5-coder:7b-instruct-q8_0"),
    ]
    
    for prompt, expected_complexity, expected_model in model_tests:
        complexity = orchestrator.classify_task(prompt)
        gpu_endpoint, model, gpu_name = orchestrator.select_gpu_and_model(complexity)
        
        complexity_correct = complexity == expected_complexity
        model_correct = model == expected_model
        all_correct = complexity_correct and model_correct
        
        status = "✓" if all_correct else "✗"
        complexity_str = complexity.name if hasattr(complexity, 'name') else str(complexity)
        
        print(f"{status} Prompt: {prompt[:40]:<40}")
        print(f"   Complexity: {complexity_str:<10} (expected {expected_complexity.name})")
        print(f"   Model: {model} (expected {expected_model})")
        print(f"   GPU: {gpu_name}\n")
    
    # Summary
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                          SUMMARY                                  ║")
    print("╚═══════════════════════════════════════════════════════════════════╝\n")
    
    for complexity in [TaskComplexity.SIMPLE, TaskComplexity.MODERATE, TaskComplexity.COMPLEX]:
        results = results_by_complexity[complexity]
        correct_count = sum(1 for r in results if r["correct"])
        total_count = len(results)
        accuracy = 100 * correct_count / total_count if total_count > 0 else 0
        
        complexity_str = complexity.name if hasattr(complexity, 'name') else str(complexity)
        print(f"{complexity_str:<10} tasks: {correct_count}/{total_count} correct ({accuracy:.0f}%)")
    
    print(f"\n{'─' * 75}")
    print(f"Overall Accuracy: {100 * correct / total:.1f}%")
    
    if correct >= total * 0.8:  # 80% threshold
        print(f"\n✅ TESTS PASSED ({100 * correct / total:.0f}% accuracy) - Routing logic is working!")
        return 0
    else:
        print(f"\n⚠️  Only {100 * correct / total:.0f}% accuracy - Review classification logic")
        return 1

if __name__ == "__main__":
    sys.exit(test_classification())
