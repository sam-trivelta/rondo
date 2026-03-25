---
name: triage
description: Triages a JIRA ticket. Fetches the ticket details, identifies affected files in the repo, classifies type and complexity, and posts a summary. Use when given a JIRA ticket ID like COMP-123 or when asked to triage a ticket.
---

## /triage <TICKET-ID>

Goal: understand the ticket and identify what needs to change in the repo.

### Steps

1. **Check for existing triage output:**
   Look for `.rondo/TICKET-ID/triage.md` in the current repo. If it exists, show the user its contents and ask: "Triage already exists for TICKET-ID — re-run or use cached?" Stop here if they want to use the cached version.

2. **Read `rondo.yaml`** — get `jira.project_key` and `dev` settings. If missing, tell the user to run `/setup` first.

3. **Fetch ticket details:**

   Run: `python "$(find ~/.claude/plugins -maxdepth 2 -name rondo -type d | head -1)/skills/triage/jira_fetch.py" <TICKET-ID>`

   If the output says "JIRA env vars not set" or the script errors, say:
   > "JIRA API not configured. Please paste the ticket description (summary, acceptance criteria, any relevant context) and I'll proceed."
   Wait for the user to paste it before continuing.

4. **Analyze the ticket:**
   - **Type**: bug / feature / refactor / chore / investigation
   - **Complexity**: S (< 1 day) / M (1–3 days) / L (3+ days, consider splitting)
   - **Key entities**: extract function names, class names, module names, API endpoints, or data models mentioned in the ticket

5. **Scan the repo for affected files** using Grep on the key entities from step 3:
   - Search `**/*.py` for the entity names
   - Search `**/test_*.py` and `**/tests/**` for existing test coverage
   - Search config files if the ticket involves settings or schemas
   List the top 5–10 most likely files to change, with a one-line reason each.

6. **Present triage summary:**

   ```
   ## Triage: TICKET-ID
   **Type:** bug | feature | refactor | chore | investigation
   **Complexity:** S | M | L
   **Summary:** one sentence describing what needs to happen

   ### Affected Files (likely)
   - path/to/file.py — reason

   ### Open Questions
   - anything unclear that needs answering before planning
   ```

7. **Save triage output to `.rondo/TICKET-ID/triage.md`:**

   First, ensure `.rondo/` is in the repo's `.gitignore`:
   - Read `.gitignore` (or check if it exists)
   - If `.rondo/` or `.rondo` is not already in it, append `.rondo/` to `.gitignore` (create the file if it doesn't exist)

   Then write `.rondo/TICKET-ID/triage.md` (create the directory if needed):
   ```markdown
   # Triage: TICKET-ID
   **Type:** ...
   **Complexity:** S | M | L
   **Summary:** one sentence

   ## Affected Files
   - path/to/file.py — reason

   ## Open Questions
   - ...
   ```

8. **Post to JIRA** (best-effort, never block on this):
   Run: `python "$(find ~/.claude/plugins -maxdepth 2 -name rondo -type d | head -1)/skills/triage/jira_comment.py" <TICKET-ID> --file .rondo/<TICKET-ID>/triage.md`
   If it fails, print a warning ("⚠ Could not post to JIRA — continuing.") and move on. Do not block.
