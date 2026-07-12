"""Full pipeline: decompose script -> generate images -> generate videos using Agnes AI."""
from __future__ import annotations
import asyncio, json, os, sys
import httpx

API_KEY = os.getenv("AGNES_API_KEY", "")
BASE_URL = "https://apihub.agnes-ai.com"
OUTPUT_DIR = "./output/pipeline"

async def call_chat(prompt: str, model: str = "agnes-2.0-flash") -> dict:
    async with httpx.AsyncClient(timeout=30, verify=False) as client:
        r = await client.post(f"{BASE_URL}/v1/chat/completions", headers={"Authorization": f"Bearer {API_KEY}"}, json={"model": model, "messages": [{"role": "user", "content": prompt}]})
        return r.json()

async def generate_image(prompt: str, name: str) -> str:
    async with httpx.AsyncClient(timeout=60, verify=False) as client:
        r = await client.post(f"{BASE_URL}/v1/images/generations", headers={"Authorization": f"Bearer {API_KEY}"}, json={"model": "agnes-image-2.1-flash", "prompt": prompt})
        url = r.json()["data"][0]["url"]
        img = await client.get(url)
        path = f"{OUTPUT_DIR}/{name}"
        with open(path, "wb") as f:
            f.write(img.content)
        return path

async def create_video(prompt: str, name: str) -> str:
    async with httpx.AsyncClient(timeout=30, verify=False) as client:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        cr = await client.post(f"{BASE_URL}/v1/videos", headers=headers, json={"model": "agnes-video-v2.0", "prompt": prompt})
        task_id = cr.json()["task_id"]
        print(f"  Video task {name}: {task_id}, polling...")
        for _ in range(120):
            qr = await client.get(f"{BASE_URL}/v1/videos/{task_id}", headers=headers)
            data = qr.json()
            if data.get("status") == "completed":
                url = data.get("metadata", {}).get("url", "")
                if url:
                    v = await client.get(url)
                    path = f"{OUTPUT_DIR}/{name}"
                    with open(path, "wb") as f:
                        f.write(v.content)
                    return path
            await asyncio.sleep(5)
        return "timeout"

async def main():
    if not API_KEY:
        print("Error: Set AGNES_API_KEY environment variable")
        return
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output: {OUTPUT_DIR}/")
    
    # Step 1: Read script
    script_path = "script/lastpiece.md"
    script = open(script_path, "r", encoding="utf-8").read()
    print(f"1. Loaded script: {len(script)} chars")
    
    # Step 2: Decompose with LLM
    print("2. Decomposing script...")
    decompose_prompt = f"Analyze this script and output JSON array of shots (shot_number, description, scene_type, duration, image_prompt):\n\n{script[:3000]}"
    result = await call_chat(decompose_prompt)
    shots_text = result["choices"][0]["message"]["content"]
    print(f"   Decomposition result: {len(shots_text)} chars")
    print(f"   Raw: {shots_text[:200]}...")
    
    # Step 3: Generate images for each shot
    print("3. Generating reference images...")
    for i in range(1, 7):
        name = f"shot_{i:02d}.png"
        prompt = f"Cinematic shot {i} of a cyberpunk Chinese New Year story"
        path = await generate_image(f"{prompt}, cinematic lighting, filmic quality", name)
        size = os.path.getsize(path)
        print(f"   Shot {i}: {path} ({size // 1024} KB)")
    
    # Step 4: Generate key video shots
    print("4. Generating key video shots...")
    for i, prompt in [(1, "Aerial view of cyberpunk city at night with one warm lit window"), (5, "Shot of boiling dumplings in a pot with steam rising")]:
        name = f"video_{i:02d}.mp4"
        print(f"   Creating video for shot {i}...")
        path = await create_video(prompt, name)
        print(f"   Shot {i}: {path}")
    
    print("Pipeline complete!")

if __name__ == "__main__":
    asyncio.run(main())
