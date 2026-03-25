---
name: fix
description: Executes an approved implementation plan. Writes code, runs linting and tests, commits, pushes the branch, and opens a GitHub PR. Use after /plan has been approved by the human.
---

## /fix <TICKET-ID>

Goal: implement the approved plan, verify it passes lint and tests, and ship a PR.

### Pre-flight checks

Before writing any code:

1. **Read `rondo.yaml`** — get `test_command`, `lint_command`, `branch_prefix`, `jira.project_key`.
2. **Confirm the current branch:** run `git branch --show-current`. It should match `{branch_prefix}/TICKET-ID-*`. If not, warn the user and stop.
3. **Read the approved plan** — check `.rondo/TICKET-ID/plan.md` first. If it exists, read it as the source of truth. If not, look in the conversation. If neither exists, tell the user to run `/rondo:plan TICKET-ID` first.

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
   Run: `python "$(find ~/.claude/plugins -maxdepth 2 -name rondo -type d | head -1)/skills/fix/jira_transition.py" <TICKET-ID> "<status>"`
   The correct status name varies by project. If the script prints "not found" with a list of available statuses, pick the most appropriate one (e.g. "Manager Review", "Resolved") and retry. If the script errors (not just "transition not found"), print a warning ("⚠ Could not transition JIRA ticket — continuing.") and move on. Do not block.

9. **Save fix summary to `.rondo/TICKET-ID/fix.md`:**

   Ensure `.rondo/` is in `.gitignore` (same check as /triage — append if missing).

   Write `.rondo/TICKET-ID/fix.md`:
   ```markdown
   # Fix: TICKET-ID
   **PR:** <url>
   **Branch:** feat/TICKET-ID-short-description
   **Status:** open

   ## What changed
   - bullet list of files changed and why
   ```

10. **Post fix summary to JIRA** (best-effort):
    Run: `python "$(find ~/.claude/plugins -maxdepth 2 -name rondo -type d | head -1)/skills/triage/jira_comment.py" <TICKET-ID> --file .rondo/<TICKET-ID>/fix.md`
    If it fails, print a warning ("⚠ Could not post fix summary to JIRA — continuing.") and move on. Do not block.

11. **Report back** with the PR URL and a one-sentence summary of what was done.
