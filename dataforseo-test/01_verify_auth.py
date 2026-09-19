#!/usr/bin/env python3
"""
01_verify_auth.py
-----------------
Smoke test to verify DataForSEO credentials and display account balance.
Does NOT consume credits (calls the free /v3/appendix/user_data endpoint).
"""

import os
import sys
from pathlib import Path

# Auto-reexecute using local virtual environment if not already active
_venv_python = Path(__file__).resolve().parent / "venv" / "bin" / "python3"
if _venv_python.exists() and sys.executable != str(_venv_python) and "VIRTUAL_ENV" not in os.environ:
    os.execv(str(_venv_python), [str(_venv_python)] + sys.argv)

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from _system.client import DataForSEOClient, DataForSEOAPIError

console = Console()

def main():
    console.print("\n[bold cyan]🔍 DataForSEO Pre-Flight Authentication Check[/bold cyan]")

    try:
        client = DataForSEOClient()
    except ValueError as e:
        console.print(Panel(
            f"[bold red]Configuration Missing:[/bold red]\n{str(e)}\n\n"
            "👉 Copy `.env.example` to `.env` inside `dataforseo-test/` and add your credentials.",
            title="Setup Error",
            border_style="red"
        ))
        sys.exit(1)

    console.print("⏳ Connecting to DataForSEO API...")
    try:
        user_data = client.get_user_data()
        tasks = user_data.get("tasks", [])
        if not tasks or not tasks[0].get("result"):
            console.print("[yellow]⚠️ Connected, but no account result returned.[/yellow]")
            return

        result = tasks[0]["result"][0]
        login = result.get("login")
        money_data = result.get("money", 0.0)
        if isinstance(money_data, dict):
            balance = float(money_data.get("balance", 0.0))
            total_deposited = float(money_data.get("total", balance))
        else:
            balance = float(money_data)
            total_deposited = balance
        rates = result.get("rates", {})

        table = Table(title="DataForSEO Account Status", show_header=True, header_style="bold green")
        table.add_column("Property", style="dim")
        table.add_column("Value", style="bold white")

        table.add_row("Account Login", str(login))
        table.add_row("Available Balance (USD)", f"${balance:.2f}")
        table.add_row("Total Deposited (USD)", f"${total_deposited:.2f}")
        table.add_row("API Status", "✅ Authenticated & Active")

        console.print(table)

        if balance < 1.0:
            console.print(f"[bold yellow]⚠️ Notice: Your balance is low (${balance:.2f}). Be mindful of live endpoint runs.[/bold yellow]")
        else:
            console.print(f"[bold green]✨ Authentication verified! Available balance: ${balance:.2f}. You are ready to proceed.[/bold green]\n")

    except DataForSEOAPIError as e:
        console.print(Panel(
            f"[bold red]API Error Code [{e.code}]:[/bold red]\n{e.message}",
            title="Authentication Failed",
            border_style="red"
        ))
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]❌ Unexpected Error:[/bold red] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
