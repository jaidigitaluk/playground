#!/usr/bin/env python3
"""
Playground Scaffolding Generator
================================
Usage:
    python3 scaffold.py <project-name> [--type=api|mcp|tool|plugin]

Generates a standardized, production-grade test environment in /playground:
- Clear separation: _system/ (engine/plumbing) vs working files (01_..., 02_...)
- Automatic secret protection (.gitignore & .env.example)
- Living PLAN.md tracking ledger
- Zero-cost caching & budget guardrail skeleton
"""

import sys
import os
import argparse
from pathlib import Path

def create_scaffold(project_name: str, proj_type: str = "api"):
    root_dir = Path(__file__).resolve().parent
    target_dir = root_dir / project_name

    if target_dir.exists():
        print(f"❌ Error: Directory '{project_name}' already exists.")
        sys.exit(1)

    print(f"🚀 Scaffolding new playground project: {project_name} (type: {proj_type})")

    # Define standard directories
    subdirs = [
        "_system",
        "_config",
        "output/reports",
        "output/debug",
        ".cache",
    ]

    for sd in subdirs:
        (target_dir / sd).mkdir(parents=True, exist_ok=True)

    # 1. Project .gitignore
    gitignore_content = """# Secret & runtime ignore
.env
.env.*
!.env.example
*.key
*.pem
credentials.json
__pycache__/
venv/
.venv/
.cache/
*.sqlite
*.db
*.log
"""
    (target_dir / ".gitignore").write_text(gitignore_content.strip() + "\n")

    # 2. .env.example
    env_example_content = f"""# Credentials for {project_name}
# COPY THIS FILE TO .env AND FILL IN YOUR ACTUAL CREDENTIALS

API_KEY=your_api_key_here
API_SECRET=your_api_secret_here

# Spend Guardrails & Caching
MAX_BUDGET_USD_PER_RUN=0.20
CACHE_TTL_HOURS=24
ENABLE_CACHE=true
"""
    (target_dir / ".env.example").write_text(env_example_content.strip() + "\n")

    # 3. requirements.txt
    reqs_content = """requests>=2.31.0
python-dotenv>=1.0.0
pydantic>=2.5.0
rich>=13.7.0
"""
    (target_dir / "requirements.txt").write_text(reqs_content.strip() + "\n")

    # 4. _system/__init__.py
    (target_dir / "_system" / "__init__.py").write_text('"""Internal system infrastructure."""\n')

    # 5. README.md
    readme_content = f"""# {project_name}

> Isolated sandbox for testing and verifying {project_name} integrations.

## Directory Structure
- `_system/`: Core plumbing, API clients, cache handlers, and security guardrails (Setup once, rarely touch).
- `_config/`: Schemas, endpoint definitions, and static lookup tables.
- `01_verify_auth.py`: Initial connectivity and authentication smoke test.
- `output/`: Output deliverables, reports, and debugging dumps.
- `PLAN.md`: Living task roadmap and test ledger.

## Quickstart
1. Set up your virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Configure credentials:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```
3. Run the initial health check:
   ```bash
   python3 01_verify_auth.py
   ```
"""
    (target_dir / "README.md").write_text(readme_content.strip() + "\n")

    # 6. PLAN.md
    plan_content = f"""# Implementation & Test Plan: {project_name}

## Objective
Establish a reliable, cost-controlled testbed for {project_name} before integrating into downstream production codebases.

## Roadmap & Milestones
- [ ] Phase 1: Environment & Credential Setup (.env configured, venv installed)
- [ ] Phase 2: Smoke Test & Connectivity (`01_verify_auth.py` passes)
- [ ] Phase 3: Core Integration Testing & Payload Inspection
- [ ] Phase 4: Output Synthesis & Client-Ready Report Generation
- [ ] Phase 5: Portability Checklist (Packaging into reusable Skill / Module)

## Notes, Quirks & Learnings
- *Log API quirks, latency patterns, and gotchas here as you discover them.*
"""
    (target_dir / "PLAN.md").write_text(plan_content.strip() + "\n")

    # 7. Initial Working File: 01_verify_auth.py
    verify_script = f"""#!/usr/bin/env python3
\"\"\"
01_verify_auth.py
-----------------
Smoke test to verify credentials and connectivity for {project_name}.
\"\"\"
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def main():
    print("🔍 Checking environment variables for {project_name}...")
    api_key = os.getenv("API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("❌ Error: API_KEY is missing or unconfigured in .env!")
        print("👉 Please edit .env with your actual credentials before running tests.")
        sys.exit(1)
    print("✅ Environment variables detected.")
    print("🚀 Ready to test connectivity.")

if __name__ == "__main__":
    main()
"""
    (target_dir / "01_verify_auth.py").write_text(verify_script.strip() + "\n")
    os.chmod(target_dir / "01_verify_auth.py", 0o755)

    # 8. Gitkeep in output dirs
    (target_dir / "output" / "reports" / ".gitkeep").touch()
    (target_dir / "output" / "debug" / ".gitkeep").touch()

    # 9. AGENTS.md & GEMINI.md (Persistent Context & Instructions)
    agents_content = f"""# Agent Instructions & Context: {project_name}

## 🏛️ Project Role: Integration & Solutions Architect ({proj_type.upper()})

You are pair-programming with the USER in an isolated test environment for `{project_name}`.

### Core Working Principles
1. **Never Be a 'Yes-Man'**:
   - Actively audit and challenge assumptions if a proposed workflow misses industry best practices, security, or efficiency.
   - Propose robust architecture before writing code.
2. **File Taxonomy (Strict Separation)**:
   - `_system/`: Internal plumbing (client, caching, guardrails, git security). Setup once, rarely touch.
   - `_config/`: Catalogs, schemas, and static data.
   - Root working files (`01_verify_auth.py`, `02_...`): Where the user works, tests, and edits.
3. **Spend & Secret Guardrails**:
   - Always verify credentials and cost estimates before firing network calls.
   - Rely on local 24h caching where applicable.

---

## 🚦 Current Status & Next Steps
- [x] **Phase 1 Complete**: Project scaffolded with isolated venv and file taxonomy.
- [ ] **Phase 2 (Immediate Next Step)**:
  1. Ensure user has copied `.env.example` to `.env` and filled in credentials.
  2. Run `python3 01_verify_auth.py` to confirm connection and authentication.
- [ ] **Phase 3**: Write and execute numbered test scripts (`02_...`, `03_...`).
- [ ] **Phase 4**: Synthesize findings and log lessons in `PLAN.md`.

---

## 💬 Session Greeting Instruction
When the user starts a session:
- Greet them as their **Solutions Architect for {project_name}**.
- Confirm that Phase 1 scaffolding is ready.
- Check if `.env` is configured and offer to run `01_verify_auth.py` together.
"""
    (target_dir / "AGENTS.md").write_text(agents_content.strip() + "\n")
    try:
        os.symlink("AGENTS.md", target_dir / "GEMINI.md")
    except Exception:
        (target_dir / "GEMINI.md").write_text(agents_content.strip() + "\n")

    print(f"✨ Successfully scaffolded '{project_name}'.")
    print(f"📄 Generated AGENTS.md with persistent context.")
    print(f"📁 Location: {target_dir}")
    print(f"👉 Next steps: cd '{project_name}' && cp .env.example .env")

def main():
    parser = argparse.ArgumentParser(description="Scaffold a new playground test project.")
    parser.add_argument("name", help="Name of the test project folder")
    parser.add_argument("--type", choices=["api", "mcp", "tool", "plugin"], default="api", help="Integration type")
    args = parser.parse_args()

    create_scaffold(args.name, args.type)

if __name__ == "__main__":
    main()
