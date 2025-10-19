#!/usr/bin/env python3
"""Generate project summary using gpt-oss-20b"""
import json
import httpx
import time

PROMPT = """We just built a copilot-bridge project with these components:

1. A hybrid routing bridge that routes AI requests intelligently - cheap tasks go to LOCAL Ollama, complex tasks go to GitHub Copilot

2. An interactive demo showcase with 8 demonstrations: Generate documentation, Code explanation, Text summarization, Question & answer, Code generation, Bug detection, Add type hints, Code refactoring

3. Full documentation suite with quickstart, demo guide, and POC results

4. Git repository with 4 commits, 9 tracked files, 1411 lines total

The project runs on local Ollama using qwen2.5-coder:7b model. Response times: 3-5 seconds, Cost: $0.00 per request. Successfully integrated with Continue.dev in VS Code.

Write a compelling 3-paragraph project summary highlighting key achievements and benefits."""

print("🤖 Generating summary with gpt-oss-20b (20.9B parameters)...")
print("⏱️  This may take 30-60 seconds...\n")

t0 = time.time()

with httpx.Client(timeout=120.0) as client:
    response = client.post(
        "http://192.168.1.138:11434/api/generate",
        json={
            "model": "gpt-oss:20b",
            "prompt": PROMPT,
            "stream": False
        }
    )

elapsed = time.time() - t0
result = response.json()
summary = result.get("response", "")

print("═"*70)
print("GPT-OSS-20B GENERATED SUMMARY")
print("═"*70)
print()
print(summary)
print()
print("─"*70)
print(f"⏱️  Generation time: {elapsed:.1f}s")
print(f"💰 Cost: $0.00")
print(f"🤖 Model: gpt-oss:20b (20.9B parameters, MXFP4)")
print(f"📊 Context length: 131K tokens")
print("═"*70)
