# Pillar 4: Documentation — guidance

Extended guidance for Pillar 4 of the agent-readiness audit (`SKILL.md`,
Step 2). The criterion table (D1–D8) and the cross-reference-accuracy rule live
in `SKILL.md`; this file holds the D3, D7, and D8 detail.

## D3 — Agent Context

An **agent context file** is the entry file an IDE or AI agent loads before
acting. Exactly two conventions are recognized as valid — `AGENTS.md` and
`CLAUDE.md`, no others. Evaluate whichever the repo uses, and never penalize
one for not being the other:

- **`AGENTS.md`** — the tool-agnostic cross-tool standard for agent context
  files. The standard defines only the file; a companion `.agents/` directory
  is a per-tool convention outside it.
- **`CLAUDE.md`** (with the `.claude/` directory) — Claude Code's native
  scheme. Claude Code also reads `AGENTS.md`, by default only when no
  `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` exists in the working
  directory or above it.

The **antipattern** is duplicating human-facing documentation into these
files instead of referencing it. Agent context files should **point to**
`README.md` and `docs/` as the single source of truth and add only
agent-specific instructions.

**Interop when both conventions coexist**: `AGENTS.md` and `CLAUDE.md` must
resolve to a **single source of truth** — one references, imports (`@path`),
or symlinks the other, or one is generated from the other. Two **divergent**
copies are an antipattern (the duplication rule applied to the two-file case);
flag them for consolidation.

**Agent-specific vs general content**: Restrictions and constraints are
**general** — they apply to both humans and agents and belong in **shared
documentation** (contributing guide, coding patterns, README), not in agent
context files. The evaluator must verify that restrictions found in the agent
context file (`AGENTS.md` / `CLAUDE.md`) are flagged as **misplaced** if they
are general-purpose.

- **Agent-specific** (belongs in `AGENTS.md` / `CLAUDE.md`): doc loading
  instructions ("Read `docs/architecture.md` before modifying core modules"),
  workflow commands, tool preferences, context loading order.
- **General** (belongs in shared docs): forbidden patterns, deprecated modules,
  naming conventions, required review processes, code style rules.

**Hot / warm memory model** (see `documentation_strategy.md`):
Agent context files, and README.md when they import it (`@README.md`), are
**hot memory** — loaded on every task.
`docs/` is **warm memory** — loaded on demand when the task touches that area.
Agent context files bridge the two tiers: they live in hot memory and point to
warm memory so the agent knows where to look for deeper context.

D3 evaluates whether agent context files provide the right agent-specific
additions on top of the shared documentation (D1 + D2). Content that belongs in
README or `docs/` is evaluated under D1 and D2 respectively. Coding patterns
and contributing guides should be read before planning and implementing.

| #    | Sub-criterion             | What to Look For                                                                              | Where                       |
| ---- | ------------------------- | --------------------------------------------------------------------------------------------- | --------------------------- |
| D3.1 | Agent workflow references | Pointers to warm-memory docs, task-specific loading instructions, workflow commands            | Agent context (`AGENTS.md` / `CLAUDE.md`) |
| D3.2 | Doc maintenance rules     | Instructions to keep docs in sync when modifying code                                         | Agent context (`AGENTS.md` / `CLAUDE.md`) |
| D3.3 | Minimal agent skills      | At least code review and documentation skills/subagents in `.agents/skills/` or `.agents/workflows/` (or the Claude equivalents `.claude/skills/`, `.claude/commands/`, `.claude/agents/`) | Agent context               |

**D3.3 — Minimal agent skills**:

The repo should provide at least two codified skills/subagents: **code review**
and **documentation**. These guide agents in repeatable tasks and reference
agent-readiness criteria as their quality baseline.

*Code review skill* should cover: lint/format compliance (S1–S3, S5), scoped to
changed files (S7), tests pass + coverage (T1, T4–T6), changelog fragment
(D7.2), doc maintenance (D3.2), PR template compliance (K2).

*Documentation skill* should cover: README currency (D1), architecture docs
(D2), code conventions (D8), API docs (D5, D5.2), changelog fragment (D7.2),
agent context (D3.2).

**Scoring D3**: D3.1-D3.2 score together as an L1 criterion (the agent
context file itself); D3.3 scores on its own as an L2 criterion: codified
review and documentation skills record how the agent must work to produce
correct output, which is documented knowledge, without enforcing it through
automation.

- D3.1-D3.2:
  - ✅ **Pass**: both present with accurate, current content
  - ⚠️ **Partial**: one present, or content exists but is outdated; or general
    restrictions are placed in agent context files instead of shared
    documentation
  - ❌ **Fail**: neither present, or agent files duplicate README/docs instead
    of adding agent-specific instructions
- D3.3: ✅ both a code review and a documentation skill/subagent; ⚠️ one of
  them; ❌ neither.

**Evaluating content accuracy**: Verify that agent context files reference
existing docs rather than restating them. Check that documented constraints
match the actual codebase state. Flag general restrictions in the agent
context file (`AGENTS.md` / `CLAUDE.md`) as misplaced.

## D7 — Changelog

| #    | Sub-criterion             | What to Look For                                                  |
| ---- | ------------------------- | ----------------------------------------------------------------- |
| D7.1 | Changelog exists          | `CHANGELOG.md` or release notes present                           |
| D7.2 | Progressive fragments     | Fragment directory (`changelog.d`, `newsfragments`) with one fragment per PR (not per commit/change), consolidated before release |

The fragment pattern is **manual** (no specific tool required) — agents create
**one fragment per PR/session** (never per commit or per change), agents or
release workflows consolidate before release. If the repo documents its own
changelog methodology, follow it; only where none is defined does the
single-fragment-per-PR default apply. The contributing guide (D6) must
document the fragment creation process.

**Scoring D7**: ✅ D7.1 + D7.2; ⚠️ only `CHANGELOG.md` without fragment
workflow; ❌ no changelog.

## D8 — Code conventions

Conventions must cover general coding standards (style guide, naming, patterns)
**and** the project's domain-specific quality standards, so that agents and
contributors produce consistent, correct output.

**Project-type convention recommendations** (evaluator guidance — these inform
D8 completeness, not scored as separate criteria):

| Project type   | Recommended convention topics                                                                         |
| -------------- | ----------------------------------------------------------------------------------------------------- |
| `cli-tool`     | CLI UX patterns: help text, exit codes, stdout/stderr separation, `--no-color` / `NO_COLOR`, signal handling |
| `web-app`      | Accessibility standards (WCAG target level), component patterns, responsive design guidelines          |
| `desktop-app`  | Accessibility standards (WCAG target level), platform conventions, keyboard navigation                 |
| `library`      | Versioning policy (semver), deprecation strategy, public API surface, backward compatibility           |
| `ai/ml`        | Model documentation standards (model cards), data conventions, reproducibility requirements            |
| `agent`        | Behavior contracts, tool inventory, safety boundaries, escalation rules                               |
| `qa-automation`| Test strategy conventions, naming, organization, test data management                                 |
| `cloud-service`| Infrastructure conventions, resource naming, environment promotion strategy                           |

**Scoring D8**: ✅ general conventions **and** domain-specific conventions
documented; ⚠️ general conventions present but domain-specific topics missing;
❌ no conventions documented.
