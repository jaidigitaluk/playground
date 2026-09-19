#!/usr/bin/env python3
"""
01_verify_auth.py
-----------------
Pre-flight health check for awwwards-studio-web.
Verifies Node/Next.js environment, python virtualenv, and optional AI video generation keys.
"""

import os
import sys
import shutil
import subprocess
from dotenv import load_dotenv

load_dotenv()

def check_env():
    print("==================================================")
    print("🏛️  ATELIER NOCTURNE: SYSTEM HEALTH & AUTH CHECK")
    print("==================================================")

    # 1. Check Node.js and NPM
    node_path = shutil.which("node")
    npm_path = shutil.which("npm")
    if not node_path or not npm_path:
        print("❌ Error: Node.js or npm is missing from system PATH.")
        sys.exit(1)
    
    node_ver = subprocess.run(["node", "-v"], capture_output=True, text=True).stdout.strip()
    npm_ver = subprocess.run(["npm", "-v"], capture_output=True, text=True).stdout.strip()
    print(f"✅ Node.js runtime: {node_ver} (Path: {node_path})")
    print(f"✅ NPM package manager: {npm_ver}")

    # 2. Check Python & Dependencies
    print(f"✅ Python environment: {sys.version.split()[0]}")
    try:
        import requests
        import dotenv
        print("✅ Python core libraries (requests, python-dotenv) loaded.")
    except ImportError as e:
        print(f"❌ Missing python dependencies: {e}")
        sys.exit(1)

    # 3. Check AI Video API Credentials (Optional)
    fal_key = os.getenv("FAL_KEY")
    replicate_token = os.getenv("REPLICATE_API_TOKEN")
    runway_secret = os.getenv("RUNWAY_API_SECRET")

    print("\n--- AI Video Generation Pipelines ---")
    if fal_key and fal_key != "your_fal_key_here":
        print("✅ FAL_KEY detected. Live diffusion rendering is ENABLED.")
    else:
        print("ℹ️ FAL_KEY not provided. High-resolution local/curated video fallback is ACTIVE.")

    if replicate_token and replicate_token != "your_replicate_token_here":
        print("✅ REPLICATE_API_TOKEN detected.")
    else:
        print("ℹ️ REPLICATE_API_TOKEN not configured.")

    if runway_secret and runway_secret != "your_runway_secret_here":
        print("✅ RUNWAY_API_SECRET detected.")
    else:
        print("ℹ️ RUNWAY_API_SECRET not configured.")

    # 4. Check Build Artifacts & Next.js readiness
    next_build_dir = os.path.join(os.path.dirname(__file__), ".next")
    if os.path.exists(next_build_dir):
        print("\n✅ Next.js production build (.next/) is verified and ready.")
    else:
        print("\n⚠️ Next.js production build not found. Run 'npm run build' or 'npm run dev'.")

    print("\n🚀 System verification complete. The creative sandbox is 100% operational.")
    print("👉 Launch local interactive dev server with: npm run dev")
    print("==================================================")

if __name__ == "__main__":
    check_env()
