#!/usr/bin/env python3
"""
Transition a JIRA ticket to a named status via REST API.

Usage: python jira_transition.py TICKET-ID "In Review"

Requires env vars (or a .env file):
  JIRA_BASE_URL  — e.g. https://yourorg.atlassian.net
  JIRA_EMAIL     — your Atlassian account email
  JIRA_API_TOKEN — API token from id.atlassian.com > Security > API tokens

Exit codes:
  0 — success or env vars missing (skips silently)
  1 — transition not found or API error
"""
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


def load_env() -> None:
    """Load .env files in priority order (later files win; shell vars always win).

    Search order (lowest to highest priority):
      1. ~/.config/rondo/.env  — user-level credential store
      2. <cwd>/.env            — per-project override
    """
    candidates = [
        Path.home() / ".config" / "rondo" / ".env",
        Path.cwd() / ".env",
    ]
    for env_file in candidates:
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())


def make_request(url: str, credentials: str, data: "bytes | None" = None) -> dict:
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Basic {credentials}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        method="POST" if data is not None else "GET",
    )
    with urllib.request.urlopen(req) as resp:
        content = resp.read()
        return json.loads(content) if content else {}


def transition_ticket(ticket_id: str, target_status: str) -> None:
    load_env()

    base_url = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
    email = os.environ.get("JIRA_EMAIL", "")
    token = os.environ.get("JIRA_API_TOKEN", "")

    if not all([base_url, email, token]):
        print("JIRA env vars not set — skipping ticket transition.")
        sys.exit(0)

    credentials = base64.b64encode(f"{email}:{token}".encode()).decode()

    # Get available transitions
    transitions_url = f"{base_url}/rest/api/3/issue/{ticket_id}/transitions"
    try:
        result = make_request(transitions_url, credentials)
    except urllib.error.HTTPError as e:
        print(f"Failed to fetch transitions: {e.code} {e.reason}", file=sys.stderr)
        sys.exit(1)

    transitions = result.get("transitions", [])
    match = next(
        (t for t in transitions if t["name"].lower() == target_status.lower()), None
    )

    if not match:
        available = [t["name"] for t in transitions]
        print(
            f"Transition '{target_status}' not found. Available: {available}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Apply the transition
    payload = json.dumps({"transition": {"id": match["id"]}}).encode()
    try:
        make_request(transitions_url, credentials, data=payload)
        print(f"Transitioned {ticket_id} to '{match['name']}'")
    except urllib.error.HTTPError as e:
        print(f"Failed to transition ticket: {e.code} {e.reason}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: jira_transition.py TICKET-ID 'target status'", file=sys.stderr)
        sys.exit(1)
    transition_ticket(sys.argv[1], sys.argv[2])
