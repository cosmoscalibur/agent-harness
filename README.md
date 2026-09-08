# Agent Harness Plugin

Claude Code plugin that packages agent readiness evaluation, a global
behavioral/tooling ruleset, and stage-specific coding methodology skills
(planning, implementation, review, product-review, perf-review, commit,
pull requests) into a single global package. It also wires up language
servers, Ruff and rumdl auto-format hooks, and MCP servers (chrome-devtools,
notion).

The CLI tools and language servers below are prerequisites — install them
first, then install the harness itself ([Installation](#installation)). The
detailed inventory of what the plugin contains is in
[What's Included](#whats-included) and the [`docs/`](docs/) reference.

## CLI Tools Required

Installation is left to the developer's own environment and package manager;
[`docs/cli-tools.md`](docs/cli-tools.md) has concrete install commands.

| Tool                                             | Purpose                                                                | Install                                                                              |
| ------------------------------------------------ | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| [ast-grep](https://github.com/ast-grep/ast-grep) | Structural code search via AST — precise matches, less context bloat   | [Installation guide](https://ast-grep.github.io/guide/quick-start.html#installation) |
| [RTK](https://github.com/rtk-ai/rtk)             | Terminal output compression (60-90% fewer tokens)                      | [Repository](https://github.com/rtk-ai/rtk)                                          |
| [gh](https://cli.github.com/)                    | GitHub integration and ADRs                                            | [Installation guide](https://github.com/cli/cli#installation)                        |
| [mergiraf](https://mergiraf.org/)                | Syntax-aware git merge driver — auto-resolves AST-equivalent conflicts | [Installation guide](https://mergiraf.org/installation.html)                         |
| [uv](https://github.com/astral-sh/uv)            | Run/manage Python3 (`scripts/sync.py`, the Ruff hook, any Python)      | [Installation guide](https://docs.astral.sh/uv/getting-started/installation/)        |

### Language Servers (Claude Code)

The plugin declares its language servers internally (in `.lsp.json`); the
binaries — for Python, Markdown, Bash, TypeScript/JS, HTML/CSS, and Rust — are
a prerequisite you install **before** the Claude setup. See
[`docs/lsp.md`](docs/lsp.md) for the per-language binaries, their install
commands, and how to add a server, and [`docs/hooks.md`](docs/hooks.md) for why
Python formatting runs through a Ruff hook rather than a second LSP.

## Installation

### rtk

Install `rtk` once per client, globally, so its command-intercept hook is
active — the hook routes supported commands through `rtk` automatically, with
no per-command discipline needed:

```bash
# Claude Code (default agent)
rtk init -g
```

Check `rtk config` afterward to confirm the hook is installed (it warns
`No hook installed` otherwise). Later, `rtk session` shows adoption per session
and `rtk discover` lists specific commands still bypassing it.

### git & mergiraf

Configure git to favor linear history and enable
[mergiraf](https://mergiraf.org/) as a syntax-aware merge driver, so conflicts
that are only formatting differences (AST-equivalent) resolve automatically
instead of landing on the agent:

```bash
git config --global pull.rebase true
git config --global merge.ff only
git config --global merge.conflictStyle diff3
git config --global merge.mergiraf.name mergiraf
git config --global merge.mergiraf.driver 'mergiraf merge --git %O %A %B -s %S -x %X -y %Y -p %P -l %L'
```

Apply mergiraf to all files globally by adding this line to git's global
attributes file (`~/.config/git/attributes`, git's default — no extra config
needed):

```text
* merge=mergiraf
```

### Claude Code

```bash
uv run scripts/sync.py
```

Copies `rules/agent-harness.md` into `~/.claude/rules/` (a global rule loaded at
session start; your own `~/.claude/CLAUDE.md` is left untouched unless it is a
legacy copy of this ruleset, which is removed) and installs the
plugin (skills, the bundled language servers, the Ruff/rumdl hooks, the
chrome-devtools MCP dependency, the bundled `notion` MCP server, and the
attribution `settings.json`). Re-run
after every update to this repo, then restart Claude Code to apply.

## What's Included

### Rules (always-on)

A single consolidated `rules/agent-harness.md` holds the behavior that applies
regardless of which skill is active — guard duty and scope control,
documentation currency, conversational register, CLI tooling preferences, and
the rules for when each workflow skill is invoked. Detailed, stage-specific
procedures live in the skills instead.

Origins are not tracked per rule — they are noted here as inspiration instead:

- In-house practices, refined by systematically interrogating Claude about its
  training biases at each stage of the development flow and writing
  counterweight rules against them.
- [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills)
  — Karpathy-inspired execution discipline.
- [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) —
  YAGNI-driven decision ladder.
- [juliusbrussee/caveman](https://github.com/juliusbrussee/caveman) — concise,
  professional prose compression.

See [`docs/rules-and-skills.md`](docs/rules-and-skills.md) for how to extend the
ruleset and add a skill, and [`CONTRIBUTING.md`](CONTRIBUTING.md) for project
structure, versioning, and cross-tool references.

### Skills

| Skill             | Source                                                          | License | Description                                                                                                                                                                 |
| ----------------- | --------------------------------------------------------------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `agent-readiness` | [Factory AI](https://www.factory.ai/agent-readiness)            | MIT     | Scores a repository's readiness for autonomous AI agent development across 9 pillars with a phased plan; adapted from Factory AI's framework to modern tooling conventions. |
| `ast-grep`        | [ast-grep/agent-skill](https://github.com/ast-grep/agent-skill) | MIT     | Guides structural, AST-based code search and rule authoring; used as-is, no adaptation.                                                                                     |
| `planning`        | Own                                                             | MIT     | Produces the pre-implementation plan: scope, design decisions, and which of them need developer approval vs. autonomous resolution; mandatorily pairs with `product-review`. |
| `implementation`  | Own                                                             | MIT     | Governs how code gets written against an approved plan: paradigm choice, over-engineering discipline, idiomaticity, verbosity, and the task completion checklist.           |
| `review`          | Own                                                             | MIT     | Runs standard, adversarial, and over-engineering review passes, language-agnostic; auto-invoked after `implementation`; invokes `perf-review` autonomously on a performance signal. |
| `product-review`  | Own                                                             | MIT     | Reviews a change against product/spec intent and business-practical edge cases, language-agnostic; mandatory alongside `planning`, requests spec documentation when none was given. |
| `perf-review`     | Own                                                             | MIT     | Performance-focused review pass (complexity, N+1 queries, allocations, blocking calls), language-agnostic; not run by default — invoked by `review` on a signal, or on explicit request. |
| `commit`          | Own                                                             | MIT     | Governs commit message structure and file grouping; never runs without an explicit developer request.                                                                       |
| `pull-requests`   | Own                                                             | MIT     | Governs PR title/body conventions; never runs without an explicit developer request.                                                                                        |
| `django-review`   | Own                                                             | MIT     | Django/DRF-specific review conventions (ORM patterns, DRF exception handling, field nullability); a supplementary pass after `review` on Django repos.                  |

See [`docs/rules-and-skills.md`](docs/rules-and-skills.md) for the skill
authoring format and how Claude Code deploys rules and skills.

### MCP & LSP (Claude Code)

Set up by `scripts/sync.py`.

- **MCP**: the `chrome-devtools` and `notion` servers install with the plugin.
  No setup beyond auth — run `/mcp` to check login status and approve any
  pending server. [`docs/mcp.md`](docs/mcp.md) is the source of truth for what
  ships and the file-vs-plugin-dependency strategy.
- **LSP**: language servers for Python, Markdown, Bash, TypeScript/JavaScript,
  HTML/CSS, and Rust, declared internally in `.lsp.json`. See
  [`docs/lsp.md`](docs/lsp.md) and the
  [Language Servers](#language-servers-claude-code) prerequisites above.
- **Hooks**: auto-format/lint on edit and other lifecycle hooks. See
  [`docs/hooks.md`](docs/hooks.md).
- **Settings**: a bundled `settings.json` empties git/PR attribution — no AI
  co-authorship trailer or session URL on commits and pull requests.

## Design Decisions

### Global vs Project-Level

All rules in this plugin are **generic** — they apply to any project, not just
repos created from a specific template. This avoids:

- Copying identical files into every repository.
- Per-repo maintenance when upstream rules update.
- Loading redundant skill content on every agent session.

Cross-cutting agent context (doc references, readiness triggers, behavioral
directives, and skill orchestration) is consolidated into a single globally
available `agent-harness.md` rule. Stage-specific procedures (planning,
implementation, review, product-review, perf-review, commit, pull requests)
live in their own skills so they load only when relevant, instead of being
always-on.

### `review` vs. a platform's own code-review command

Claude Code (and possibly other clients) may ship its own generic code-review
capability (e.g. a `/code-review` command with low/medium/high/max/ultra effort
levels, `--fix`, `--comment`). Its description overlaps with this plugin's own
`review` skill — both review "the current diff" — so an ambiguous, unnamed
request ("review this") could resolve to either, even though the two names
aren't identical: the collision is in what each does, not just what each is
called, and that's true of any plugin skill whose name or description echoes
a platform built-in, not only this one. There's no structural precedence
between skills from different plugins/platforms; resolution is driven by how
each is named or described, not by a priority setting.

Two mitigations, at the two points this plugin controls:

- `agent-harness.md`'s automatic post-`implementation` trigger names the fully
  qualified `agent-harness:review` — a direct reference, not a fuzzy match, so
  that call site is deterministic regardless of what else is installed.
- For any other request, name the skill explicitly at the console:
  `/agent-harness:review` forces this plugin's methodology-specific pass
  (adversarial/over-engineering passes against this repo's own rules, plus
  autonomously invoking `perf-review` on a signal); `/code-review` forces the
  platform's generic, effort-scaled one. Explicit naming always wins over an
  unnamed, ambiguous ask.
