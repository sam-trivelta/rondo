---
name: plan
description: Generates an implementation plan for a JIRA ticket. Reads triage output, produces a step-by-step plan, creates a git branch, and waits for human approval before any code is written. Use after /triage has been run for the ticket.
---

## /plan <TICKET-ID>

Goal: produce an approved implementation plan and a clean git branch to work on.

### Steps

1. **Read `rondo.yaml`** — get `branch_prefix`, `main_branch`, and `jira.project_key`.

2. **Read triage output** — check `.rondo/TICKET-ID/triage.md` first. If it exists, read it. If not, look in the conversation for a triage summary. If neither exists, run `/rondo:triage TICKET-ID` now before proceeding.

3. **Generate implementation plan:**

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

4. **Create the git branch:**
   ```bash
   git checkout {main_branch} && git pull
   git checkout -b {branch_prefix}/TICKET-ID-short-description
   ```
   Keep the slug short (3–5 words, kebab-case). Use `main_branch` from rondo.yaml as the base.

5. **Present the plan to the user and STOP.**
   End with: "Approve this plan to proceed with `/fix TICKET-ID`."
   Do NOT write any code until the user explicitly approves.

6. **Save plan to `.rondo/TICKET-ID/plan.md`** (after user approves):

   Ensure `.rondo/` is in `.gitignore` (same check as /triage — append if missing).

   Write `.rondo/TICKET-ID/plan.md`:
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
   Run: `python "$(find ~/.claude/plugins -maxdepth 2 -name rondo -type d | head -1)/skills/triage/jira_comment.py" <TICKET-ID> --file .rondo/<TICKET-ID>/plan.md`
   If it fails, print a warning ("⚠ Could not post plan to JIRA — continuing.") and move on. Do not block.
