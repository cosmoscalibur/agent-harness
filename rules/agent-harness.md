# Technical Strategy & Execution Rules

Detailed procedures for planning, implementation, code review, commits, and
pull requests live in dedicated skills (`planning`, `implementation`,
`review`, `product-review`, `perf-review`, `commit`, `pull-requests`). This
file holds the behavior that must apply regardless of which skill is
active, plus the rules for when each one gets invoked.

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
- Justification-inversion suspicion: the same discipline in reverse — when a
  technical decision already made (a guard, a constraint, a schema shape) is
  defended with a business term ("audit", "quality control") that traces to
  no real requirement/ticket/spec, suspect the justification was built
  backward to defend the decision, not derived from it. Invalidating that
  premise reopens whatever alternative was dismissed by citing it — it
  doesn't stay closed just because a PR mentioned it once.
- Attribution discipline: the same "never invent" rule, applied to causation.
  When diagnosing a failure, gather evidence before asserting a cause;
  separate what you observed from what you inferred, and never claim a change
  did or didn't cause something without evidence for it.
- Baseline discipline: the same evidence standard, applied to the comparison
  point. "Pre-existing" means present at the remote default branch's HEAD,
  fetched fresh — never a prior commit on the current branch, an earlier
  commit within the same PR/session, or stale local state. A defect
  introduced and then resolved purely within the PR's own commits is not a
  finding and is never narrated as one — in code comments, commit messages,
  PR bodies, or review output. Only a defect traceable to that remote HEAD
  is.
- Repo-state preflight: before mutating a repo, confirm a clean, expected
  starting state (working tree, branch, stash). An unclean tree, a detached
  HEAD, or an unexpected stash at task start is a stop-and-flag case, not
  something to work around — report it and wait. Discarding uncommitted work
  to reach a clean baseline is itself the hazard §4 forbids.
- Lint-suppression discipline: a lint/type-check suppression (`noqa`, `type:
  ignore`, `pylint: disable`, a config-level rule disable) is never a default
  agent action, no matter how spurious the violation looks — surface it and
  get explicit developer justification and approval first, the same
  approval-gate discipline as any other stop-and-flag case. This holds even
  more when the "violation" isn't confirmed to be an active, actually-fired
  rule: never preemptively suppress or disable a rule that hasn't been
  verified to trigger — a common agent failure is defensive silencing of a
  case that was never a real violation to begin with.

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
- Never use relative temporal references ("today", "currently", "for now")
  in documentation — they rot silently once the fact changes, with nothing
  forcing a revisit. State intentionality with its reason, not just the
  label: "this is a declared ceiling" or "this is deliberate" without the
  business reason it exists tells the next reader nothing they didn't
  already see in the code. Verbosity has an opportunity cost: lines spent on
  the obvious crowd out the room for the one non-obvious fact that actually
  mattered.
- Documentation never narrates the development process that produced it: no
  self-referential session language ("new finding", "confirmed with the
  user", "live confirmation", "pending validation") in comments, docstrings,
  commits, or PR bodies — that belongs in the conversation, never in a
  committed artifact. The same applies to a temporary diagnostic/analysis
  document: state the fact directly in the permanent artifact; never point to
  the scratch document as the source of truth.
- A comment/docstring pointing at another symbol for real, non-redundant
  context (a related concept, a complementary function) uses the ecosystem's
  structured cross-reference directive — Sphinx roles (`:func:`/`:class:`/
  `:meth:`/`:data:`) or a `seealso::` directive in Python, `{@link}`/`@see` in
  JSDoc, intra-doc links in Rustdoc — never free prose stating an equivalence
  claim ("same as X", "see Y", "same mechanism as Z"). A structured reference
  is tool-verified and breaks loudly if the target moves; a prose claim
  silently rots. Where no such directive is available or warranted, state the
  fact for this symbol on its own terms instead of comparing.
- Each documentation layer owns only its own subject: a constant's doc states
  what it represents, never the action of the code that consumes it (that
  belongs in the consuming function's docstring); a dependency's
  install/setup narrative belongs in README/CONTRIBUTING/docs, never inline
  near the call site that uses it.

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
  `implementation`. `planning` mandatorily runs `product-review` alongside
  it — comparing the request against order/spec documentation, requesting it
  if none was given — never deferred or treated as optional.
- After any change to non-test logic (behavioral code), invoke
  `agent-harness:review` automatically before reporting the task as done —
  it's a read-only pass, so it doesn't need an explicit request. Skip only for
  changes confined to docs, comments, or config, or to tests alone. Qualified
  name, not bare `review`: a platform's own generic code-review command may
  share that word and must not be picked up here instead.
- `review` invokes `perf-review` autonomously when it surfaces a qualifying
  performance signal (see `review`'s Additional checks) — the one
  review-stage skill allowed to self-invoke another without waiting for a
  developer request, since the signal it acts on is itself the evidence.
  Absent a signal, `perf-review` runs only on explicit developer request.
- Before proposing `commit`, confirm `agent-harness:review` actually ran on
  the change — a verifiable precondition, not just the implied order. Once
  `review` clears, ask whether to proceed to `commit` — draft the message only
  after the developer agrees; `git add` and `git commit` run only once the
  developer approves that drafted message.
- Cap self-resolution attempts before escalating. After two attempts at the
  same blocker with no progress, stop and ask the developer directly (§1's
  stop-and-ask) instead of retrying the same failing approach a third time.
