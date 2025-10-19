#!/usr/bin/env python3
"""
Interactive Refactoring Quality Test Runner

Tests local vs cloud models on realistic refactoring tasks.
Shows token counts, asks for consent, measures quality.
"""
import sys
import time
import json
import argparse
from datetime import datetime
from pathlib import Path
import httpx

# Import test samples
from test_samples import ALL_SAMPLES, CORPUS_STATS, get_sample

# Configuration
OLLAMA_BASE = "http://192.168.1.138:11434"
LOCAL_MODEL = "qwen2.5-coder:7b-instruct-q8_0"
RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

def estimate_tokens(text: str) -> int:
    """Estimate token count (~1.3 words per token)."""
    return int(len(text.split()) * 1.3)

def format_refactor_prompt(sample: dict) -> str:
    """Create refactoring prompt from sample."""
    goals_text = "\n".join(f"  {i+1}. {goal}" for i, goal in enumerate(sample["refactor_goals"]))
    
    return f"""Refactor the following Python code to improve quality:

ORIGINAL CODE:
{sample['code']}

REFACTORING GOALS:
{goals_text}

REQUIREMENTS:
- Preserve all functionality (code must still work)
- Add clear comments explaining changes
- Use modern Python 3.10+ idioms
- Add type hints where appropriate
- Ensure code is more readable and maintainable

Please provide the refactored code with explanations of changes made.
"""

def show_test_info(sample: dict, model_name: str):
    """Display token count and cost info before test."""
    prompt = format_refactor_prompt(sample)
    
    code_tokens = sample["tokens"]
    prompt_tokens = estimate_tokens(prompt)
    total_input = code_tokens + prompt_tokens
    expected_output = int(code_tokens * 1.2)  # Assume 20% longer with improvements
    total_tokens = total_input + expected_output
    
    is_local = "ollama" in model_name.lower() or model_name == LOCAL_MODEL
    cost = 0.0 if is_local else (total_tokens / 1000) * 0.02
    time_est = "5-8 seconds" if is_local else "2-4 seconds"
    
    print("╔" + "═"*76 + "╗")
    print("║" + f" REFACTORING TEST: {sample['name']}".ljust(76) + "║")
    print("╚" + "═"*76 + "╝")
    print()
    print(f"📝 Description: {sample['description']}")
    print(f"🎯 Category: {sample['category']}")
    print()
    print("📊 Token Analysis:")
    print(f"   • Sample code:      {code_tokens:5d} tokens")
    print(f"   • Refactor prompt:  {prompt_tokens:5d} tokens")
    print(f"   • Total input:      {total_input:5d} tokens")
    print(f"   • Expected output:  {expected_output:5d} tokens")
    print(f"   • TOTAL CONTEXT:    {total_tokens:5d} tokens")
    print()
    print("💰 Cost Estimate:")
    print(f"   • Model: {model_name}")
    if is_local:
        print(f"   • Cost: $0.000 (FREE - local inference)")
    else:
        print(f"   • Cost: ${cost:.3f} (${0.02:.2f} per 1K tokens)")
    print()
    print(f"⏱️  Expected Time: {time_est}")
    print()
    print("🎯 Refactoring Goals:")
    for i, goal in enumerate(sample["refactor_goals"], 1):
        print(f"   {i}. {goal}")
    print()
    
    return total_tokens

def ask_consent(total_tokens: int) -> bool:
    """Ask user if they want to proceed with test."""
    print("─"*78)
    response = input(f"Feed {total_tokens:,} tokens to the model? [y/N] ").strip().lower()
    return response in ['y', 'yes']

def run_local_refactor(sample: dict) -> dict:
    """Run refactoring test with local Ollama model."""
    prompt = format_refactor_prompt(sample)
    
    print(f"\n🤖 Running local model: {LOCAL_MODEL}")
    print("⏳ This may take 5-10 seconds...")
    
    start_time = time.time()
    
    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{OLLAMA_BASE}/api/generate",
                json={
                    "model": LOCAL_MODEL,
                    "prompt": prompt,
                    "stream": False
                }
            )
            result = response.json()
            refactored = result.get("response", "")
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    
    elapsed = time.time() - start_time
    
    print(f"✅ Complete in {elapsed:.1f}s")
    print()
    
    return {
        "model": LOCAL_MODEL,
        "model_type": "local",
        "elapsed_seconds": elapsed,
        "refactored_code": refactored,
        "timestamp": datetime.now().isoformat()
    }

def run_cloud_refactor(sample: dict) -> dict:
    """Run refactoring test with cloud model (placeholder)."""
    print(f"\n☁️  Running cloud model: GitHub Copilot")
    print("⚠️  Note: This is a placeholder - actual GitHub Copilot API integration required")
    print()
    
    return {
        "model": "github-copilot",
        "model_type": "cloud",
        "elapsed_seconds": 0,
        "refactored_code": "[CLOUD RESPONSE PLACEHOLDER - Implement GitHub Copilot API]",
        "timestamp": datetime.now().isoformat()
    }

def display_results(sample: dict, result: dict):
    """Show before/after comparison."""
    print("═"*78)
    print("REFACTORING RESULTS")
    print("═"*78)
    print()
    print("📥 ORIGINAL CODE:")
    print("─"*78)
    print(sample["code"][:500])  # Show first 500 chars
    if len(sample["code"]) > 500:
        print(f"\n... ({len(sample['code']) - 500} more characters)")
    print()
    print("📤 REFACTORED CODE:")
    print("─"*78)
    print(result["refactored_code"][:500])
    if len(result["refactored_code"]) > 500:
        print(f"\n... ({len(result['refactored_code']) - 500} more characters)")
    print()
    print("─"*78)
    print(f"⏱️  Generation time: {result['elapsed_seconds']:.1f}s")
    print(f"🤖 Model: {result['model']} ({result['model_type']})")
    print()

def score_refactoring(sample: dict, result: dict) -> dict:
    """Prompt user to score the refactoring quality."""
    print("═"*78)
    print("QUALITY SCORING")
    print("═"*78)
    print()
    print("Please rate the refactoring on these dimensions (0-10):")
    print()
    
    scores = {}
    
    # Correctness
    print("1. CORRECTNESS (0=broken, 5=has bugs, 10=perfect)")
    print("   Does the code still work? Any regressions?")
    scores["correctness"] = int(input("   Score [0-10]: ").strip() or "5")
    print()
    
    # Readability
    print("2. READABILITY (1=worse, 5=no change, 10=much better)")
    print("   Is it easier to understand than the original?")
    scores["readability"] = int(input("   Score [1-10]: ").strip() or "5")
    print()
    
    # Pythonic
    print("3. PYTHONIC (1=still bad, 5=okay, 10=textbook Python)")
    print("   Uses modern idioms, type hints, best practices?")
    scores["pythonic"] = int(input("   Score [1-10]: ").strip() or "5")
    print()
    
    # Completeness
    print("4. COMPLETENESS (1=almost nothing, 5=half, 10=all goals met)")
    print("   How many of the refactoring goals were addressed?")
    scores["completeness"] = int(input("   Score [1-10]: ").strip() or "5")
    print()
    
    # Calculate overall (weighted average)
    overall = (
        scores["correctness"] * 0.4 +
        scores["readability"] * 0.2 +
        scores["pythonic"] * 0.2 +
        scores["completeness"] * 0.2
    )
    scores["overall"] = round(overall, 1)
    
    print(f"📊 OVERALL SCORE: {scores['overall']}/10")
    print()
    
    # Optional notes
    print("Optional: Any notes about the refactoring?")
    notes = input("Notes (or press Enter to skip): ").strip()
    if notes:
        scores["notes"] = notes
    
    return scores

def save_results(sample: dict, result: dict, scores: dict):
    """Save test results to JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = RESULTS_DIR / f"test_{sample['name'].replace('.py', '')}_{result['model_type']}_{timestamp}.json"
    
    data = {
        "sample": sample,
        "result": result,
        "scores": scores,
        "test_metadata": {
            "timestamp": datetime.now().isoformat(),
            "sample_tokens": sample["tokens"],
            "model": result["model"],
            "elapsed_seconds": result["elapsed_seconds"]
        }
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"💾 Results saved to: {filename}")
    print()

def run_single_test(sample_name: str, model: str, interactive: bool = True):
    """Run a single refactoring test."""
    sample = get_sample(sample_name)
    if not sample:
        print(f"❌ Sample not found: {sample_name}")
        return
    
    # Show token info
    total_tokens = show_test_info(sample, model)
    
    # Ask for consent if interactive
    if interactive:
        if not ask_consent(total_tokens):
            print("❌ Test cancelled by user")
            return
    
    # Run the test
    if model == "local":
        result = run_local_refactor(sample)
    elif model == "cloud":
        result = run_cloud_refactor(sample)
    else:
        print(f"❌ Unknown model: {model}")
        return
    
    if not result:
        print("❌ Test failed")
        return
    
    # Display results
    display_results(sample, result)
    
    # Score quality
    if interactive:
        scores = score_refactoring(sample, result)
        save_results(sample, result, scores)
    else:
        print("⚠️  Skipping quality scoring (non-interactive mode)")

def run_all_tests(models: list, interactive: bool = True):
    """Run all refactoring tests."""
    print("╔" + "═"*76 + "╗")
    print("║" + " "*23 + "FULL TEST SUITE" + " "*38 + "║")
    print("╚" + "═"*76 + "╝")
    print()
    print(f"📊 Corpus Summary:")
    print(f"   • Samples: {CORPUS_STATS['total_samples']}")
    print(f"   • Total tokens: {CORPUS_STATS['total_tokens']:,}")
    print(f"   • Models to test: {', '.join(models)}")
    print()
    
    if interactive:
        response = input("Proceed with full test suite? [y/N] ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ Test suite cancelled")
            return
    
    total_tests = len(ALL_SAMPLES) * len(models)
    completed = 0
    
    for sample in ALL_SAMPLES:
        for model in models:
            completed += 1
            print(f"\n{'='*78}")
            print(f"TEST {completed}/{total_tests}")
            print('='*78)
            run_single_test(sample["name"], model, interactive=False)
            
            # Brief pause between tests
            if completed < total_tests:
                time.sleep(2)
    
    print("\n" + "═"*78)
    print("✅ ALL TESTS COMPLETE")
    print("═"*78)
    print(f"\nResults saved in: {RESULTS_DIR}")
    print("\nNext step: Run `python3 compare_results.py` to analyze")

def main():
    parser = argparse.ArgumentParser(description="Refactoring Quality Test Runner")
    parser.add_argument("--sample", help="Sample name to test (e.g., legacy_login.py)")
    parser.add_argument("--model", default="local", choices=["local", "cloud"],
                       help="Model to use (local or cloud)")
    parser.add_argument("--all", action="store_true", help="Run all samples")
    parser.add_argument("--models", default="local", help="Comma-separated models for --all")
    parser.add_argument("--interactive", action="store_true", default=True,
                       help="Ask for confirmation before tests")
    parser.add_argument("--batch", action="store_true", help="Run in batch mode (no interaction)")
    
    args = parser.parse_args()
    
    # Adjust interactive mode
    interactive = args.interactive and not args.batch
    
    if args.all:
        models = args.models.split(',')
        run_all_tests(models, interactive=interactive)
    elif args.sample:
        run_single_test(args.sample, args.model, interactive=interactive)
    else:
        # Interactive mode: show menu
        print("╔" + "═"*76 + "╗")
        print("║" + " "*17 + "REFACTORING QUALITY TEST RUNNER" + " "*28 + "║")
        print("╚" + "═"*76 + "╝")
        print()
        print("Available samples:")
        for i, sample in enumerate(ALL_SAMPLES, 1):
            print(f"  {i}. {sample['name']:25s} ({sample['tokens']:4d} tokens, {sample['category']})")
        print()
        print("  A. Run all samples")
        print("  Q. Quit")
        print()
        
        choice = input("Select sample (1-6, A, or Q): ").strip().upper()
        
        if choice == 'Q':
            print("Goodbye!")
            return
        elif choice == 'A':
            run_all_tests([args.model], interactive=True)
        elif choice.isdigit() and 1 <= int(choice) <= len(ALL_SAMPLES):
            sample = ALL_SAMPLES[int(choice) - 1]
            run_single_test(sample["name"], args.model, interactive=True)
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
