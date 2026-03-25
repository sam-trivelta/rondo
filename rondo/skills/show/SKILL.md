---
name: show
description: Displays saved triage and plan artifacts for a ticket. Use in a new session to review what was previously triaged or planned before running /fix.
argument-hint: <TICKET-ID>
allowed-tools: [Bash, Read]
---


## /show <TICKET-ID>

Goal: display saved artifacts for the ticket so the user can reorient in a new session.

### Steps

1. **Compute the Rondo config directory** for this repo:

   ```bash
   RONDO_REPO_ID=$(git remote get-url origin 2>/dev/null \
     | sed 's|.*[:/]\([^/]*/[^/]*\)$|\1|; s|\.git$||; s|/|-|g')
   [ -z "$RONDO_REPO_ID" ] && RONDO_REPO_ID=$(basename "$(pwd)")
   RONDO_DIR="$HOME/.config/rondo/$RONDO_REPO_ID"
   TICKET_DIR="$RONDO_DIR/<TICKET-ID>"
   ```

2. **Check what exists:**
   ```bash
   ls "$TICKET_DIR" 2>/dev/null
   ```
   If the directory doesn't exist or is empty: print "No artifacts found for TICKET-ID — run `/triage TICKET-ID` first." and stop.

3. **Print triage.md** if it exists — read and display the full contents.

4. **Print plan.md** if it exists — read and display the full contents.

5. **Print next-step hint:**
   - triage exists, no plan → "Next: `/plan TICKET-ID`"
   - plan exists → "Plan is saved. Run `/fix TICKET-ID` to execute it."
