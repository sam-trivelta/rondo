#!/usr/bin/env python3
"""
Post a formatted comment to a JIRA ticket via REST API.

Usage:
  python jira_comment.py TICKET-ID "plain text"
  python jira_comment.py TICKET-ID --file path/to/file.md

When --file is used, the markdown is converted to Atlassian Document Format
(ADF) so it renders with headings, bullet lists, bold text, etc. in JIRA.

Requires env vars (or a .env file):
  JIRA_BASE_URL  — e.g. https://yourorg.atlassian.net
  JIRA_EMAIL     — your Atlassian account email
  JIRA_API_TOKEN — API token from id.atlassian.com > Security > API tokens
"""
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


def load_env() -> None:
    env_file = Path.cwd() / ".env"
    if not env_file.exists():
        env_file = Path(__file__).parent.parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())


def parse_inline(text: str) -> list:
    """Parse inline markdown (**bold**, `code`) into ADF text nodes."""
    nodes = []
    # Split on **bold** and `code` markers
    pattern = re.compile(r"(\*\*(.+?)\*\*|`(.+?)`)")
    last = 0
    for m in pattern.finditer(text):
        if m.start() > last:
            nodes.append({"type": "text", "text": text[last:m.start()]})
        if m.group(0).startswith("**"):
            nodes.append({"type": "text", "text": m.group(2), "marks": [{"type": "strong"}]})
        else:
            nodes.append({"type": "text", "text": m.group(3), "marks": [{"type": "code"}]})
        last = m.end()
    if last < len(text):
        nodes.append({"type": "text", "text": text[last:]})
    return nodes or [{"type": "text", "text": text}]


def md_to_adf(text: str) -> list:
    """Convert a subset of markdown to a list of ADF block nodes."""
    nodes = []
    lines = text.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i]

        # Blank line — skip (paragraph breaks handled by block boundaries)
        if not line.strip():
            i += 1
            continue

        # Horizontal rule
        if line.strip() in ("---", "***", "___"):
            nodes.append({"type": "rule"})
            i += 1
            continue

        # Heading
        heading_match = re.match(r"^(#{1,3})\s+(.+)$", line)
        if heading_match:
            level = len(heading_match.group(1))
            nodes.append({
                "type": "heading",
                "attrs": {"level": level},
                "content": parse_inline(heading_match.group(2)),
            })
            i += 1
            continue

        # Bullet list — collect consecutive bullet lines
        if re.match(r"^[-*]\s+", line):
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i]):
                content = re.sub(r"^[-*]\s+", "", lines[i])
                items.append({
                    "type": "listItem",
                    "content": [{"type": "paragraph", "content": parse_inline(content)}],
                })
                i += 1
            nodes.append({"type": "bulletList", "content": items})
            continue

        # Ordered list — collect consecutive numbered lines
        if re.match(r"^\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                content = re.sub(r"^\d+\.\s+", "", lines[i])
                items.append({
                    "type": "listItem",
                    "content": [{"type": "paragraph", "content": parse_inline(content)}],
                })
                i += 1
            nodes.append({"type": "orderedList", "content": items})
            continue

        # Plain paragraph — collect until blank line or block element
        para_lines = []
        while i < len(lines):
            l = lines[i]
            if (not l.strip()
                    or re.match(r"^#{1,3}\s", l)
                    or re.match(r"^[-*]\s+", l)
                    or re.match(r"^\d+\.\s+", l)
                    or l.strip() in ("---", "***", "___")):
                break
            para_lines.append(l)
            i += 1
        if para_lines:
            nodes.append({
                "type": "paragraph",
                "content": parse_inline(" ".join(para_lines)),
            })

    return nodes


def post_comment(ticket_id: str, adf_content: list) -> None:
    load_env()

    base_url = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
    email = os.environ.get("JIRA_EMAIL", "")
    token = os.environ.get("JIRA_API_TOKEN", "")

    if not all([base_url, email, token]):
        print(
            "JIRA env vars not set (JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN). Skipping comment.",
            file=sys.stderr,
        )
        sys.exit(0)

    url = f"{base_url}/rest/api/3/issue/{ticket_id}/comment"
    credentials = base64.b64encode(f"{email}:{token}".encode()).decode()

    payload = json.dumps({
        "body": {
            "type": "doc",
            "version": 1,
            "content": adf_content,
        }
    }).encode()

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            print(f"Comment posted to {ticket_id} (status {resp.status})")
    except urllib.error.HTTPError as e:
        print(f"Failed to post comment: {e.code} {e.reason}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: jira_comment.py TICKET-ID 'text' | --file path/to/file.md", file=sys.stderr)
        sys.exit(1)

    ticket = sys.argv[1]

    if sys.argv[2] == "--file":
        if len(sys.argv) < 4:
            print("Usage: jira_comment.py TICKET-ID --file path/to/file.md", file=sys.stderr)
            sys.exit(1)
        md_text = Path(sys.argv[3]).read_text()
        adf = md_to_adf(md_text)
    else:
        # Plain text fallback — wrap in a single paragraph
        adf = [{"type": "paragraph", "content": [{"type": "text", "text": sys.argv[2]}]}]

    post_comment(ticket, adf)
