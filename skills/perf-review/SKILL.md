---
name: perf-review
description: >-
  Review a change for performance — algorithmic complexity, N+1 queries and
  missing field/relation selection, hot-query indexing, avoidable
  allocations, and blocking calls on critical paths. Language-agnostic. Not
  run by default: `review` invokes it autonomously on a qualifying signal, or
  a developer requests it directly.
---

# Performance Review

Not a default pass — `review` invokes this autonomously when it surfaces a
qualifying signal (see `review`'s performance-signal rule), or a developer
requests it directly on a diff/PR.

## Rules

- Algorithmic complexity: flag any operation whose cost scales worse than
  the problem needs — a nested loop over the same collection an index/map
  lookup would flatten, a repeated linear scan where a set/dict membership
  check suffices.
- N+1 queries and missing field/relation selection: a query issued once per
  item in a loop where a single batched query (a join,
  `select_related`/`prefetch_related`, an `IN` clause) would do. The same
  missing explicit selection is a risk even with no loop in sight: fetching
  every column/relation when the caller only needs a few pays an avoidable
  data-transfer and deserialization cost on every call, and leaves a lazy
  relation sitting there to trigger an N+1 the moment someone iterates over
  it later. Flag the absence of an explicit field/relation list on its own
  merits — don't wait for a loop to make the N+1 visible before flagging it.
- Hot-query indexing: for a query on a path called frequently or over a
  large table, verify the columns used in filtering, ordering, and join
  conditions have a supporting index (check the schema/migrations) — flag a
  probable full-table-scan risk when none is evident.
- Avoidable allocations: a new collection built only to immediately reduce
  it to one value, a copy where a view/slice/reference would do.
- Blocking calls on critical paths: synchronous I/O (network, disk, a
  blocking lock) on a path with a latency budget or called from
  concurrency-sensitive code, with no documented reason it can't be
  async/deferred/batched.
- Lazy loading where applicable: defer work (a query, a computation) until
  its result is actually needed, rather than eagerly computing it for every
  code path — including ones that discard it.
- Classify every finding: bug, risk, nit, or question — same classification
  as `review`.
- Format: `<file>:L<line>: <problem>. <fix>.`
