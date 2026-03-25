---
name: status
description: Checks Rondo's connectivity (JIRA API, GitHub) and shows the pipeline state for a ticket. Use with no arguments to check connectivity, or with a ticket ID like COMP-2837 to see where it is in the triage → plan → fix pipeline.
---

## /status [TICKET-ID]

### Connectivity check (always run this first)

1. **Check JIRA API:**
   Run: `python "$(find ~/.claude/plugins -maxdepth 2 -name rondo -type d | head -1)/skills/triage/jira_fetch.py" --check`
   - Prints `ok: email@domain.com` on success
   - Prints an error message on failure

2. **Check GitHub:**
   Run: `gh auth status 2>&1`
   - Exit code 0 = authenticated
   - Exit code non-zero = not authenticated

3. **Print connectivity summary:**
   ```
   ## Rondo Status

   JIRA API:  ✓ connected (sam.clark@trivelta.com)
   GitHub:    ✓ authenticated
   ```
   Use ✗ and the error message if either check fails.

---

### Pipeline state (only when TICKET-ID is given)

4. **Check which state files exist** in the current repo:
   - `.rondo/TICKET-ID/triage.md` → triaged
   - `.rondo/TICKET-ID/plan.md` → planned
   - `.rondo/TICKET-ID/fix.md` → fixed

5. **Read the first line of each file that exists** (the `# Heading`) for a one-liner summary.

6. **Print pipeline state:**
   ```
   ## COMP-2837 — Slack bigdeposit and bigwithdrawal channel improvement

     ✓ triaged  →  ✓ planned  →  ⏳ ready to fix

   Next step: /fix COMP-2837
   ```

   States:
   - ✓ = file exists (step complete)
   - ⏳ = previous step done, this step is next
   - ✗ = blocked (previous step not done)

   If no files exist at all: "No state found for TICKET-ID — start with `/rondo:triage TICKET-ID`"
