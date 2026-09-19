# awwwards-studio-web

> Isolated sandbox for testing and verifying awwwards-studio-web integrations.

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
