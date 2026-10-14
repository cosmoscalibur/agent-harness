---
name: planning
description: >-
  Produce an implementation plan before non-trivial code changes — scope, key
  design decisions, open ambiguities, and which decisions need developer
  approval vs. which are autonomous. Use before starting any non-trivial
  implementation, when a request could alter a public contract, persisted
  schema, or externally observable behavior, or when a task needs to be
  framed as a verifiable, test-first goal.
---

# Planning

Produce a plan before non-trivial implementation begins. Do not execute
without explicit developer approval on the plan.

## Rules

- Before starting analysis, update the current branch with the remote
  default branch through git's configured integration (`git pull origin
  <default-branch>`, which applies the repo's or global `pull.rebase`/
  `merge.ff` settings). A plan built on stale local state can target code that's
  already changed upstream. Stop and flag instead of updating when the tree
  isn't clean (`agent-harness.md` §1's repo-state preflight), the update
  conflicts, no integration is configured (the pull fails on divergent
  branches), or it would rewrite commits already pushed.
- The plan states: scope, key design decisions, open ambiguities.
- Evaluate each design decision on the problem's actual nature — never
  default to a paradigm, pattern, or defense level without justifying fit;
  state that justification as one of the plan's key design decisions.
- Flag which decisions need developer consultation (architecture trade-offs,
  contract changes, business-rule ambiguity) vs. which are autonomous (no
  impact on contract or observable behavior). Don't mislabel either
  direction.
- Don't anticipate every internal function in the plan. Resolve unforeseen
  details autonomously per the `implementation` skill's resolution ladder;
  state the assumption inline.
- Frame the task as a verifiable, test-first goal: "add validation" → write
  failing tests for invalid input, then pass them. "fix bug" → reproduce with
  a test, then fix. "refactor X" → tests green before and after.
- Invoke `product-review` alongside this skill, not after it, for any
  non-trivial change: it compares the request against the order/spec
  documentation and requests that documentation when none was given.

## Handoff

Once the plan is approved, proceed to the `implementation` skill. If
execution has to diverge from the approved plan, that gets flagged
explicitly during `implementation` — never applied silently.
