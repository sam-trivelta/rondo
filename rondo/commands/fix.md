---
name: fix
description: Executes an approved implementation plan. Writes code, runs linting and tests, commits, pushes the branch, and opens a GitHub PR. Use after /plan has been approved by the human.
---

## /fix <TICKET-ID>

Goal: implement the approved plan, verify it passes lint and tests, and ship a PR.

### Pre-flight checks

Before writing any code:

1. **Compute the Rondo config directory** for this repo:

   ```bash
   RONDO_REPO_ID=$(git remote get-url origin 2>/dev/null \
     | sed 's|.*[:/]\([^/]*/[^/]*\)$|\1|; s|\.git$||; s|/|-|g')
   [ -z "$RONDO_REPO_ID" ] && RONDO_REPO_ID=$(basename "$(pwd)")
   RONDO_DIR="$HOME/.config/rondo/$RONDO_REPO_ID"
   TICKET_DIR="$RONDO_DIR/<TICKET-ID>"
   ```

2. **Read `rondo.yaml`** from `$RONDO_DIR/rondo.yaml` — get `test_command`, `lint_command`, `branch_prefix`, `jira.project_key`. If missing, tell the user to run `/setup` first.

3. **Confirm the current branch:** run `git branch --show-current`. It should match `{branch_prefix}/TICKET-ID-*`. If not, warn the user and stop.

4. **Read the approved plan** from `$TICKET_DIR/plan.md`. If it doesn't exist, look in the conversation. If neither exists, tell the user to run `/plan TICKET-ID` first.

### Steps

1. **Implement the changes** per the plan steps. Edit files using your tools. Read each file before editing it. Follow the repo's existing code style, naming conventions, and import patterns.

2. **Write tests** as specified in the plan. Check where existing tests live and follow the same structure and naming.

3. **Run lint:**
   ```bash
   {lint_command from rondo.yaml}
   ```
   Fix any errors before proceeding. Do not skip or suppress lint rules.

4. **Run tests:**
   ```bash
   {test_command from rondo.yaml}
   ```
   If tests fail, diagnose the root cause and fix it. Iterate until tests pass.
   If you cannot fix a failure after 3 attempts, stop and explain the problem to the user — do not commit broken code.

5. **Stage and commit** (stage specific files, not everything):
   ```bash
   git add path/to/changed/file.py path/to/test_file.py
   git commit -m "TICKET-ID: short description of what changed"
   ```

6. **Push the branch:**
   ```bash
   git push -u origin HEAD
   ```

7. **Open a PR:**
   ```bash
   gh pr create \
     --title "TICKET-ID: short description" \
     --body "$(cat <<'EOF'
   ## Summary
   <one paragraph from the plan>

   ## Changes
   - bullet list of what changed

   ## Testing
   - how this was tested

   Closes TICKET-ID
   EOF
   )"
   ```

8. **Transition the JIRA ticket** (best-effort):
   Run: `python "$(find ~/.claude/plugins -maxdepth 2 -name rondo -type d | head -1)/scripts/jira_transition.py" <TICKET-ID> "<status>"`
   The correct status name varies by project. If the script prints "not found" with a list of available statuses, pick the most appropriate one (e.g. "Manager Review", "Resolved") and retry. If the script errors (not just "transition not found"), print a warning ("⚠ Could not transition JIRA ticket — continuing.") and move on. Do not block.

9. **Save fix summary** to `$TICKET_DIR/fix.md`:

   ```bash
   mkdir -p "$TICKET_DIR"
   ```

   Write `$TICKET_DIR/fix.md`:
   ```markdown
   # Fix: TICKET-ID
   **PR:** <url>
   **Branch:** feat/TICKET-ID-short-description
   **Status:** open

   ## What changed
   - bullet list of files changed and why
   ```

10. **Post fix summary to JIRA** (best-effort):
    Run: `python "$(find ~/.claude/plugins -maxdepth 2 -name rondo -type d | head -1)/scripts/jira_comment.py" <TICKET-ID> --file "$TICKET_DIR/fix.md"`
    If it fails, print a warning ("⚠ Could not post fix summary to JIRA — continuing.") and move on. Do not block.

11. **Report back** with the PR URL and a one-sentence summary of what was done.
