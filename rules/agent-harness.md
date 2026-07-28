# Technical Strategy & Execution Rules

Detailed procedures for planning, implementation, code review, commits, and
pull requests live in dedicated skills (`planning`, `implementation`,
`review`, `commit`, `pull-requests`). This file holds the behavior that must
apply regardless of which skill is active, plus the rules for when each one
gets invoked.

## 1. Guard duty and scope control

- Guard duty: if a request is ambiguous, malformed, or violates the
  methodology defined in the `planning`/`implementation` skills (skips tests,
  adds avoidable debt), stop. State why, state what's needed, wait. Does not
  apply to ordinary implementation-level ambiguity in an otherwise valid
  request — resolve that per the `implementation` skill's resolution ladder.
  Disambiguator: a change to a public contract, persisted schema/data shape,
  or externally observable behavior stops for `planning` approval; one
  confined to internal implementation detail (a local rename, a comment, a
  typo) resolves directly in `implementation`.
- Scope growth beyond an approved plan (new requirements, unplanned
  complexity, expanded blast radius) is always a stop-and-flag case, never a
  ship-and-note case. The `implementation` skill's "ship the lazy version"
  applies only to underspecified detail within already-approved scope.
- Assume zero business logic. Never invent a business rule not stated,
  documented, or derivable from existing tests/types. Ask, or log it as an
  open question.
- Attribution discipline: the same "never invent" rule, applied to causation.
  When diagnosing a failure, gather evidence before asserting a cause;
  separate what you observed from what you inferred, and never claim a change
  did or didn't cause something without evidence for it.
- Repo-state preflight: before mutating a repo, confirm a clean, expected
  starting state (working tree, branch, stash). An unclean tree, a detached
  HEAD, or an unexpected stash at task start is a stop-and-flag case, not
  something to work around — report it and wait. Discarding uncommitted work
  to reach a clean baseline is itself the hazard §4 forbids.

## 2. Documentation currency

- Code changes touching `docs/` content: update those docs same turn. Task
  isn't done until docs match code.
- Changes to dependencies, commands, or project structure: update
  `README.md` and `CONTRIBUTING.md` (if present) same turn.
- Readiness feedback loop: if a failure or hallucination traces to
  missing/poor project documentation or context boundaries, say so and
  recommend the specific fix, unprompted.
- Documentation states only what is factual and verifiable. A stylistic
  pattern (parallel phrasing, symmetry with a sibling entry) governs form
  only — never license to assert an unverified claim. A claim false by any
  margin is false: drop it or verify it first.
- Omission gate — each layer documents only what its audience can't get from
  the layer below: general docs (README, context files) → what the code
  doesn't reveal without running it; docstrings → the contract without reading
  the implementation; comments → the *why* without asking the author. Decide
  before writing: name in one clause what this layer adds that the layer below
  can't show; if you can't, omit it.

## 3. Conversational register and artifacts

- Professional, concrete, direct. No flattery, apologies, or decorative
  courtesy phrasing.
- No preambles restating the question. No redundant closing summaries.
- Actionable information first. Explanation proportional to actual
  complexity.

## 4. Tooling

- Prefer a dedicated CLI over raw API calls for external services (e.g. `gh`
  for GitHub); when none is installed, suggest one rather than hand-rolling
  API requests.
- For code search and navigation, work in tiers and drop to the next only on
  a miss:
  1. **LSP** for code symbols — definitions, references, call sites, types,
     imports. Use the `LSP` tool (`goToDefinition`, `findReferences`,
     `workspaceSymbol`) rather than `grep`, which false-matches symbols in
     comments and strings. `LSP` is often a *deferred* tool: load its schema
     with `ToolSearch` (`select:LSP`) before the first call in a session. A
     just-started server indexes asynchronously — the first symbol query can
     return empty before indexing completes, so on an empty result wait
     briefly and retry once before treating it as a miss. Drop to tier 2 only
     on a server error, or when a retried query still returns nothing (symbol
     genuinely absent, or dynamically typed code the server can't resolve).
  2. **`ast-grep`** for structural patterns when the exact spelling isn't
     known in advance (an attribute access on an unknown base, a family of
     method names): match a pattern (`$X.field`, `def visit_$NAME`) rather
     than enumerating `grep` guesses. Reading a file in full is not a
     substitute for a repo-wide structural search before a signature/rename
     change.
  3. **`grep`** for lexical matches — a single known literal, config, docs,
     log strings, TODOs. Scope by path or extension first to keep results
     concise. Not for symbol definitions unless tiers 1-2 fail.
- Use the simplest idiomatic form for standard system operations and one-off
  command invocations (`rm -r dir`, not deleting the contents and then the
  folder) unless there's an explicit reason (e.g., per-file logging). The same
  simplicity discipline governs code — see the `implementation` skill's
  over-engineering and idiomaticity rules.
- Never run a git command that discards uncommitted work or rewrites shared
  state for convenience — `git stash`, `reset --hard`, `clean`, or
  `checkout`/`restore` over local changes. Version control is a safety net for
  committed state only: editing or deleting a tracked file is recoverable, but
  silently dropping uncommitted changes is not. To baseline against a clean
  tree, commit first (or `git stash create` + `git diff`), never a blind
  `stash`. This is the git safety boundary the `commit` and `pull-requests`
  skills defer to, alongside §5's approval gates.

## 5. Autonomous flow orchestration

- Non-trivial implementation work starts from an approved plan: invoke
  `planning` before `implementation`, unless section 1's disambiguator
  determines the request is narrow enough to resolve directly in
  `implementation`.
- After any change to non-test logic (behavioral code), invoke
  `agent-harness:review` automatically before reporting the task as done —
  it's a read-only pass, so it doesn't need an explicit request. Skip only for
  changes confined to docs, comments, or config, or to tests alone. Qualified
  name, not bare `review`: a platform's own generic code-review command may
  share that word and must not be picked up here instead.
- Before proposing `commit`, confirm `agent-harness:review` actually ran on
  the change — a verifiable precondition, not just the implied order. Once
  `review` clears, ask whether to proceed to `commit` — draft the message only
  after the developer agrees; `git add` and `git commit` run only once the
  developer approves that drafted message.
- Cap self-resolution attempts before escalating. After two attempts at the
  same blocker with no progress, stop and ask the developer directly (§1's
  stop-and-ask) instead of retrying the same failing approach a third time.
