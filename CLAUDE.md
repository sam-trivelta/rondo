# Rondo — Plugin Development

This is the rondo Claude Code plugin. It automates the JIRA → code → PR loop via
four skills: `/rondo:setup`, `/rondo:triage`, `/rondo:plan`, `/rondo:fix`.

## Testing locally

Load the plugin without installing it:
```bash
claude --plugin-dir /path/to/rondo
```
After making changes, run `/reload-plugins` to pick them up without restarting.

## Structure

- `.claude-plugin/plugin.json` — manifest (name, version, description)
- `skills/<name>/SKILL.md` — slash command instructions (frontmatter: name, description)
- `skills/triage/jira_fetch.py` — fetches JIRA tickets via REST API
- `skills/triage/jira_comment.py` — posts markdown comments to JIRA (ADF conversion)
- `skills/fix/jira_transition.py` — transitions JIRA ticket status

## Env vars (for testing JIRA integration)

Store in `.env` at the repo root (gitignored):
```
JIRA_BASE_URL=https://yourorg.atlassian.net
JIRA_EMAIL=you@yourorg.com
JIRA_API_TOKEN=your-token
```
