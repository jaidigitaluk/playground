"""
client.py
---------
Resilient, production-grade DataForSEO v3 API Client.
Fixes all common DataForSEO integration pitfalls:
1. Automatic array wrapping of single task payloads (prevents 40001 errors).
2. HTTP 200 internal status code inspection (detects embedded errors).
3. 60-second timeouts for live endpoints.
4. Transparent 24-hour local caching to save credits.
5. Spend and call-count guardrail enforcement.
"""

import os
import sys
from pathlib import Path

# Auto-reexecute using local virtual environment if not already active
_venv_python = Path(__file__).resolve().parent.parent / "venv" / "bin" / "python3"
if _venv_python.exists() and sys.executable != str(_venv_python) and "VIRTUAL_ENV" not in os.environ:
    os.execv(str(_venv_python), [str(_venv_python)] + sys.argv)

import requests
from typing import Any, Dict, List, Union, Optional
from dotenv import load_dotenv

from .cache import get_cached_response, set_cached_response
from .guardrails import guard, SpendGuardrailExceeded, CallLimitExceeded

load_dotenv(override=True)

BASE_URL = "https://api.dataforseo.com"

class DataForSEOAPIError(Exception):
    """Raised when DataForSEO returns an error in HTTP or internal status codes."""
    def __init__(self, code: int, message: str, task_data: Optional[Dict] = None):
        super().__init__(f"DataForSEO Error [{code}]: {message}")
        self.code = code
        self.message = message
        self.task_data = task_data

class DataForSEOClient:
    def __init__(
        self,
        login: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 60,
    ):
        self.login = login or os.getenv("DATAFORSEO_LOGIN") or os.getenv("DATAFORSEO_USERNAME")
        self.password = password or os.getenv("DATAFORSEO_PASSWORD") or os.getenv("DATAFORSEO_API_KEY")
        self.timeout = timeout

        if not self.login or not self.password or self.login == "your_login_email@domain.com":
            raise ValueError(
                "Missing DataForSEO credentials! "
                "Please configure DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD in your .env file."
            )

        self.auth = (self.login, self.password)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "DataForSEO-Playground-Client/1.0"
        })

    def request(
        self,
        method: str,
        path: str,
        payload: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
        use_cache: bool = True,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Executes a request to DataForSEO with caching, guardrails, and error handling.
        """
        endpoint_path = path if path.startswith("/v3") else f"/v3/{path.lstrip('/')}"
        url = f"{BASE_URL}{endpoint_path}"

        # 1. Normalize Payload: DataForSEO requires an ARRAY of task objects for POSTs
        formatted_payload = None
        if payload is not None:
            if isinstance(payload, dict):
                # Auto-wrap single object into array
                formatted_payload = [payload]
            elif isinstance(payload, list):
                formatted_payload = payload
            else:
                raise ValueError("Payload must be a dictionary or a list of dictionaries.")

        # 2. Check Cache
        if use_cache and not force_refresh and method.upper() == "POST":
            cached = get_cached_response(endpoint_path, formatted_payload)
            if cached is not None:
                return {
                    "_from_cache": True,
                    "data": cached
                }

        # 3. Guardrail Pre-Flight Check (Protects credits)
        guard.pre_flight_check(endpoint_path)

        # 4. Execute Network Call with automatic retry for transient SE server glitches
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                if method.upper() == "GET":
                    response = self.session.get(url, timeout=self.timeout)
                else:
                    response = self.session.post(url, json=formatted_payload, timeout=self.timeout)
            except requests.exceptions.Timeout:
                if attempt < max_retries:
                    import time
                    time.sleep(2)
                    continue
                raise DataForSEOAPIError(
                    code=408,
                    message=f"Request to {endpoint_path} timed out after {self.timeout}s."
                )
            except requests.exceptions.RequestException as e:
                raise DataForSEOAPIError(code=500, message=f"Network error: {str(e)}")

            # 5. Check HTTP Status
            if response.status_code == 401:
                raise DataForSEOAPIError(401, "Invalid Authentication Credentials (401 Unauthorized).")
            if response.status_code == 402:
                raise DataForSEOAPIError(402, "Payment Required / Insufficient Balance (402).")
            if response.status_code >= 400:
                raise DataForSEOAPIError(response.status_code, f"HTTP Error: {response.text}")

            data = response.json()

            # 6. Check DataForSEO Internal Task Status (Embedded in HTTP 200)
            tasks = data.get("tasks", [])
            if tasks:
                task = tasks[0]
                status_code = task.get("status_code", 20000)
                # 40101 is transient SE server error; retry once after a short pause
                if status_code == 40101 and attempt < max_retries:
                    import time
                    time.sleep(2)
                    continue
                if status_code >= 40000:
                    status_message = task.get("status_message", "Unknown DataForSEO Task Error")
                    raise DataForSEOAPIError(
                        code=status_code,
                        message=status_message,
                        task_data=task
                    )
            break

        # 7. Record Spend & Guardrail Update
        actual_cost = data.get("cost", None)
        guard.record_call(endpoint_path, actual_cost)

        # 8. Save to Cache
        if use_cache and method.upper() == "POST":
            set_cached_response(endpoint_path, formatted_payload, data)

        return {
            "_from_cache": False,
            "data": data
        }

    def get_user_data(self) -> Dict[str, Any]:
        """Fetches account balance and limits. Free endpoint."""
        res = self.request("GET", "/v3/appendix/user_data", use_cache=False)
        return res["data"]
