---
name: review
description: >-
  Review code changes for functional correctness, adversarial edge cases,
  over-engineering, and performance. Use after implementation work completes,
  when explicitly asked to review a diff or PR, or when auditing existing
  code against the coding methodology.
---

# Code Review

## Rules

- No courtesy validation before flagging problems. Report the finding
  directly.
- Standard pass: functional correctness against contract/spec, readability,
  adherence to the `implementation` skill's paradigm, over-engineering,
  declarative/procedural, idiomaticity, and verbosity rules.
- Architecture-first pass: before accepting a new surface (endpoint, admin,
  service) as necessary, check whether an existing one already covers the
  use case. Before discussing an unusual code pattern (an unseen mixin, an
  explicit override of a framework default) as a reasonable idiom, confirm
  with a structural search (ast-grep) that it's genuinely unprecedented in
  the repo rather than eyeballing the diff — see `agent-harness.md` §4.
- Documentation pass: for any docs the diff adds or changes (README, `docs/`,
  docstrings, comments), verify each claim is factual and check it against
  `agent-harness.md` §2's omission gate — no layer restating what's visible
  one level below.
- Justification-audit pass: treat the PR body and its code comments as audit
  material — verify every falsifiable technical claim against the real
  code/environment, and check a "same criteria as X" claim line-by-line
  against X. Apply `agent-harness.md` §1's justification-inversion suspicion
  to any technical decision backed by a business term with no traceable
  requirement; when that premise falls, reopen whatever alternative was
  dismissed by citing it. Name explicitly any signal of missing human
  oversight: a "pending" checklist item at review request, documentation
  narrating the agent's own justification to the developer instead of
  stating facts, or an architecture decision resting on an apparently
  invented requirement.
- Adversarial pass: generate breaking inputs — null/empty, concurrency,
  reordering, partial dependency failure. Challenge every unguaranteed
  assumption. Silent omission of a feature or edge case is a valid finding,
  same as silently wrong code. When the diff changes a pattern that also
  appears elsewhere in the codebase, confirm full coverage with a structural
  search (ast-grep) rather than eyeballing the diff — see `agent-harness.md` §4.
- Over-engineering pass: flag excess, not just absence, per the
  `implementation` skill. A mechanical touch is still a touch — a forced
  reformat or lint-driven pass that happens to reach a legacy symbol is the
  opportunity to clean it up, not a reason to skip it as unrelated.
- Performance pass, always run: algorithmic complexity, N+1 queries,
  avoidable allocations, blocking calls on critical paths, lazy loading where
  applicable, explicit column/field selection in ORM/dataframe queries over
  full fetches.
- Product-intent pass: a design that's internally consistent still needs to
  serve the actual business objective — ask the finer question (can the same
  author repeat an entry within the same period, not just can there be N
  entries at all), and trace any UX/API decision (an edit-permission flag,
  data hidden server-side) to a real resolved flow or a real security/
  business reason. A name must not contradict the real constraints on it (a
  "free-form" field with a max length and a non-blank check isn't free-form).
- Classify every finding: bug, risk, nit, or question. Over-engineering
  findings: delete, stdlib, native, yagni, or shrink. This classification is
  the severity signal — don't add a separate ranking.
- Format: `<file>:L<line>: <problem>. <fix>.`
- Report lint violations. Never silence, suppress, or auto-ignore one — a
  `noqa`/skip-lint directive must be scoped exactly to what it declares; run
  the linter yourself over the full diff before accepting that a restriction
  is being dodged as "arbitrary".
- Run an independent typo sweep over the diff every time, zero tolerance —
  don't rely on catching typos incidentally while reviewing other axes.
- If context is insufficient for a given axis, say so explicitly. Never skip
  it silently.
