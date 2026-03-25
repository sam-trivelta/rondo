# Rondo — MVP PRD

## What

Rondo is a Claude Code plugin that automates the JIRA → code → PR pipeline. It installs once per machine via `/plugin add <org>/rondo` and requires a one-time `/setup` per repo. Four slash commands cover the full dev loop; human approval gates sit between planning and coding.

## The Loop

```
/setup  (once per repo)

/triage TICKET-ID  →  human reviews  →  /plan TICKET-ID  →  human approves  →  /fix TICKET-ID
```

- **`/setup`** — scans the repo for dev environment indicators (pyproject.toml, Makefile, requirements.txt, CI workflows), infers test/lint commands and branch conventions, confirms with the user, and writes `rondo.yaml` to the repo root. Offers to create `CLAUDE.md` if none exists.
- **`/triage`** — fetch ticket via `jira` CLI (falls back to copy-paste if CLI unavailable), classify type/complexity, scan repo for affected files, post summary back to JIRA as a comment
- **`/plan`** — read triage output, generate a step-by-step implementation plan, create a git branch, post plan to JIRA, stop and wait for human approval
- **`/fix`** — execute the approved plan, write tests, run lint + tests, commit, push, open PR via `gh` CLI, transition JIRA ticket to In Review

Claude does the cognitive work. Scripts handle JIRA I/O. Humans stay in the loop between planning and execution.

## Repo Structure

```
rondo/
├── .claude-plugin/
│   └── plugin.json              # plugin manifest
├── CLAUDE.md                    # standing agent rules
├── README.md                    # install + usage docs
└── skills/
    ├── setup/
    │   ├── SKILL.md             # /setup slash command
    │   └── detect_dev_env.py    # scans repo, outputs rondo.yaml template
    ├── triage/
    │   ├── SKILL.md             # /triage slash command
    │   └── jira_comment.py      # posts comment to JIRA via REST API
    ├── plan/
    │   └── SKILL.md             # /plan slash command
    └── fix/
        └── SKILL.md             # /fix slash command
```

**Key pattern:** Claude uses its native tools (Bash, Glob, Grep, Edit) directly — no heavy script wrappers. Helper scripts exist only where auth complexity warrants it (JIRA REST API comments).

## SKILL.md Format

Every skill folder has a `SKILL.md` with YAML frontmatter:

```markdown
---
name: skill-name
description: When to use this skill and what it does (triggers automatic loading by Claude)
---

## Instructions
...
```

The `description` triggers automatic loading; the `name` becomes the slash command.

## rondo.yaml (per target repo)

Written by `/setup` into the target repo root. Tells Rondo how to dev and test in that specific repo.

```yaml
jira:
  project_key: PROJ   # e.g. COMP, COMPLENG

dev:
  test_command: pytest
  lint_command: "black . --check"
  branch_prefix: feat
  main_branch: main
```

## CLAUDE.md (Agent Rules)

```markdown
# Rondo

You are an autonomous developer working within a team's existing codebase. Always respect the project's conventions.

## Rules
- Always read `rondo.yaml` in the repo root before doing dev work. If it's missing, tell the user to run `/setup` first.
- Never push code or open a PR without a human-approved plan.
- Never skip tests. Run the test command from rondo.yaml before committing.
- Branch naming: `{branch_prefix}/{TICKET-ID}-short-description`
- Commit format: `TICKET-ID: short description`
- Always link PRs back to the JIRA ticket in the PR body.
- When JIRA CLI is unavailable, ask the user to paste the ticket description — don't block.
```

## JIRA Access

Rondo tries JIRA access in this order and degrades gracefully:

1. **`jira` CLI** (ankitpokhrel/jira-cli) — `brew install jira-cli && jira init`
2. **REST API** (`jira_comment.py`) — requires `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` env vars
3. **Copy-paste fallback** — user pastes ticket description directly into the chat; Rondo proceeds from there

## Environment Setup

```bash
# GitHub CLI (required for PR creation)
gh auth login

# JIRA CLI (optional but recommended)
brew install jira-cli
jira init

# JIRA REST API (optional, for posting comments if CLI can't)
export JIRA_BASE_URL="https://yourorg.atlassian.net"
export JIRA_EMAIL="you@yourorg.com"
export JIRA_API_TOKEN="your-token"   # id.atlassian.com → Security → API tokens
```

## Open Questions — Answer Before First Use

1. **GitHub org name** — needed for `/plugin add <org>/rondo` once the repo is published
2. **JIRA project key(s)** — e.g. `COMP`, `COMPLENG` — used in `/setup`
3. **jira CLI access** — can you run `brew install jira-cli`? If yes, try that first.

## Build Order (for execution)

1. Files are already scaffolded — start with `/setup` skill end-to-end
2. Test `/setup` on a real Trivelta repo — confirm rondo.yaml is generated correctly
3. Test `/triage` on a real ticket (paste fallback is fine for first run)
4. Test `/plan` — verify branch is created, plan is readable
5. Test `/fix` end-to-end — verify lint passes, tests pass, PR opens

Don't test all three skills at once. Prove `/triage` → `/plan` first, then add `/fix`.
