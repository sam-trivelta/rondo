#!/usr/bin/env python3
"""
Fetch a JIRA ticket via REST API and print a structured summary.

Usage:
  python jira_fetch.py TICKET-ID        # fetch and print ticket
  python jira_fetch.py --check          # test auth only (used by /status)

Requires env vars (or a .env file in the current directory):
  JIRA_BASE_URL  — e.g. https://yourorg.atlassian.net
  JIRA_EMAIL     — your Atlassian account email
  JIRA_API_TOKEN — API token from id.atlassian.com > Security > API tokens

Exit codes:
  0 — success (ticket printed) or env vars missing (prints message, Claude falls back to paste)
  1 — ticket not found or API error
"""
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


def load_env() -> None:
    """Load .env from cwd if present (simple key=value, no quotes needed)."""
    env_file = Path.cwd() / ".env"
    if not env_file.exists():
        # Also check the script's directory (rondo repo root)
        env_file = Path(__file__).parent.parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())


def extract_text(node: dict) -> str:
    """Recursively extract plain text from an Atlassian Document Format node."""
    if not node:
        return ""
    if node.get("type") == "text":
        return node.get("text", "")
    return "".join(extract_text(child) for child in node.get("content", []))


def fetch_ticket(ticket_id: str) -> None:
    load_env()

    base_url = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
    email = os.environ.get("JIRA_EMAIL", "")
    token = os.environ.get("JIRA_API_TOKEN", "")

    if not all([base_url, email, token]):
        print("JIRA env vars not set — paste the ticket description to proceed.")
        sys.exit(0)

    url = f"{base_url}/rest/api/3/issue/{ticket_id}"
    credentials = base64.b64encode(f"{email}:{token}".encode()).decode()

    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Basic {credentials}",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Ticket {ticket_id} not found.", file=sys.stderr)
        else:
            print(f"JIRA API error: {e.code} {e.reason}", file=sys.stderr)
        sys.exit(1)

    fields = data["fields"]

    summary = fields.get("summary", "")
    issue_type = fields.get("issuetype", {}).get("name", "")
    status = fields.get("status", {}).get("name", "")
    assignee = (fields.get("assignee") or {}).get("displayName", "Unassigned")
    priority = (fields.get("priority") or {}).get("name", "")

    description = ""
    if fields.get("description"):
        description = extract_text(fields["description"]).strip()

    # Acceptance criteria — stored in a custom field on many JIRA instances
    acceptance_criteria = ""
    for key, value in fields.items():
        if key.startswith("customfield_") and isinstance(value, dict):
            text = extract_text(value).strip()
            if text:
                # Heuristic: custom fields with "accept" in their schema name
                acceptance_criteria = text
                break

    print(f"Ticket:      {ticket_id}")
    print(f"Summary:     {summary}")
    print(f"Type:        {issue_type}")
    print(f"Status:      {status}")
    print(f"Assignee:    {assignee}")
    if priority:
        print(f"Priority:    {priority}")
    print()
    if description:
        print("Description:")
        print(description)
        print()
    if acceptance_criteria:
        print("Acceptance Criteria:")
        print(acceptance_criteria)


def check_auth() -> None:
    """Test JIRA connectivity. Prints 'ok: <email>' or an error. Used by /status."""
    load_env()

    base_url = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
    email = os.environ.get("JIRA_EMAIL", "")
    token = os.environ.get("JIRA_API_TOKEN", "")

    if not all([base_url, email, token]):
        print("not configured — set JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN in .env")
        sys.exit(1)

    url = f"{base_url}/rest/api/3/myself"
    credentials = base64.b64encode(f"{email}:{token}".encode()).decode()
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Basic {credentials}", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            print(f"ok: {data.get('emailAddress', email)}")
    except urllib.error.HTTPError as e:
        print(f"auth failed: {e.code} {e.reason}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: jira_fetch.py TICKET-ID | --check", file=sys.stderr)
        sys.exit(1)
    if sys.argv[1] == "--check":
        check_auth()
    else:
        fetch_ticket(sys.argv[1])
