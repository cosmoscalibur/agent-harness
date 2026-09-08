---
name: review
description: >-
  Review code changes for functional correctness, adversarial edge cases, and
  over-engineering — language-agnostic. Use after implementation work
  completes, when explicitly asked to review a diff or PR, or when auditing
  existing code against the coding methodology. Invokes `perf-review`
  autonomously on a performance signal; product/spec fit is `product-review`'s
  job, not this skill's.
---

# Code Review

## Rules

- No courtesy validation before flagging problems. Report the finding
  directly.
- Standard pass: functional correctness against contract/spec, readability,
  naming semantics, adherence to the `implementation` skill's paradigm,
  over-engineering, declarative/procedural, idiomaticity, and verbosity
  rules.
- Architecture-first pass, at any level of granularity: before accepting a
  new surface (endpoint, admin, service) as necessary, check whether an
  existing one already covers the use case. Before discussing an unusual
  code pattern (an unseen mixin, an explicit override of a framework
  default) as a reasonable idiom, confirm with a structural search
  (ast-grep) that it's genuinely unprecedented in the repo rather than
  eyeballing the diff — see `agent-harness.md` §4.
- Documentation pass: for any docs the diff adds or changes (README, `docs/`,
  docstrings, comments), verify each claim is factual and check it against
  `agent-harness.md` §2's omission gate — no layer restating what's visible
  one level below. Flag: self-referential process narration, a reference to a
  temporary diagnostic document instead of the fact itself, a prose
  comparison ("same as X", "see Y") where a structured cross-reference
  directive was warranted, a constant's doc describing its consumer's action
  instead of its own meaning, install/setup narrative that belongs in
  README/CONTRIBUTING instead, and a placeholder/stub that isn't fully
  traceable — missing an explicit `NotImplementedError`/failing-test marker,
  missing a TODO documenting the pending work, or — when the repo keeps a
  roadmap document — that document left unupdated.
- Readiness feedback loop pass: if a failure or hallucination this task
  traced to missing or poor project documentation or context boundaries
  (README, CLAUDE.md, `docs/`), say so and recommend the specific fix,
  unprompted — this end-of-task point is where that friction is still
  precise enough to name, not a detail to let fade. The same applies one
  layer up: when the friction traced to the agent's own ruleset
  (`agent-harness.md`, a skill) or the developer's global `CLAUDE.md`
  instead — not a fact specific to this project — saving it as project-scoped
  memory alone isn't enough. Name the specific rule/file gap and recommend
  the edit, in addition to (not instead of) any immediate memory note kept
  for continuity. The test: would this same confusion recur in any project
  using this harness? If yes, it's a harness gap, not a project fact.
- Baseline-discipline pass: a "bug found and fixed" claim (in code comments,
  commit body, or PR description) is only valid against the remote default
  branch's HEAD (`agent-harness.md` §1's baseline discipline) — a defect
  introduced and resolved purely within the PR's own commits is not a
  finding and must not be narrated as one; flag any comment/commit that
  claims otherwise.
- Justification-audit pass: treat the PR body and its code comments as audit
  material — verify every falsifiable technical claim against the real
  code/environment, and check a "same criteria as X" claim line-by-line
  against X. Apply `agent-harness.md` §1's justification-inversion suspicion
  to any technical decision backed by a business term with no traceable
  requirement — concrete check for an "audit"/"quality control" claim: does
  the design actually preserve history (an edit trail), not just a
  deletion/status flag? Editable content with no prior version kept already
  contradicts the audit narrative. When the premise falls, reopen whatever
  alternative was dismissed by citing it. Name explicitly any signal of
  missing human oversight: a "pending" checklist item at review request,
  documentation narrating the agent's own justification to the developer
  instead of stating facts, or an architecture decision resting on an
  apparently invented requirement.
- Adversarial pass: generate breaking inputs — null/empty, concurrency,
  reordering, partial dependency failure. Challenge every unguaranteed
  assumption. Silent omission of a feature or edge case is a valid finding,
  same as silently wrong code. When the diff changes a pattern that also
  appears elsewhere in the codebase, confirm full coverage with a structural
  search (ast-grep) rather than eyeballing the diff — see `agent-harness.md` §4.
- Over-engineering pass: flag excess, not just absence, per the
  `implementation` skill. A mechanical touch is still a touch — a forced
  reformat or lint-driven pass that happens to reach a legacy symbol is the
  opportunity to clean it up, not a reason to skip it as unrelated. Includes
  unjustified privatization — a name marked private by default with no real
  encapsulation need, per `implementation`'s over-engineering rules.
- Performance signal → `perf-review`: performance is not reviewed by this
  pass by default. When the diff shows a qualifying signal — a query issued
  inside a loop with no batching/prefetch, a query or ORM call with no
  explicit field/relation selection at all (risk of over-fetching now, or an
  N+1 the moment a lazy relation gets touched later — the absence of an
  explicit list is the signal, not just the loop case), a bulk/batch
  endpoint, an unbounded collection materialized in memory, a blocking call
  on a path already known to be hot, or a query on a likely-hot/large-table
  path with no evident supporting index — invoke `perf-review` autonomously
  and note in the report that the signal triggered it. Absent such a signal,
  don't invoke or recommend it speculatively.
- Classify every finding: bug, risk, nit, or question. Over-engineering
  findings: delete, stdlib, native, yagni, or shrink. This classification is
  the severity signal — don't add a separate ranking.
- Format: `<file>:L<line>: <problem>. <fix>.`
- Report lint violations. Never silence, suppress, or auto-ignore one — a
  `noqa`/skip-lint directive must be scoped exactly to what it declares; run
  the linter yourself over the full diff before accepting that a restriction
  is being dodged as "arbitrary". An unauthorized suppression is itself a
  finding to report (`agent-harness.md` §1's lint-suppression discipline) —
  never resolved by applying or accepting the suppression during review.
- Run an independent typo sweep over the diff every time, zero tolerance —
  don't rely on catching typos incidentally while reviewing other axes.
- If context is insufficient for a given axis, say so explicitly. Never skip
  it silently.

## Additional checks

- **Unjustified defensiveness on internal surfaces.** An internal endpoint or
  function whose only caller is code you control end-to-end (not a third
  party) doesn't need a generic `try/except`, a defensive cast, or "just in
  case" payload validation around something that "might fail", absent real
  evidence (a measured incident, not a hypothetical) that the scenario
  occurs. The cost of unjustified protection isn't just extra code: it turns
  a real failure into a silent error the team ignores, and blinds
  support/engineering when the caller actually breaks the contract. Crashing
  is preferable to swallowing the error, unless (a) there's evidence of a
  real incident and (b) the consumer has adequate handling for that failure
  without affecting the end user. This applies equally to payload validation
  and to I/O (a `try/except` around a side effect that has never failed in
  production). See `django-review` for the concrete DRF-endpoint case.

  - **Caveat that matters — check this BEFORE asking for a guard to be
    removed: does removing the guard produce a real failure, or does it let
    invalid data through with no failure at all?** "Let it crash" is only the
    right alternative when the invalid data breaks something on its own
    further down (a numeric cast over non-numeric text raises; accessing an
    attribute on a null object also raises). If the invalid data is the SAME
    TYPE as valid data but outside the business range (a year that's still a
    valid integer for the column, an id with the correct format that just
    doesn't correspond to anything), removing the check doesn't cause any
    crash at all — it causes the bad data to persist silently with a
    successful response. That is strictly worse than the error being
    eliminated.

    This isn't a binary rule ("if it doesn't crash on its own, keep the
    guard") — the decision depends on how likely the scenario is, with three
    possible outcomes, not two:
    1. **Genuinely improbable** (the data's source is a client you control and
       would never generate it): fine to remove the guard with no
       replacement. Accepting the residual risk is a valid decision.
    2. **Real but low probability, and doesn't crash on its own**: removing
       the guard alone isn't enough — manually log the anomaly (an explicit
       exception/warning when the out-of-range data appears) for visibility,
       even without rejecting the request.
    3. **Non-negligible probability**: keep the rejection — the validation
       wasn't excess defensiveness, it's a real business rule.
    Before accepting that a guard should go under "don't be defensive", ask
    the two questions in order: first "how likely is this scenario, with
    what evidence?", and only if the answer is "improbable" ask "which line
    of code actually explodes if it happens anyway?" — if nothing explodes
    and the probability isn't negligible, the middle ground (manual logging
    without rejecting) is a legitimate answer you hadn't considered with only
    "keep vs. remove".

  - **Adjustment when the risk is about a shared pattern, not a single
    endpoint.** If the accepted risk scenario is about an input pattern
    shared by *all* endpoints of an entity (not an isolated one), the
    protection belongs in the shared layer (permissions), not reimplemented
    per feature — reimplementing it per endpoint is the same unjustified
    defensiveness, just repeated N times instead of once.

- **A guard that "should never happen" hides the bug, it doesn't prevent
  it.** If a value should always exist by construction of the flow (it comes
  from a URL with a guaranteed id, from an operation already validated
  earlier, from a record created in the same request), a silent
  `if x is None: return` over that value isn't error handling — it masks a
  real bug behind a no-op. Before accepting that guard, ask for the concrete
  scenario where the value can actually be missing; if none exists, the code
  should fail loudly (let it crash, or use a lookup that raises instead of
  one that degrades to `None`) so the bug surfaces the first time it occurs,
  instead of being lost as a silent return.

- **Don't re-validate an invariant the caller already guarantees.** If a
  method/service documents that it's exclusive to one context (e.g. "only
  for flow X"), and **all** of its call sites already filter by that context
  before invoking it, don't duplicate the same validation inside. That
  redundancy isn't free "double security" — it implies the component is
  actually more generic than its documentation claims, and adds a second
  source of truth for the same rule that can drift from the first. The
  gate's responsibility lives in one place — verify which is the more
  natural one (usually the caller, which already knows why it's invoking)
  and let the rest trust it.

- **Pass what's used, not the whole object.** If a function only reads the
  `id` (or two or three specific fields) of a related object, its signature
  should receive those values directly — not the whole object. Don't treat
  it as a special case just because the object was already in memory (e.g.
  the current session's user): passing the whole object when the `id`
  suffices is the same unnecessary coupling, whether it takes the shape of a
  function parameter or a query filter, and it's a real memory/time overhead
  on its own — a fully-hydrated object carries its whole field set and
  internal state where a scalar or a small dict of the specific fields used
  would do. That's a separate concern from how the object was originally
  fetched: a retrieval query with no explicit field selection pays its own
  memory/bandwidth/time cost regardless of how the result is later passed
  around — see `perf-review`'s field/relation-selection rule for that half.
  See `django-review` for the same pattern disguised in ORM filters.

- **No redundant queries when the caller already has the data.** Before
  accepting that an internal method "re-queries for isolation" a record the
  caller already loaded, evaluate whether the caller can simply widen its
  own field/relation selection to include what's needed. Isolation between
  layers doesn't justify paying an extra query if the data is already in
  memory one level up.

- **A single source of truth for the same business concept.** If two
  different functions need to evaluate the same domain condition (e.g. "has
  this declaration already been filed/finalized?"), they should rely on the
  same shared predicate, not each reimplement their own version of the
  condition. Divergence — even in a single omitted field — is a consistency
  bug waiting to manifest, not a style nit. The rule holds between methods
  too, not just between files: two methods evaluating the same condition
  (e.g. "is owner and is admin") with the logic written twice separately is
  premature over-disaggregation, not separation of concerns — split them
  only once the real rule diverges.

- **A pending-work TODO lives in a single place — the most natural one to
  find it, not every place that touches it.** Same source-of-truth principle
  as above, but for documentation instead of logic. If a field needs a
  "this needs migrating/cleaning up" note, that note goes where someone would
  first look when reviewing that field (typically the model that defines
  it), not repeated — not even partially — in every service/view that
  consumes it. A TODO split across two files, neither being "the" complete
  one, is over-documentation: when someone resolves it in one place, the
  other goes stale and nobody notices the drift until the next review.
  Before adding a pending-work note in a new file, ask whether it already
  exists (or should exist) in a more natural place, and consolidate there
  instead of duplicating.

- **A legacy field/toggle that a change replaces needs an explicit decision
  about its lifecycle.** It isn't enough for the new mechanism to "win" in
  the new logic if the old field is still writable elsewhere. The PR must
  decide and record it: is it retired (with a migration/backfill TODO), or
  is there a real reason for it to keep living in parallel? Ambiguity with
  no documented decision isn't acceptable — even if the decision is "left as
  a TODO with concrete measured numbers" (a quantified pending backfill),
  that's already a valid answer; "not mentioned" isn't.

  - **"Legacy" and "needs a backfill before it can be ignored" are
    contradictory — don't let the label pass without that nuance.** If a
    field truly doesn't matter, its data doesn't need migrating anywhere; if
    a backfill is needed to avoid losing real information (numbers measured
    in production/staging, not an assumption), that field is still a live
    source of truth today, even while on its way out. Calling it "legacy"
    without that clarification understates the risk of the window between
    "ignored in code" and "the backfill ran".
  - **Don't add new code or tests that depend on a field already marked for
    retirement.** If something is being decommissioned, the surface that
    touches it should shrink, not grow — including tests: writing a new test
    that instantiates the legacy field (even to prove it's now ignored) is a
    new dependency on something that's supposed to be on its way out. The
    guarantee that it's ignored should be enough for the existing code/TODO,
    with no need for added coverage that cements its presence.

- **A pattern copied from another module needs its underlying justification
  to apply here too.** If the PR adopts an existing pattern (soft-delete
  because another model uses it, a `try/except` because another endpoint has
  one) citing the precedent as the reason, verify that the real need behind
  that precedent (audit, traceability, a known incident) also exists in the
  new case. The analogy without that check copies the form without the
  function.

- **YAGNI for representations with no consumer.** Don't add `__str__`,
  derived properties, or an API representation "by convention"/"just in
  case" if nothing consumes it yet (not an admin interface, not logs, not an
  endpoint). If it isn't used, don't define it — add it when the first real
  consumer shows up.

- **Simplify what's used only once.** An intermediate variable that's read
  only once and adds no naming clarity can be assigned/passed directly at
  the point of use.

- **Review the reversibility of every terminal state in a state machine.**
  For any state with no manual exit transition (a "not applicable"/"done"),
  explicitly confirm whether a reasonable way back exists — even if
  automatic rather than manual — or whether its absence is justified. Don't
  assume it just because the transition map "looks complete".

- **Already-agreed domain naming conventions are enforced, not repeated as a
  suggestion.** If the team has already established a prefix or naming
  pattern for a specific domain (e.g. a prefix that marks "exclusive to a
  specific product/flow"), a new component in that domain that doesn't
  follow it is a deviation to fix in the same PR, not an optional style
  preference for later. The taxonomy isn't only about folders or business
  prefixes: before naming something `*Service`, confirm it meets the
  semantic pattern that term already carries in the repo, not just that it
  lives in `services/`.

- **If you accept the "don't be defensive if you control the input"
  principle, apply it to the whole diff, not just the first site where you
  noticed it.** It's common for a fix to remove a one-line `try/except` but
  leave a `.get(..., default)` or an `or []` two lines below, on exactly the
  same premise (the caller is yours, the config is yours). After finding the
  first case of unjustified defensiveness, sweep the same method/file again
  asking the same question of every remaining guard: what real scenario
  would trigger it? A fallback over cross-cutting config the entire
  application needs (settings, infrastructure feature flags) is the most
  deceptive case: if it were missing, other parts of the system would
  already have broken before reaching your guard, so the fallback prevents
  nothing — it only postpones the error to a point where it's harder to
  diagnose.

- **A docstring/comment doesn't mix languages within the same block.** If
  the file/module is already written in one language, a lone technical term
  in another ("backfill", "legacy") is fine when it has no natural
  translation or is jargon the team has already adopted, but avoid
  alternating full sentences between the two languages in the same
  paragraph — read it back and confirm it doesn't read like code-switching.

- **Documentation as noise — signs of the agent's personal notes.** Each
  layer documents its own responsibility: a UI help field (`help_text` in
  Django, `description` in other frameworks) is business meaning, not format
  or the rule that already governs it (that lives in the validator); the
  reason for an implementation decision lives in the code that implements
  it, not repeated in a domain doc and the changelog. The bar isn't "it took
  me effort to understand", it's "a future maintainer needs it and can't get
  it anywhere else" — see `agent-harness.md` §2. Concrete signs that a
  paragraph is the agent's personal note rather than documentation: comparing
  to an unrelated model with no functional link, pinning a library version
  inline, explaining the framework/ORM instead of the actual decision, or a
  "Summary:" prefix on a technical docstring (technical documentation states
  facts, it doesn't summarize for a non-technical reader). Explaining logic
  that lives in another module (e.g. permissions) at its point of
  consumption is the same misplaced-layer failure.

- **Signature-change call-site audit.** After a signature change (method
  rename, new/different parameters, type change), audit *every* call site —
  with LSP, not grep. Use `LSP prepareCallHierarchy` + `incomingCalls` on the
  method's definition: it returns every real call site along with the name
  of the enclosing function, with no noise from imports, `__all__` string
  entries, or text matches inside comments — grep does bring that noise, and
  can also fail silently if the method is invoked through a variable/alias.
  If `LSP` isn't available for the language, `findReferences` is the
  fallback (less precise: it doesn't group by calling function, and does
  count non-executable mentions). Watch the first query right after the
  server starts: it can return incomplete results (not empty — that's the
  deceptive case) while it finishes indexing the workspace; if the count
  looks low for a symbol you know is used across several modules, repeat the
  query once before trusting the result. See `django-review` for the
  concrete case of a rename that slipped through without this check.

- **A declared constraint/guard the runtime doesn't actually enforce is dead
  code, not documented intent.** A validation or constraint declared in code
  or schema but not actually enforced by the environment it targets (a
  database engine that silently ignores the declared check type, a config
  flag nothing reads) protects nothing at runtime — flag it explicitly.
  Leaving it declared "for a future migration" or as documentation isn't
  enough, and it can give whoever reads it false confidence. See
  `django-review` for the concrete Django/database case.

- **A test that only exercises framework/generated configuration proves the
  framework works, not your code.** A test on generated or framework-default
  configuration (an admin panel's field list, a serializer's `Meta`, a
  routed URL list) with no custom logic behind it — no override the test
  actually exercises — verifies the framework, not anything this codebase
  added (e.g., Django admin's `list_display`/`Meta` with no `get_queryset`/
  `save_model` override).

- **Before adding manual error handling in a request handler, check what the
  framework's own default handler already does.** A web framework's default
  exception-to-response mapping (DRF's `exception_handler`, Flask's error
  handlers, FastAPI's exception handlers, Rails' `rescue_from`) already
  converts a known exception into the correct response on its own. A
  `try/except` added "so the contract reads in the handler" that produces
  the exact same observable response is dead code reimplementing what the
  framework already does for free — confirm it produces something different
  before accepting it. See `django-review` for the concrete DRF case.

- **A field shouldn't have two different representations of "no value".** If
  a field can be both `NULL` and an empty string/collection with no distinct
  meaning between the two, that's a modeling inconsistency waiting to
  surface as a bug (a query that checks one but not the other, a form that
  clears to one while a migration defaults to the other) — pick one
  canonical representation of absence per field and enforce it. Django's own
  convention is the concrete instance: numeric fields use `null=True`; text
  fields use `blank=True` and avoid `null=True`, so "empty" has exactly one
  representation instead of two.
