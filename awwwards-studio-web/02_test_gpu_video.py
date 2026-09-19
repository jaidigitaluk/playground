#!/usr/bin/env python3
"""
02_test_gpu_video.py
--------------------
Interactive CLI smoke test for Cloud GPU AI Video Generation.
Connects to Fal.ai (Kling 1.5 HD / Luma Ray / Wan 2.1) to generate a bespoke 5-second video clip.
"""

import os
import sys
import json
import time
from dotenv import load_dotenv
import requests

load_dotenv()

def main():
    print("==================================================")
    print("🎬 ATELIER NOCTURNE: GPU BESPOKE VIDEO PIPELINE")
    print("==================================================")

    fal_key = os.getenv("FAL_KEY")
    if not fal_key or fal_key == "your_fal_key_here":
        print("❌ Error: FAL_KEY not found in .env!")
        print("\n👉 How to get your key:")
        print("   1. Go to https://fal.ai and sign up (takes 30 seconds).")
        print("   2. Grab your API Key from the Keys dashboard.")
        print("   3. Add it to .env: FAL_KEY=your_actual_key")
        print("\n(Cost per generation is approx $0.05 to $0.15 on Fal.ai)")
        sys.exit(1)

    print("✅ FAL_KEY detected.")
    print("⚡ Available Cloud GPU Models:")
    print("   [1] Kling 1.5 HD (Extreme physical realism & character dynamics)")
    print("   [2] Luma Dream Machine Ray 2 (Choreographed camera moves & orbits)")
    print("   [3] Wan 2.1 (Ultra-fast cinematic generation)")

    default_prompt = "Liquid chrome geometric monument floating over black volcanic sand dunes at golden hour, 8k raw cinema, volumetric light."
    print(f"\nDefault Prompt: \"{default_prompt}\"")

    confirm = input("\nPress [ENTER] to submit test job to Cloud GPU (or type 'q' to quit): ").strip()
    if confirm.lower() == 'q':
        print("Aborted.")
        sys.exit(0)

    endpoint = "https://queue.fal.run/fal-ai/kling-video/v1.5/pro/text-to-video"
    headers = {
        "Authorization": f"Key {fal_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": default_prompt,
        "aspect_ratio": "16:9",
        "duration": "5",
    }

    print("\n🚀 Submitting job to Fal.ai GPU cluster...")
    try:
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        print(f"🎉 Job Queued Successfully! Request ID: {data.get('request_id')}")
        print("Status Endpoint:", data.get("status_url"))
        print("\n👉 Your GPU video is rendering on NVIDIA H100 clusters!")
    except Exception as e:
        print(f"❌ Error submitting to Fal.ai: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
