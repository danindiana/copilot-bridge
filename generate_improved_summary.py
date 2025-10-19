#!/usr/bin/env python3
"""
Generate IMPROVED project summary using gpt-oss-20b with MORE context
Compares: minimal context (116 words) vs full context (~600 words)
"""
import json
import httpx
import time

# Full context from our documentation
with open('/tmp/full_context.txt', 'r') as f:
    full_context = f.read()

PROMPT = f"""{full_context}

Based on the above detailed project information, write a compelling 3-paragraph executive summary for this project. 

The summary should:
1. Highlight the technical innovation and architecture
2. Emphasize the comprehensive feature set and demonstrations
3. Focus on business value, cost savings, and real-world impact

Write in a professional, engaging style suitable for a project README or technical blog post."""

print("🤖 Generating IMPROVED summary with gpt-oss-20b (20.9B parameters)")
print("📊 Using FULL context (~600 words instead of 116)")
print("⏱️  This may take 30-90 seconds due to larger context...\n")

# Stats
words_in_prompt = len(PROMPT.split())
print(f"📥 INPUT CONTEXT: {words_in_prompt} words (~{int(words_in_prompt * 1.3)} tokens)")
print()

t0 = time.time()

with httpx.Client(timeout=180.0) as client:
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

words_in_output = len(summary.split())

print("═"*70)
print("GPT-OSS-20B IMPROVED SUMMARY (WITH FULL CONTEXT)")
print("═"*70)
print()
print(summary)
print()
print("─"*70)
print(f"📥 INPUT: {words_in_prompt} words (~{int(words_in_prompt * 1.3)} tokens)")
print(f"📤 OUTPUT: {words_in_output} words (~{int(words_in_output * 1.3)} tokens)")
print(f"⏱️  Generation time: {elapsed:.1f}s")
print(f"💰 Cost: $0.00")
print(f"🤖 Model: gpt-oss:20b (20.9B parameters, MXFP4)")
print(f"📊 Context used: 4096 tokens (current setting)")
print(f"📈 Max context: 131,072 tokens (capable)")
print("═"*70)

# Save for comparison
with open('/tmp/improved_summary.txt', 'w') as f:
    f.write(summary)
print(f"\n✅ Saved to: /tmp/improved_summary.txt")
