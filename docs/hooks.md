# Hooks (Claude Code)

This plugin ships hooks on Claude Code only, declared in
[`hooks/hooks.json`](../hooks/hooks.json) and installed with the plugin:

- `PostToolUse` hooks that auto-fix files on write/edit via bundled scripts —
  see [Script pattern](#script-pattern) for the current set.
- A `SessionStart` hook that injects context at session start — see
  [Session-start LSP hint](#session-start-lsp-hint).

## Why a hook and not a second LSP

Claude Code runs **one language server per language**. A language's LSP can
give type/structure intelligence without covering formatting or lint-autofix
(`basedpyright` for Python, `marksman` for Markdown do this), and a second LSP
per language can't be added to fill that gap. A `PostToolUse` hook fills it
instead: after Claude writes or edits a matching file, the hook runs the
language's linter/formatter on it.

## Structure

A plugin declares hooks in `hooks/hooks.json` at the plugin root (or inline as a
`hooks` key in `plugin.json`; a standalone file keeps them out of the
version-bumped manifest). The shape mirrors Claude Code's user hooks:

```json
{
  "hooks": {
    "<Event>": [
      {
        "matcher": "<regex over tool names>",
        "hooks": [
          {
            "type": "command",
            "command": "uv run --no-project \"${CLAUDE_PLUGIN_ROOT}/hooks/<script>.py\""
          }
        ]
      }
    ]
  }
}
```

- **Event** (e.g. `PostToolUse`, which fires after a tool call succeeds) —
  other lifecycle events exist (`PreToolUse`, `SessionStart`,
  `UserPromptSubmit`, …).
- **`matcher`** is a regex over **tool names**, not file paths — `Write|Edit`
  matches both edit tools. There is no way to match on the edited file's type
  here, so each hook script filters by extension itself.
- **`hooks[].type: "command"`** runs a shell command; Claude Code passes the
  tool payload as JSON on its stdin. Python is invoked through `uv run` (this
  project standardizes on `uv`), and `--no-project` keeps the run isolated from
  any surrounding project environment.
- **`${CLAUDE_PLUGIN_ROOT}`** resolves to the installed plugin's root directory
  — always reference bundled files through it, never a relative path.

See [`hooks/hooks.json`](../hooks/hooks.json) for the current entries.

## Script pattern

Every hook script (Python stdlib, no dependencies) follows the same shape:
read the stdin payload, take `tool_input.file_path`, return immediately unless
it matches the target extension, then run the language's tool via `uvx`
(fetches it from PyPI on demand, cached after first use — so `uv` is the only
prerequisite) to fix and format the file. Each call runs with `check=False`: a
lint failure is swallowed rather than blocking the edit, and any violation the
tool can't auto-fix is left for `implementation`/`review` to catch — the hook
never surfaces it back to the agent.

Two hooks currently follow this pattern:

| Script | Extension | Tool | Manual install |
| --- | --- | --- | --- |
| [`hooks/ruff_fix.py`](../hooks/ruff_fix.py) | `.py`/`.pyi` | [Ruff](https://docs.astral.sh/ruff/) | `uv tool install ruff` |
| [`hooks/rumdl_fix.py`](../hooks/rumdl_fix.py) | `.md` | [rumdl](https://github.com/rvben/rumdl) | `uv tool install rumdl` |

### Adding another hook

Add an entry under the appropriate event in `hooks/hooks.json`, put any script
in `hooks/` (not `scripts/`, which is for one-off tooling like the installer),
and reference it via `${CLAUDE_PLUGIN_ROOT}`. Invoke Python through `uv run` and
keep the script stdlib-only so it needs no environment setup.

## Session-start LSP hint

The `SessionStart` entry is not a formatter and does not follow the script
pattern above. It is a `command` hook that prints a static JSON payload with
`hookSpecificOutput.additionalContext`, which Claude Code injects into the
model's context at session start. Because the output is a constant, it emits
the JSON inline via `printf` rather than spawning an interpreter through
`uv run`.

Its purpose is to counter tool-schema *deferral*: with many tools present
(bundled MCP servers plus built-ins), Claude Code defers the `LSP` tool's
schema, so an agent must load it with `ToolSearch (select:LSP)` before the
first call. Injecting the directive at session start raises the salience of
that step and reinforces the tier order in `rules/agent-harness.md` section 4.
It is a nudge, not a guarantee — the hook cannot call `ToolSearch` itself; the
model still has to act on the directive.
