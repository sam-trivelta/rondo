# Rondo

Claude Code plugin that automates the JIRA → code → PR dev loop.

```
/setup  →  /triage TICKET-ID  →  review  →  /plan TICKET-ID  →  approve  →  /fix TICKET-ID
```

## Install

From within any Claude Code session:

```
/plugin marketplace add sam-trivelta/rondo
/plugin install rondo@rondo
/reload-plugins
```

For local development, use the `--plugin-dir` flag instead:

```bash
claude --plugin-dir /path/to/rondo
```

## One-time setup per repo

Navigate to the target repo and run:

```
/rondo:setup
```

Rondo scans the repo for your test runner, linter, and branch conventions, then writes `rondo.yaml`. Run it once per repo.

## The Loop

### `/rondo:triage TICKET-ID`
Fetches the ticket via the JIRA REST API (or asks you to paste the description if not configured). Scans the repo for affected files and posts a triage summary back to JIRA.

### `/rondo:plan TICKET-ID`
Reads the triage output and generates a step-by-step implementation plan. **Stops and waits for your approval before writing any code.**

### `/rondo:fix TICKET-ID`
Executes the approved plan: creates a branch, writes code, runs lint and tests, commits, pushes, and opens a PR via `gh`. Transitions the JIRA ticket to In Review.

### `/rondo:status [TICKET-ID]`
Checks JIRA API and GitHub connectivity. With a ticket ID, shows where the ticket sits in the triage → plan → fix pipeline.

### `/rondo:show TICKET-ID`
Displays saved triage and plan artifacts. Useful for reorienting in a new session before running `/rondo:fix`.

## Environment

`gh` CLI must be authenticated:
```bash
gh auth login
```

JIRA (optional — enables fetching tickets and posting comments):
```bash
mkdir -p ~/.config/rondo
cat > ~/.config/rondo/.env << 'EOF'
JIRA_BASE_URL=https://yourorg.atlassian.net
JIRA_EMAIL=you@yourorg.com
JIRA_API_TOKEN=your-token
EOF
```
Get your API token at https://id.atlassian.com/manage-profile/security — click **Create and manage API tokens**.
This file is shared across all repos. A `.env` in any individual repo overrides it.

## rondo.yaml

Written by `/setup` into the target repo root. Edit manually if needed.

```yaml
jira:
  project_key: PROJ   # e.g. COMP, COMPLENG

dev:
  test_command: pytest
  lint_command: "black . --check"
  branch_prefix: feat
  main_branch: main
```
