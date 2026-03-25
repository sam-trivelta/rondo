---
name: plan
description: Generates an implementation plan for a JIRA ticket. Reads triage output from disk automatically — no manual lookup needed. Produces a step-by-step plan and waits for human approval before any code is written. You can scope the plan to a subset of the triage by saying so in the same message (e.g. "only plan the username change"). Use after /triage has been run for the ticket.
argument-hint: <TICKET-ID>
allowed-tools: [Bash, Read, Glob, Grep, Write, Edit]
---


## /plan <TICKET-ID>

Goal: produce an approved implementation plan. Branch creation happens in `/fix`.

### Steps

1. **Compute the Rondo config directory** for this repo:

   ```bash
   RONDO_REPO_ID=$(git remote get-url origin 2>/dev/null \
     | sed 's|.*[:/]\([^/]*/[^/]*\)$|\1|; s|\.git$||; s|/|-|g')
   [ -z "$RONDO_REPO_ID" ] && RONDO_REPO_ID=$(basename "$(pwd)")
   RONDO_DIR="$HOME/.config/rondo/$RONDO_REPO_ID"
   TICKET_DIR="$RONDO_DIR/<TICKET-ID>"
   ```

2. **Read `rondo.yaml`** from `$RONDO_DIR/rondo.yaml` — get `branch_prefix`, `main_branch`, and `jira.project_key`. If missing, tell the user to run `/setup` first.

3. **Read triage output** — check `$TICKET_DIR/triage.md` first. If it exists, read it. If not, look in the conversation for a triage summary. If neither exists, run `/triage TICKET-ID` now before proceeding.

   If the user specified a scope in their message (e.g. "only plan the username change"), note it. Apply it when generating the plan — list the excluded items explicitly in the Out of Scope section with a reason (e.g. "out of scope for this PR — user excluded").

4. **Generate implementation plan:**

   ```
   ## Plan: TICKET-ID
   **Branch:** {branch_prefix}/TICKET-ID-short-description

   ### Approach
   One paragraph explaining the overall strategy and key trade-offs.

   ### Steps
   1. `path/to/file.py` — what to change and why
   2. ...

   ### Tests
   - What to test, where the test file lives, and what cases to cover

   ### Out of Scope
   - What this PR will NOT do (keeps the PR focused)
   ```

5. **Present the plan to the user and STOP.**
   End with: "Approve this plan to proceed with `/fix TICKET-ID`."
   Do NOT write any code until the user explicitly approves.

6. **Save plan to `$TICKET_DIR/plan.md`** (after user approves):

   ```bash
   mkdir -p "$TICKET_DIR"
   ```

   Write `$TICKET_DIR/plan.md`:
   ```markdown
   # Plan: TICKET-ID
   **Branch:** feat/TICKET-ID-short-description

   ## Approach
   ...

   ## Steps
   1. `path/to/file.py` — what to change and why

   ## Tests
   - ...

   ## Out of Scope
   - ...
   ```

7. **Post plan to JIRA** (best-effort):
   Run: `python "$(find ~/.claude/plugins -maxdepth 2 -name rondo -type d | head -1)/scripts/jira_comment.py" <TICKET-ID> --file "$TICKET_DIR/plan.md"`
   If it fails, print a warning ("⚠ Could not post plan to JIRA — continuing.") and move on. Do not block.
