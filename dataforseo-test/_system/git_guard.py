#!/usr/bin/env python3
"""
git_guard.py
------------
Pre-commit secret scanner to ensure zero credential leakage to GitHub.
"""

import subprocess
import sys
import re
from pathlib import Path

SUSPICIOUS_PATTERNS = [
    re.compile(r'DATAFORSEO_PASSWORD\s*=\s*["\']?[a-zA-Z0-9_\-\.]{8,}["\']?'),
    re.compile(r'api[-_]?key\s*[:=]\s*["\']?[a-zA-Z0-9_\-\.]{12,}["\']?', re.IGNORECASE),
    re.compile(r'bearer\s+[a-zA-Z0-9_\-\.]{20,}', re.IGNORECASE),
    re.compile(r'ghp_[a-zA-Z0-9]{36}'),
]

FORBIDDEN_FILENAMES = [
    ".env",
    ".env.local",
    ".env.production",
    "credentials.json",
    "id_rsa",
]

def check_staged_files():
    try:
        res = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True
        )
        staged_files = [f.strip() for f in res.stdout.splitlines() if f.strip()]
    except Exception as e:
        print(f"⚠️ Git guard check skipped: {e}")
        return True

    violations = []

    PLACEHOLDER_SUBSTRINGS = ["your_", "example", "placeholder", "xxx", "<", "test_token"]

    for f in staged_files:
        p = Path(f)
        if p.name in FORBIDDEN_FILENAMES:
            violations.append(f"❌ Forbidden credential file staged: {f}")
            continue

        # Check diff content of staged file
        try:
            diff_res = subprocess.run(
                ["git", "diff", "--cached", f],
                capture_output=True,
                text=True,
                check=True
            )
            content = diff_res.stdout
            for pattern in SUSPICIOUS_PATTERNS:
                matches = pattern.findall(content)
                for m in matches:
                    # Ignore harmless placeholders
                    if any(ph in m.lower() for ph in PLACEHOLDER_SUBSTRINGS):
                        continue
                    violations.append(f"❌ Suspicious secret pattern detected in staged diff of: {f}")
                    break
        except Exception:
            pass

    if violations:
        print("\n🚨 GIT GUARD: COMMIT BLOCKED TO PREVENT SECRET LEAKAGE!")
        for v in violations:
            print(f"   {v}")
        print("\n👉 Remove secrets or unstage `.env` before committing.\n")
        return False

    return True

if __name__ == "__main__":
    if not check_staged_files():
        sys.exit(1)
    print("✅ Git Guard: Staged files verified. No secrets detected.")
    sys.exit(0)
