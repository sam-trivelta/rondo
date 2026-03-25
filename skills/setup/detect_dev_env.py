#!/usr/bin/env python3
"""
Scan the current directory for dev environment indicators.
Prints a JSON object with inferred test_command, lint_command, main_branch.

Usage: python detect_dev_env.py
"""
import json
import subprocess
from pathlib import Path


def detect() -> None:
    result = {
        "test_command": "pytest",
        "lint_command": None,
        "main_branch": "main",
        "evidence": [],
    }

    root = Path.cwd()

    # pyproject.toml
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text()
        result["evidence"].append("pyproject.toml found")
        if "ruff" in content:
            result["lint_command"] = "ruff check ."
            result["evidence"].append("ruff detected in pyproject.toml")
        elif "black" in content:
            result["lint_command"] = "black . --check"
            result["evidence"].append("black detected in pyproject.toml")

    # setup.cfg
    setup_cfg = root / "setup.cfg"
    if setup_cfg.exists():
        content = setup_cfg.read_text()
        result["evidence"].append("setup.cfg found")
        if "flake8" in content:
            result["lint_command"] = result["lint_command"] or "flake8 ."
            result["evidence"].append("flake8 config found in setup.cfg")

    # Makefile — prefer make targets if present
    makefile = root / "Makefile"
    if makefile.exists():
        content = makefile.read_text()
        result["evidence"].append("Makefile found")
        if "\ntest:" in content or "make test" in content:
            result["test_command"] = "make test"
            result["evidence"].append("make test target found")
        if "\nlint:" in content or "make lint" in content:
            result["lint_command"] = "make lint"
            result["evidence"].append("make lint target found")

    # requirements files — scan for known linters
    for req_file in root.glob("requirements*.txt"):
        content = req_file.read_text()
        result["evidence"].append(f"{req_file.name} found")
        if result["lint_command"] is None:
            if "ruff" in content:
                result["lint_command"] = "ruff check ."
            elif "black" in content:
                result["lint_command"] = "black . --check"
            elif "flake8" in content:
                result["lint_command"] = "flake8 ."

    # Detect main branch from git remote
    try:
        out = subprocess.check_output(
            ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        result["main_branch"] = out.split("/")[-1]
    except Exception:
        pass  # default "main" already set

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    detect()
