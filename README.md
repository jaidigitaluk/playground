# Integration & Tool Playground

Welcome to your isolated testing sandbox. This directory is reserved for experimenting with APIs, MCP servers, tools, and plugins **before** deploying them into production or client-facing projects.

---

## 🏛️ The Playground Operating Protocol

Every test project inside this playground strictly follows our 5-stage protocol:

1. **Isolation First**: Every test gets its own folder with dedicated `.env.example`, `.gitignore`, and dependencies. No polluting global packages or leaking secrets.
2. **Zero-Secret-Leakage**: Master `.gitignore` and per-project guards strictly block `.env`, `.env.*`, and sensitive keys from ever reaching GitHub.
3. **Clear File Taxonomy**:
   - `_system/`: Engine plumbing (API client, caching, spend guardrails). Setup once, rarely touch.
   - `_config/`: Catalogs, field pruning masks, endpoint metadata.
   - `01_...`, `02_...`: Working files that you actually edit and execute.
4. **Spend Guardrails & 24h Local Caching**:
   - Every API client hashes requests into `.cache/` (24h TTL) so you can tweak code/prompts without burning credits on repeated calls.
   - Hard budget stops prevent rogue agents from burning through account balances.
5. **Living Plan & Ledger (`PLAN.md`)**:
   - Every test project includes a `PLAN.md` tracking milestones, API quirks, and findings.

---

## 🚀 Scaffolding a New Test Project

Whenever you want to test a new integration (e.g., Stripe, Shopify, Pinecone, or a new MCP):

```bash
# Run the scaffolding generator
python3 scaffold.py <project-name> [--type=api|mcp|tool|plugin]

# Example:
python3 scaffold.py stripe-billing-test --type=api
```

This immediately spins up the complete folder structure with pre-configured `.gitignore`, `.env.example`, `requirements.txt`, `_system/`, and `PLAN.md`.

---

## 📁 Active Projects

| Project Folder | Type | Description | Status |
| :--- | :--- | :--- | :--- |
| [`dataforseo-test/`](./dataforseo-test/) | Hybrid API + MCP Engine | Full enterprise SEO & AI Overview blueprint engine with copywriter brief & JSON-LD schema | **Verified & Battle-Tested** (Phases 1–4.6 complete; Ready for Skill packaging) |
