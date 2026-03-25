---
name: setup
description: Sets up Rondo for the current repository. Run once per repo to detect the dev environment (test runner, linter, branch conventions) and create a rondo.yaml config file. Use when rondo.yaml is missing or needs updating.
---

## /setup

Goal: create or update `rondo.yaml` in the current repo root.

### Steps

1. **Check for existing rondo.yaml** — if it exists, read it and show the current config. Ask the user whether to update it or keep it as-is.

2. **Scan the repo for dev environment indicators** using your Glob and Read tools:
   - `pyproject.toml` — check for `[tool.pytest]`, `[tool.black]`, `[tool.ruff]`, `[tool.isort]`
   - `setup.cfg` — check for `[tool:pytest]`, `[flake8]`
   - `Makefile` — look for `test`, `lint`, `check` targets
   - `.github/workflows/*.yml` — look for test/lint steps to infer commands
   - `requirements*.txt` / `requirements-dev.txt` — note key dev dependencies
   - `tox.ini`, `pytest.ini` — confirms pytest

3. **Infer config values:**
   - `test_command`: default `pytest`; use `make test` if a Makefile target exists
   - `lint_command`: check for ruff, black, flake8 in order; default `black . --check`
   - `branch_prefix`: default `feat`
   - `main_branch`: run `git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null` and parse last segment; default `main`
   - `jira_project_key`: cannot be inferred — ask the user (e.g. `COMP`, `COMPLENG`)

4. **Present inferred config** to the user and ask them to confirm or correct each value before writing.

5. **Write `rondo.yaml`** to the repo root:

   ```yaml
   jira:
     project_key: PROJ   # e.g. COMP

   dev:
     test_command: pytest
     lint_command: "black . --check"
     branch_prefix: feat
     main_branch: main
   ```

6. **Check JIRA API connectivity:**
   Remind the user that Rondo uses the JIRA REST API. The `.env` file in the Rondo repo root must have:
   ```
   JIRA_BASE_URL=https://yourorg.atlassian.net
   JIRA_EMAIL=you@yourorg.com
   JIRA_API_TOKEN=your-token
   ```
   If these aren't set, `/triage` will fall back to copy-paste mode.

7. **Offer to create or update `CLAUDE.md`** in the repo.

   - If no `CLAUDE.md` exists and the user says yes, write this file (fill in inferred values):

     ```markdown
     # <repo name>

     ## Stack
     - Language/framework: <inferred from repo scan>
     - Test command: <from rondo.yaml>
     - Lint command: <from rondo.yaml>

     ## Rondo rules
     - Always read `rondo.yaml` before doing dev work. If missing, run `/rondo:setup`.
     - Never push code or open a PR without a human-approved plan.
     - Never skip tests. Run the test command from `rondo.yaml` before committing.
     - Branch naming: `{branch_prefix}/{TICKET-ID}-short-description`
     - Commit format: `TICKET-ID: short description`
     - Always link PRs back to the JIRA ticket in the PR body.
     - When JIRA CLI is unavailable, ask the user to paste the ticket description.
     ```

   - If a `CLAUDE.md` already exists, check whether it contains a `## Rondo rules` section. If not, append the section above to the end of the existing file — do not overwrite what the team already has.
