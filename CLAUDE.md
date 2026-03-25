# Rondo — Plugin Development

This is the rondo Claude Code plugin. It automates the JIRA → code → PR loop via
six skills: `/rondo:setup`, `/rondo:triage`, `/rondo:plan`, `/rondo:fix`, `/rondo:status`, `/rondo:show`.

## Testing locally

Load the plugin without installing it:
```bash
claude --plugin-dir /path/to/rondo
```
After making changes, run `/reload-plugins` to pick them up without restarting.

## Structure

- `rondo/.claude-plugin/plugin.json` — manifest (name, version, description)
- `rondo/skills/<name>/SKILL.md` — slash command instructions (frontmatter: name, description)
- `rondo/scripts/jira_fetch.py` — fetches JIRA tickets via REST API
- `rondo/scripts/jira_comment.py` — posts markdown comments to JIRA (ADF conversion)
- `rondo/scripts/jira_transition.py` — transitions JIRA ticket status
- `rondo/scripts/detect_dev_env.py` — scans repo for test/lint commands, outputs rondo.yaml template

## Env vars (for testing JIRA integration)

Store in `.env` at the repo root (gitignored):
```
JIRA_BASE_URL=https://yourorg.atlassian.net
JIRA_EMAIL=you@yourorg.com
JIRA_API_TOKEN=your-token
```
