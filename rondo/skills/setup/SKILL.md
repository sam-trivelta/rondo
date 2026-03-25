---
name: setup
description: Sets up Rondo for the current repository. Run once per repo to detect the dev environment (test runner, linter, branch conventions) and create rondo.yaml. Use when rondo.yaml is missing or needs updating.
allowed-tools: [Bash, Read, Glob, Grep, Write, Edit]
---


## /setup

Goal: create or update `rondo.yaml` in `~/.config/rondo/<repo-id>/` — nothing is written to the repo itself.

### Steps

1. **Compute the Rondo config directory** for this repo:

   ```bash
   RONDO_REPO_ID=$(git remote get-url origin 2>/dev/null \
     | sed 's|.*[:/]\([^/]*/[^/]*\)$|\1|; s|\.git$||; s|/|-|g')
   [ -z "$RONDO_REPO_ID" ] && RONDO_REPO_ID=$(basename "$(pwd)")
   RONDO_DIR="$HOME/.config/rondo/$RONDO_REPO_ID"
   mkdir -p "$RONDO_DIR"
   ```

   Tell the user: "Rondo config for this repo will live at `$RONDO_DIR`."

2. **Check for existing rondo.yaml** at `$RONDO_DIR/rondo.yaml`. If it exists, read it and show the current config. Ask the user whether to update it or keep it as-is.

3. **Scan the repo for dev environment indicators** using your Glob and Read tools:
   - `pyproject.toml` — check for `[tool.pytest]`, `[tool.black]`, `[tool.ruff]`, `[tool.isort]`
   - `setup.cfg` — check for `[tool:pytest]`, `[flake8]`
   - `Makefile` — look for `test`, `lint`, `check` targets
   - `.github/workflows/*.yml` — look for test/lint steps to infer commands
   - `requirements*.txt` / `requirements-dev.txt` — note key dev dependencies
   - `tox.ini`, `pytest.ini` — confirms pytest

4. **Infer config values:**
   - `test_command`: default `pytest`; use `make test` if a Makefile target exists
   - `lint_command`: check for ruff, black, flake8 in order; default `black . --check`
   - `branch_prefix`: default `feat`
   - `main_branch`: run `git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null` and parse last segment; default `main`
   - `jira_project_key`: cannot be inferred — ask the user (e.g. `COMP`, `COMPLENG`)

5. **Present inferred config** to the user and ask them to confirm or correct each value before writing.

6. **Write `rondo.yaml`** to `$RONDO_DIR/rondo.yaml`:

   ```yaml
   jira:
     project_key: PROJ   # e.g. COMP

   dev:
     test_command: pytest
     lint_command: "black . --check"
     branch_prefix: feat
     main_branch: main
   ```

7. **Check JIRA API connectivity:**
   Rondo reads credentials from `~/.config/rondo/.env` — a single file shared across all repos.
   If it doesn't exist yet, show the user these commands to create it:

   ```bash
   mkdir -p ~/.config/rondo
   cat > ~/.config/rondo/.env << 'EOF'
   JIRA_BASE_URL=https://yourorg.atlassian.net
   JIRA_EMAIL=you@yourorg.com
   JIRA_API_TOKEN=your-token
   EOF
   ```

   API tokens: id.atlassian.com → Security → API tokens.
   If not configured, `/triage` will fall back to copy-paste mode.

8. **Offer to create `CLAUDE.md`** in the repo — only if the user wants teammates to see Rondo's working rules. This is optional. If the repo already has a `CLAUDE.md`, offer to append the Rondo rules section to it instead. Skip entirely if the user prefers no repo-level files.

   If creating:
   ```markdown
   # <repo name>

   ## Stack
   - Language/framework: <inferred from repo scan>
   - Test command: <from rondo.yaml>
   - Lint command: <from rondo.yaml>

   ## Rondo rules
   - Always run `/setup` first if rondo.yaml config is missing.
   - Never push code or open a PR without a human-approved plan.
   - Never skip tests. Run the test command before committing.
   - Branch naming: `{branch_prefix}/{TICKET-ID}-short-description`
   - Commit format: `TICKET-ID: short description`
   - Always link PRs back to the JIRA ticket in the PR body.
   - When JIRA CLI is unavailable, ask the user to paste the ticket description.
   ```
