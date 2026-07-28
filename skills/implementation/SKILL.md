---
name: implementation
description: >-
  Write and complete code changes against an approved plan — paradigm choice
  (functional vs. imperative), over-engineering/YAGNI discipline, declarative
  vs. procedural structure, idiomatic constructs, and comment/naming
  verbosity. Use while writing or modifying code, choosing between design
  approaches, deciding whether an abstraction is justified, or closing out a
  task (types, tests, docs).
---

# Implementation

Execute an approved plan (see `planning`). Evaluate each design choice on the
problem's actual nature — never default to a paradigm, pattern, or defense
level without justifying fit.

## Paradigm: functional vs. imperative

- Data transformation, business rules, branch-heavy logic: functional
  composition, immutability, pure functions.
- I/O, required side effects, stateful SDK integration: imperative/OOP as the
  domain demands. Don't force monads or functional wrappers onto inherent
  mutation.
- Never choose a pattern for elegance alone if it adds indirection without
  measurably fewer bugs or better readability.

## Over-engineering, validation, error handling

- Before adding an interface, abstract class, or indirection layer: state in
  one sentence what concrete problem it solves today. "Might need it later"
  doesn't count. YAGNI by default.
- Scale error handling to real impact radius (internal single-consumer code
  vs. exposed endpoint or sensitive data).
- Match a script's complexity to its impact radius and lifespan. A
  self-contained, single-skill, internal-use script not exposed to untrusted
  input needs no help text, defensive input trimming, or explicit error
  handling — a native traceback on failure is sufficient signal. Add those
  only when blast radius or reuse justifies them.
- Parse, don't validate, only at real trust boundaries: external user input,
  external API responses, LLM output before downstream use. Parse into a type
  that makes invalid state unrepresentable, once, at the boundary.
- Outside those boundaries: don't re-validate what type, caller contract, or
  prior flow already guarantees. Don't create a type for trivial internal
  structures just to apply the pattern.
- The trust boundary is the external system, not the agent's own workspace:
  local, reversible actions inside a version-controlled repo (editing or
  deleting a file) need no pre- or post-action validation — version control is
  the safety net.
- Fail fast on programmer invariants and genuinely unexpected states. Never
  silently absorb a bug signal.
- Data is obligatory by default: every input, field, column, or table is
  required unless a contract marks it optional explicitly (an optional/nullable
  type, a documented default, a config flag). Absence of obligatory data is an
  unexpected state — fail fast; never degrade or substitute a default for it.
- Never fail-fast where an architectural fallback already exists (e.g. a
  defined human-escalation or default-path fallback). Degrade to the known
  path instead. The license to degrade is a fallback or optionality declared
  in the contract, never inferred — the test is not "does this feel expected?"
  but "is the optionality or fallback declared?". Distinguish unexpected error
  (fail fast) from expected domain failure with a defined fallback (degrade).
- Prefer a plain function over a formal pattern (factory, strategy, observer)
  unless a real, non-hypothetical variation justifies it.
- Defensive code outweighing business logic signals over-engineering.
  Reassess.
- Deletion beats addition: prefer removing code to adding code when both fix
  the problem.
- The diff floor is code plus the types/tests/docs required by the
  completion checklist below; minimize within that floor, never below it.
  Shortest working diff, fewest files — but only after understanding the
  problem. The smallest change in the wrong place is a second bug.
- Resolution ladder — selects the technique for a task already accepted as
  valid and in scope. It never substitutes for confirming the request itself
  should proceed — ambiguous scope, skipped tests, or an invented business
  rule are reasons to stop and ask, not inputs to the ladder. Take the first
  that applies: reuse what's already in the codebase (before a multi-site
  reuse check or edit — rename, signature change, replacing a call pattern —
  confirm every real site with a structural search (ast-grep) first, see
  `agent-harness.md` §4) → stdlib → a native platform feature (HTML input
  type, CSS, DB constraint) → an installed dependency (use it; don't add a
  new one for a few lines of code) → otherwise the minimum code that works.
  Skip anything speculative and say so in one line.
- Between two equally small stdlib options, pick the one correct on edge
  cases, not the shorter one.
- Well-formed but underspecified request, within approved scope: ship the
  simplest version that plausibly satisfies it, then state the gap ("Did X;
  Y covers it. Need full X? Say so."). Don't stall on a question you can
  default.

## Declarative vs. procedural

- Declarative when the problem is defined by outcome, not steps:
  infrastructure, schemas, queries, condition→action rules.
- Procedural when order intrinsically matters, dependencies are sequential,
  or flow control is needed (retries, multi-step transactions, intermediate
  state).
- Base the choice on problem structure, not surface domain, and independent
  of the functional/imperative choice above — a declarative rule table can be
  implemented imperatively; a pure function can still encode a procedural
  step sequence.

## Idiomaticity

- Use constructs native to the language in use (Python
  comprehensions/generators, Go slices/interfaces, Rust/Kotlin pattern
  matching, JS/TS optional chaining/destructuring) over literal translation
  from another language.
- Follow the ecosystem's own naming, structure, and error-handling
  conventions.
- This governs form, not quantity — see over-engineering above for how much
  structure is justified.

## Verbosity

- Documentation follows `agent-harness.md` §2's omission gate: before writing a
  comment or docstring, name what it adds that the code or signature can't show
  — the *why* (design decision, trade-off, exception), or the contract's
  non-obvious part; if you can't name it, don't write it. So: no comment
  restating what the code says (e.g., listing the elements of a named list
  being iterated), and no docstring paraphrasing the function name.
- Keep names clear and concise, per the language's and codebase's own
  convention.

## Completion checklist

- Every new/changed function, endpoint, or rule ships with explicit types and
  minimal docs at completion — not deferred.
- "Docs current" here excludes the release changelog fragment: it is
  PR-scoped and created once at PR preparation (see the `pull-requests`
  skill), not per change during implementation.
- Every non-trivial function/rule ships with a test at completion. Skip only
  for: pure delegation with no branching or transformation,
  framework/scaffold-generated code, or trivial constant/config definitions.
  Any other omission is debt, not a default.
- If execution diverges from the approved plan, flag it explicitly. Never
  apply silently.
- Assert the anti-patterns the `review` skill checks are absent, rather than
  leaving them for review to catch: no new `noqa`/lint suppression, no silent
  drop of required data, no speculative parameter or option added "for later".
- At task close: plan approved, types/tests/docs consistent and current. Any
  gap is declared debt, not omitted.
