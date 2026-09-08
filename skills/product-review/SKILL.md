---
name: product-review
description: >-
  Review a change against product intent — order/spec documentation, edge
  cases from a practical business perspective, and whether the design serves
  the actual objective, not just internal consistency. Language- and
  stack-agnostic. Mandatory alongside `planning` for non-trivial changes: if
  no spec/order documentation was given, request it before proceeding.
---

# Product Review

Reviews whether a change actually serves the request behind it, not just
whether the code is internally consistent. Runs mandatorily alongside
`planning` for any non-trivial change — see `planning`'s rules and
`agent-harness.md` §5. Not a substitute for `review`'s correctness pass
or `perf-review`'s performance pass.

## Rules

- Compare the change against the order/spec documentation for the request (a
  ticket, a requirements doc, an existing spec). If none was given, request
  it explicitly before proceeding — never infer the business rule the
  request is trying to satisfy from the diff alone (`agent-harness.md` §1:
  assume zero business logic).
- Ask the finer question, not the obvious one: not "can there be N records
  per customer?" (obvious), but "can the same author leave N records in the
  same period, or should it be 1?". Cardinality, uniqueness, and
  repeat-entry rules need the specific business scenario, not the generic
  one.
- Trace any UX/API decision (an edit-permission flag, data hidden
  server-side) to a real resolved flow or a real security/business reason —
  not internal consistency alone. What happens if the record is wrong and
  the author can't fix it — does it escalate to support, or is that path
  undefined? Hiding data on the backend that the frontend could simply not
  render isn't a design win without a real reason behind it — it's an extra
  problem for whoever needs that data later.
- A name must not contradict the real constraints on it: a "free-form" field
  with a max length and a non-blank check isn't free-form — reserve
  "free-form" for something with no restriction beyond being text.
- The design must serve the actual business objective, not just be
  internally consistent with itself — internal consistency is a floor, not
  the goal.
- Generate edge cases from the practical/business angle, not only the
  technical one: a date range crossing a fiscal-year boundary, a quantity of
  zero versus none supplied at all, a state transition a real user would
  plausibly attempt versus one only a fuzzer would reach.
- Classify every finding: bug, risk, nit, or question — same classification
  as `review`, so both passes' output composes.
- Format: `<file>:L<line>: <problem>. <fix>.`
