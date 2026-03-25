---
name: triage
description: Triages a JIRA ticket. Fetches the ticket details, identifies affected files in the repo, classifies type and complexity, and posts a summary. Use when given a JIRA ticket ID like COMP-123 or when asked to triage a ticket.
argument-hint: <TICKET-ID>
allowed-tools: [Bash, Read, Glob, Grep, Write, Edit]
---


## /triage <TICKET-ID>

Goal: understand the ticket and identify what needs to change in the repo.

### Steps

1. **Compute the Rondo config directory** for this repo:

   ```bash
   RONDO_REPO_ID=$(git remote get-url origin 2>/dev/null \
     | sed 's|.*[:/]\([^/]*/[^/]*\)$|\1|; s|\.git$||; s|/|-|g')
   [ -z "$RONDO_REPO_ID" ] && RONDO_REPO_ID=$(basename "$(pwd)")
   RONDO_DIR="$HOME/.config/rondo/$RONDO_REPO_ID"
   TICKET_DIR="$RONDO_DIR/<TICKET-ID>"
   ```
   (substitute the actual ticket ID for `<TICKET-ID>` throughout)

2. **Check for existing triage output:**
   Look for `$TICKET_DIR/triage.md`. If it exists, show the user its contents and ask: "Triage already exists for TICKET-ID — re-run or use cached?" Stop here if they want to use the cached version.

3. **Read `rondo.yaml`** from `$RONDO_DIR/rondo.yaml` — get `jira.project_key` and `dev` settings. If missing, tell the user to run `/setup` first.

4. **Fetch ticket details:**

   Run: `python "$(find ~/.claude/plugins -maxdepth 2 -name rondo -type d | head -1)/scripts/jira_fetch.py" <TICKET-ID>`

   If the output says "JIRA env vars not set" or the script errors, say:
   > "JIRA API not configured. Please paste the ticket description (summary, acceptance criteria, any relevant context) and I'll proceed."
   Wait for the user to paste it before continuing.

5. **Analyze the ticket:**
   - **Type**: bug / feature / refactor / chore / investigation
   - **Complexity**: S (< 1 day) / M (1–3 days) / L (3+ days, consider splitting)
   - **Key entities**: extract function names, class names, module names, API endpoints, or data models mentioned in the ticket

6. **Scan the repo for affected files** using Grep on the key entities from step 4:
   - Search `**/*.py` for the entity names
   - Search `**/test_*.py` and `**/tests/**` for existing test coverage
   - Search config files if the ticket involves settings or schemas
   List the top 5–10 most likely files to change, with a one-line reason each.

7. **Present triage summary:**

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

8. **Save triage output** — create `$TICKET_DIR/` and write `triage.md` there:

   ```bash
   mkdir -p "$TICKET_DIR"
   ```

   Contents of `$TICKET_DIR/triage.md`:
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

9. **Post to JIRA** (best-effort):
   Run: `python "$(find ~/.claude/plugins -maxdepth 2 -name rondo -type d | head -1)/scripts/jira_comment.py" <TICKET-ID> --file "$TICKET_DIR/triage.md"`
   If it fails, print a warning ("⚠ Could not post to JIRA — continuing.") and move on. Do not block.
