# Contributing

How to develop and extend the **agent-harness** plugin. The generic engineering
methodology lives in `rules/agent-harness.md` and the stage skills; this file
covers project structure, versioning, and cross-tool reference material.

## Project layout

- `rules/agent-harness.md` — the always-on ruleset. `scripts/sync.py` installs
  it to `~/.claude/rules/agent-harness.md` (a global Claude Code rule loaded at
  session start), leaving the user's own `~/.claude/CLAUDE.md` untouched — it
  removes only a legacy copy of this ruleset previously installed there (a
  `CLAUDE.md` whose heading is the ruleset title).
- `skills/<name>/SKILL.md` — the stage skills (planning, implementation,
  review, product-review, perf-review, commit, pull-requests) plus the
  agent-readiness, ast-grep, and django-review skills.
- `hooks/` — bundled Claude Code hooks (see `docs/hooks.md`). `.lsp.json` —
  bundled language servers. `.mcp.json` — bundled MCP servers. `settings.json`
  — bundled settings (git/PR attribution).
- `.claude-plugin/plugin.json` — the plugin manifest (carries the version).
  `.claude-plugin/marketplace.json` — marketplace entry (no version field).
- `docs/` — maintenance reference, kept current per `CLAUDE.md`.
- `scripts/sync.py` — Claude Code install/update.

## Versioning

SemVer. A version bump updates `.claude-plugin/plugin.json`, the sole manifest
carrying the version (`.claude-plugin/marketplace.json` has no version field).

- **Default: patch.** Skill/rule/doc-content edits, hook or `.lsp.json` changes,
  bug fixes, and adding another instance of an already-present component type
  (e.g. another MCP server when MCP servers already exist) are all patch.
- **Minor: only when adding a component of a type the plugin did not have
  before** — first-of-its-kind, not another-of-a-kind. Example: the first
  subagent when none existed; the first MCP server in a plugin that had none.
- Documentation-only changes need no bump.

The bump is the **last action before pushing**: make it once, at the end of the
work — not per edit, per turn, or per commit.

## Reference: plugin & global-file structure across agent tools

Contributor reference and possible future work. **Claude Code is the only
supported target today**; Antigravity and Zed are listed for reference only, not
worked on now.

### Claude Code

Authoritative docs: [plugins](https://code.claude.com/docs/en/plugins),
[the `.claude` directory](https://code.claude.com/docs/en/claude-directory).

- **Plugin** — components live at the plugin root, *not* inside
  `.claude-plugin/`: `.claude-plugin/plugin.json` (manifest); `skills/<name>/SKILL.md`;
  `agents/`; `hooks/hooks.json`; `commands/`; `.mcp.json`; `.lsp.json`;
  `monitors/monitors.json`; `bin/`; `settings.json`.
- **User-global files** under `~/.claude/`: `CLAUDE.md` (user memory, loaded
  every session); `rules/*.md` (global rules — load at session start unless
  scoped with `paths:` frontmatter); `skills/`; `agents/`; `settings.json`; and
  user-scope MCP servers. This plugin installs its ruleset to
  `~/.claude/rules/agent-harness.md`.

### Antigravity

Reference: <https://antigravity.google/docs/plugins> — its plugin and
global-file structure. Not a supported target.

### Zed

Reference: [skills](https://zed.dev/docs/ai/skills),
[instructions](https://zed.dev/docs/ai/instructions),
[MCP](https://zed.dev/docs/ai/mcp) — Zed's skill, rules/instructions, and MCP
configuration. Not a supported target.
