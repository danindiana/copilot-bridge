#!/usr/bin/env python3
import os, json, httpx, asyncio, sys, time
LOCAL = "http://192.168.1.138:11434"
GH    = "https://api.githubcopilot.com"
TOKEN = os.getenv("GITHUB_TOKEN") or sys.exit("export GITHUB_TOKEN")

async def main():
    payload = json.load(sys.stdin)
    msg     = payload.get("messages",[{}])[-1].get("content","")
    cheap   = any(w in msg.lower() for w in ("docstring","comment","lint","test","rename"))
    t0      = time.time()

    if cheap:
        # LOCAL route
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{LOCAL}/api/generate",
                                  json={"model":"qwen2.5-coder:7b-instruct","prompt":msg,"stream":False},
                                  timeout=30)
        print(json.dumps({"choices":[{"delta":{"content":r.json()["response"]}}]}))
        print(f"LOCAL  {len(msg.split())}w  {int((time.time()-t0)*1000)}ms", file=sys.stderr)
    else:
        # GITHUB route
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{GH}/chat/completions",
                                  headers={"Authorization":f"Bearer {TOKEN}"},
                                  json=payload, timeout=30)
        print(r.text)
        print(f"GITHUB {len(msg.split())}w  {int((time.time()-t0)*1000)}ms", file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(main())
