# Demo Showcase - Interactive Demonstrations

This script provides interactive demonstrations of local AI models in action.

## Quick Start

### Interactive Mode (Default)
```bash
cd ~/copilot-bridge
python3 demo_showcase.py
```

### Run All Demos
```bash
python3 demo_showcase.py --all
```

### Run Specific Demo
```bash
python3 demo_showcase.py 1    # Run demo #1 only
python3 demo_showcase.py 5    # Run demo #5 only
```

## Available Demonstrations

### 1. 📝 Generate Documentation
- Generates Google-style docstrings
- Adds proper Args, Returns, Raises sections
- Perfect for documenting existing code

### 2. 🔍 Code Explanation
- Explains complex algorithms step-by-step
- Includes time/space complexity analysis
- Helps understand unfamiliar code

### 3. 📄 Text Summarization
- Condenses long documentation
- Extracts key information
- Creates concise summaries

### 4. ❓ Question & Answer
- Answers technical questions
- Explains concepts
- Provides accurate information

### 5. 💻 Code Generation
- Creates code from specifications
- Includes error handling
- Adds inline comments

### 6. 🐛 Bug Detection
- Identifies bugs and issues
- Explains potential problems
- Suggests fixes

### 7. 🏷️ Add Type Hints
- Adds Python type annotations
- Includes necessary imports
- Improves code quality

### 8. ♻️ Code Refactoring
- Makes code more Pythonic
- Improves efficiency
- Follows best practices

## Example Usage

### Interactive Menu
```bash
$ python3 demo_showcase.py

Available Demos:
  1. Generate Documentation (docstrings)
  2. Code Explanation (algorithms)
  3. Text Summarization
  4. Question & Answer
  5. Code Generation
  6. Bug Detection
  7. Add Type Hints
  8. Code Refactoring
  9. Run ALL demos
  0. Exit

Select demo (0-9): 1
```

### Batch Run All
```bash
$ python3 demo_showcase.py --all

********************************************************************
  LOCAL AI MODELS DEMONSTRATION
  Running on: http://192.168.1.138:11434
  Model: qwen2.5-coder:7b-instruct-q8_0
  Time: 2025-10-19 00:15:00
********************************************************************

======================================================================
                    Demo 1: Generate Documentation
======================================================================

Task: Add Google-style docstring to this function:

def process_user_data(user_id, email, age, preferences=None):
    ...

Calling local model...

Response:
    """
    Process and normalize user data.
    
    Args:
        user_id (int): The unique identifier for the user.
        email (str): The user's email address.
        age (int): The user's age.
        preferences (dict, optional): User preferences. Defaults to None.
    
    Returns:
        dict: A dictionary containing normalized user data.
    """

⏱️  Time: 3.45s | Cost: $0.00 | Model: qwen2.5-coder:7b-instruct-q8_0
```

## Performance Metrics

All demos run on **local Ollama instance**:
- **Server:** 192.168.1.138:11434
- **Model:** qwen2.5-coder:7b-instruct-q8_0 (8.1 GB)
- **Avg Response:** 3-5 seconds
- **Cost:** $0.00 per request

## Requirements

- Python 3.10+
- httpx (`pip install httpx`)
- Ollama running on 192.168.1.138:11434
- Model: qwen2.5-coder:7b-instruct-q8_0

## Features

✅ **Interactive Menu** - Choose demos individually  
✅ **Batch Mode** - Run all demos sequentially  
✅ **Color Output** - Pretty, readable results  
✅ **Timing Info** - See response times  
✅ **Cost Tracking** - Always $0 (local processing)  
✅ **Real Examples** - Practical use cases  

## Tips

- Press **Enter** between demos in --all mode
- Press **Ctrl+C** to stop at any time
- Each demo is independent
- Results may vary slightly between runs

## Customization

Edit `demo_showcase.py` to:
- Change the Ollama server URL
- Use different models
- Add your own demo scenarios
- Modify prompts for your use case

Enjoy exploring local AI capabilities! 🚀
