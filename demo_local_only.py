#!/usr/bin/env python3
"""
Simplified demo - LOCAL routing only (no GitHub token needed)
Shows the concept without requiring GitHub auth
"""
import json, httpx, asyncio, sys, time

LOCAL = "http://192.168.1.138:11434"

async def main():
    payload = json.load(sys.stdin)
    msg = payload.get("messages",[{}])[-1].get("content","")
    t0 = time.time()
    
    # Always route to LOCAL for demo
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{LOCAL}/api/generate",
                              json={"model":"qwen2.5-coder:7b-instruct-q8_0","prompt":msg,"stream":False},
                              timeout=30)
    
    response_text = r.json()["response"]
    print(json.dumps({"choices":[{"delta":{"content":response_text}}]}))
    elapsed_ms = int((time.time()-t0)*1000)
    print(f"LOCAL  {len(msg.split())}w  {elapsed_ms}ms", file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(main())
