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

Rondo scans the repo for your test runner, linter, and branch conventions, then writes `rondo.yaml` to the repo root. Run it once per repo. If no `CLAUDE.md` exists, Rondo offers to create one.

## The Loop

### `/triage TICKET-ID`
Fetches the ticket via the `jira` CLI. If the CLI isn't available, Rondo asks you to paste the ticket description instead. Scans the repo for affected files and posts a triage summary.

### `/plan TICKET-ID`
Reads the triage output, generates a step-by-step implementation plan, and creates a git branch. **Stops and waits for your approval before writing any code.**

### `/fix TICKET-ID`
Executes the approved plan: writes code, runs lint and tests, commits, pushes, and opens a PR via `gh`. Transitions the JIRA ticket to In Review if CLI access is available.

## Environment

`gh` CLI must be authenticated:
```bash
gh auth login
```

JIRA CLI (optional — enables fetching tickets and posting comments):
```bash
brew install jira-cli
jira init
```

JIRA REST API (optional — for fetching tickets and posting comments):
```bash
mkdir -p ~/.config/rondo
cat > ~/.config/rondo/.env << 'EOF'
JIRA_BASE_URL=https://yourorg.atlassian.net
JIRA_EMAIL=you@yourorg.com
JIRA_API_TOKEN=your-token
EOF
```
Get your API token at id.atlassian.com → Security → API tokens.
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
