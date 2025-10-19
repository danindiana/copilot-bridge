#!/usr/bin/env python3
"""
Interactive Demo: Local AI Models in Action
============================================

Demonstrates various use cases:
1. Code documentation (docstrings, comments)
2. Code explanation and analysis
3. Text summarization
4. Q&A and information retrieval
5. Code generation
6. Bug detection

All running on LOCAL Ollama instance - $0 cost!
"""

import json
import httpx
import asyncio
import sys
from datetime import datetime

# Configuration
OLLAMA_BASE = "http://192.168.1.138:11434"
MODEL = "qwen2.5-coder:7b-instruct-q8_0"

# ANSI color codes for pretty output
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

async def call_local_model(prompt: str, model: str = MODEL) -> tuple[str, float]:
    """Call the local Ollama model and return response + time."""
    import time
    t0 = time.time()
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{OLLAMA_BASE}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
    
    elapsed = time.time() - t0
    result = response.json()
    return result.get("response", ""), elapsed

def print_header(title: str):
    """Print a fancy section header."""
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{title.center(70)}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

def print_result(response: str, elapsed: float):
    """Print the model response with timing info."""
    print(f"{GREEN}Response:{RESET}\n{response}")
    print(f"\n{YELLOW}⏱️  Time: {elapsed:.2f}s | Cost: $0.00 | Model: {MODEL}{RESET}")

async def demo_1_docstring():
    """Demo: Generate Google-style docstring."""
    print_header("Demo 1: Generate Documentation")
    
    code = """
def process_user_data(user_id, email, age, preferences=None):
    if not preferences:
        preferences = {}
    data = {
        'id': user_id,
        'email': email.lower(),
        'age': age,
        'prefs': preferences
    }
    return data
"""
    
    print(f"{BOLD}Task:{RESET} Add Google-style docstring to this function:\n")
    print(code)
    
    prompt = f"Add a comprehensive Google-style docstring to this Python function:\n\n{code}\n\nProvide ONLY the docstring text, no other explanation."
    
    print(f"\n{YELLOW}Calling local model...{RESET}")
    response, elapsed = await call_local_model(prompt)
    print_result(response, elapsed)

async def demo_2_explain():
    """Demo: Explain complex code."""
    print_header("Demo 2: Code Explanation")
    
    code = """
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
"""
    
    print(f"{BOLD}Task:{RESET} Explain how this algorithm works:\n")
    print(code)
    
    prompt = f"Explain step-by-step how this quicksort implementation works, including time complexity:\n\n{code}"
    
    print(f"\n{YELLOW}Calling local model...{RESET}")
    response, elapsed = await call_local_model(prompt)
    print_result(response, elapsed)

async def demo_3_summarize():
    """Demo: Summarize text/documentation."""
    print_header("Demo 3: Text Summarization")
    
    text = """
Python's asyncio library provides infrastructure for writing single-threaded concurrent 
code using coroutines, multiplexing I/O access over sockets and other resources, running 
network clients and servers, and other related primitives. It is often a perfect fit for 
IO-bound and high-level structured network code. asyncio provides a set of high-level APIs 
to run Python coroutines concurrently, perform network IO and IPC, control subprocesses, 
distribute tasks via queues, and synchronize concurrent code. Additionally, there are 
low-level APIs for library and framework developers to access transport and protocol 
abstractions, implement new event loop implementations, and create custom policy objects.
"""
    
    print(f"{BOLD}Task:{RESET} Summarize this technical documentation:\n")
    print(text)
    
    prompt = f"Provide a concise 2-sentence summary of this text:\n\n{text}"
    
    print(f"\n{YELLOW}Calling local model...{RESET}")
    response, elapsed = await call_local_model(prompt)
    print_result(response, elapsed)

async def demo_4_qa():
    """Demo: Question answering."""
    print_header("Demo 4: Question & Answer")
    
    question = "What is the difference between TCP and UDP protocols?"
    
    print(f"{BOLD}Question:{RESET} {question}\n")
    
    prompt = f"Answer this question concisely and accurately:\n\n{question}"
    
    print(f"\n{YELLOW}Calling local model...{RESET}")
    response, elapsed = await call_local_model(prompt)
    print_result(response, elapsed)

async def demo_5_code_gen():
    """Demo: Generate code from description."""
    print_header("Demo 5: Code Generation")
    
    spec = "Create a Python function that validates an email address using regex. Include error handling."
    
    print(f"{BOLD}Specification:{RESET} {spec}\n")
    
    prompt = f"Write Python code for: {spec}\n\nProvide only the code with inline comments."
    
    print(f"\n{YELLOW}Calling local model...{RESET}")
    response, elapsed = await call_local_model(prompt)
    print_result(response, elapsed)

async def demo_6_bug_detection():
    """Demo: Find bugs in code."""
    print_header("Demo 6: Bug Detection")
    
    code = """
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

result = calculate_average([])
print(result)
"""
    
    print(f"{BOLD}Task:{RESET} Find bugs in this code:\n")
    print(code)
    
    prompt = f"Identify all bugs and potential issues in this code:\n\n{code}\n\nExplain each issue and suggest fixes."
    
    print(f"\n{YELLOW}Calling local model...{RESET}")
    response, elapsed = await call_local_model(prompt)
    print_result(response, elapsed)

async def demo_7_type_hints():
    """Demo: Add type hints."""
    print_header("Demo 7: Add Type Hints")
    
    code = """
def fetch_user_profile(user_id, include_posts=False):
    profile = database.get_user(user_id)
    if include_posts:
        profile['posts'] = database.get_posts(user_id)
    return profile
"""
    
    print(f"{BOLD}Task:{RESET} Add complete type hints:\n")
    print(code)
    
    prompt = f"Add Python type hints to this function. Include imports if needed:\n\n{code}\n\nProvide only the updated code."
    
    print(f"\n{YELLOW}Calling local model...{RESET}")
    response, elapsed = await call_local_model(prompt)
    print_result(response, elapsed)

async def demo_8_refactor():
    """Demo: Refactor code."""
    print_header("Demo 8: Code Refactoring")
    
    code = """
def process_data(data):
    result = []
    for item in data:
        if item != None:
            if item > 0:
                result.append(item * 2)
    return result
"""
    
    print(f"{BOLD}Task:{RESET} Refactor to be more Pythonic:\n")
    print(code)
    
    prompt = f"Refactor this code to be more Pythonic and efficient:\n\n{code}\n\nProvide the improved code with a brief explanation."
    
    print(f"\n{YELLOW}Calling local model...{RESET}")
    response, elapsed = await call_local_model(prompt)
    print_result(response, elapsed)

async def run_all_demos():
    """Run all demos sequentially."""
    print(f"\n{BOLD}{GREEN}{'*'*70}")
    print(f"  LOCAL AI MODELS DEMONSTRATION")
    print(f"  Running on: {OLLAMA_BASE}")
    print(f"  Model: {MODEL}")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'*'*70}{RESET}")
    
    demos = [
        demo_1_docstring,
        demo_2_explain,
        demo_3_summarize,
        demo_4_qa,
        demo_5_code_gen,
        demo_6_bug_detection,
        demo_7_type_hints,
        demo_8_refactor,
    ]
    
    total_time = 0
    for i, demo in enumerate(demos, 1):
        try:
            import time
            t0 = time.time()
            await demo()
            elapsed = time.time() - t0
            total_time += elapsed
            
            print(f"\n{BLUE}{'─'*70}{RESET}")
            print(f"{BLUE}Demo {i}/{len(demos)} complete! Press Enter for next demo (or Ctrl+C to exit)...{RESET}")
            input()
            
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}Demo interrupted by user.{RESET}")
            break
        except Exception as e:
            print(f"\n{RED}Error in demo: {e}{RESET}")
    
    print(f"\n{BOLD}{GREEN}{'='*70}")
    print(f"  DEMONSTRATION COMPLETE!")
    print(f"  Total demos run: {i}")
    print(f"  Total time: {total_time:.1f}s")
    print(f"  Total cost: $0.00 (100% local processing)")
    print(f"{'='*70}{RESET}\n")

async def run_single_demo(demo_num: int):
    """Run a specific demo by number."""
    demos = {
        1: demo_1_docstring,
        2: demo_2_explain,
        3: demo_3_summarize,
        4: demo_4_qa,
        5: demo_5_code_gen,
        6: demo_6_bug_detection,
        7: demo_7_type_hints,
        8: demo_8_refactor,
    }
    
    if demo_num in demos:
        await demos[demo_num]()
    else:
        print(f"{RED}Invalid demo number. Choose 1-8.{RESET}")

def print_menu():
    """Print the demo menu."""
    print(f"\n{BOLD}{BLUE}Available Demos:{RESET}")
    print(f"  1. Generate Documentation (docstrings)")
    print(f"  2. Code Explanation (algorithms)")
    print(f"  3. Text Summarization")
    print(f"  4. Question & Answer")
    print(f"  5. Code Generation")
    print(f"  6. Bug Detection")
    print(f"  7. Add Type Hints")
    print(f"  8. Code Refactoring")
    print(f"  9. Run ALL demos")
    print(f"  0. Exit")
    print()

async def interactive_mode():
    """Interactive menu-driven demo."""
    while True:
        print_menu()
        choice = input(f"{BOLD}Select demo (0-9): {RESET}").strip()
        
        if choice == "0":
            print(f"\n{GREEN}Goodbye!{RESET}\n")
            break
        elif choice == "9":
            await run_all_demos()
        elif choice.isdigit() and 1 <= int(choice) <= 8:
            await run_single_demo(int(choice))
            print(f"\n{BLUE}{'─'*70}{RESET}")
        else:
            print(f"{RED}Invalid choice. Please enter 0-9.{RESET}")

def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            asyncio.run(run_all_demos())
        elif sys.argv[1].isdigit():
            demo_num = int(sys.argv[1])
            asyncio.run(run_single_demo(demo_num))
        else:
            print(f"Usage: {sys.argv[0]} [--all | 1-8]")
            print(f"  No args: Interactive mode")
            print(f"  --all: Run all demos")
            print(f"  1-8: Run specific demo")
    else:
        asyncio.run(interactive_mode())

if __name__ == "__main__":
    main()
