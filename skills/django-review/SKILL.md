---
name: django-review
description: >-
  Code-review conventions for Django/DRF projects — DRF's default exception
  handling, ORM patterns (filters, select_related/only), database
  constraints, and imports. Model/service names in the examples are
  generalized to apply to any Django project, not a specific repo.
  Complements `review` (language-agnostic) — run this pass after that one
  when the repo is Django/DRF.
---

# Code Review — Django/DRF conventions

Use these **after** `review` — this is the framework/ORM-specific
convention layer, not a replacement for the correctness/adversarial passes or
the general language-agnostic criteria.

## Rules

- **DRF's default exception handler.** See the equivalent, generalized rule
  in `review`. If the project has no custom `EXCEPTION_HANDLER` in
  `REST_FRAMEWORK` (settings), any uncaught
  `rest_framework.exceptions.ValidationError`/`ParseError`/etc. already
  converts on its own into the correct 4xx response with `.detail` as the
  body — a `try/except ValidationError: return Response(error.detail,
  status=400)` added "so the contract reads in the endpoint" changes nothing
  observable.

- **Pass what's used, not the whole object — including in ORM filters.** See
  the equivalent rule in `review` for function signatures; the same pattern
  shows up disguised in a
  `Model.objects.filter(fk=full_object)`/`get_object_or_404(Model,
  fk=full_object)`: Django accepts the full instance as a convenience, but
  that doesn't change that the filter only needs the id — use an explicit
  `fk_id=object.id`. Don't treat it as a special case just because the
  object was already in memory (e.g. `request.user`): passing the whole
  object when the `id` suffices is a real memory/time overhead versus
  passing that id (or a couple of specific fields) directly, whether it
  takes the shape of a function parameter or a `.filter()`/
  `get_object_or_404()` kwarg — a fully-hydrated instance carries its whole
  field set and internal state, not just the value actually read. This is
  separate from how the object was originally fetched: if that retrieval
  query has no explicit field list (no `.only()`/`.values()`), that's its
  own performance risk — more memory, bandwidth, and time spent fetching
  columns nobody reads — see `perf-review`'s field/relation-selection rule
  for that half of the problem. (Django's ORM does resolve `fk=full_object`
  by reading `full_object.pk` already in memory for a standard
  pk-based FK — no extra query from the filter itself in the common case;
  don't flag one unless the FK uses a non-default `to_field` that the
  retrieval query deferred.)

- **No redundant queries when the caller already has the data.** See the
  equivalent rule in `review`; in Django this shows up as an internal method
  that "re-queries for isolation" a related record the
  caller already loaded (e.g. re-fetching a parent object inside a service).
  Before accepting it, evaluate whether the caller can simply widen its own
  `.only()`/`select_related()`/`prefetch_related()` to include the needed
  fields/relations, instead of paying an extra query for "isolation between
  layers".

- **A DB constraint the production engine doesn't enforce is dead code, not
  documented intent.** See the equivalent, generalized rule in `review`.
  If a Django constraint (a conditional `UniqueConstraint`, a
  `CheckConstraint`, etc.) depends on a capability the
  project's database engine doesn't support (e.g. MySQL without support for
  the declared check type), flag it explicitly — leaving it declared "in
  case of a migration to Postgres" or as documentation isn't enough; in
  practice it protects nothing at runtime and can give whoever reads the
  model false confidence.

- **Import consistency — absolute imports are the default for new code,
  always.** House policy: new code defaults to absolute imports — even
  inside an existing file that already uses relative imports elsewhere,
  don't add a new relative import just because "that's what this file
  already does". Matching a file's existing style isn't a valid reason to
  make new code relative; the deviation to flag is any *new* relative
  import, not the legacy ones already in place (don't rewrite those unless
  the change already touches that exact line). Two legitimate exceptions,
  and only these: a real circular import that absolute imports can't
  resolve another way, and a same-level import to a sibling module within
  the same app (`from .models import Foo`, `from . import views`) — the one
  case Django's own official tutorial uses and teaches as idiomatic style.
  A relative import that climbs into a parent or sibling package
  (`from ..other_app import X`, `from ... import X`) is never covered by
  that exception — it's always the more severe case: harder to follow, more
  fragile to a module move, and can mask a real circular-import problem
  instead of solving it.

## Concrete cases

Illustrations of `review`'s general rules in Django/DRF terms
(model/service names generalized):

- **Unjustified defensiveness, DRF version.** A `try/except DatabaseError`
  around a side effect that has never failed in production, or an
  `int(request.data[...])` cast to `ParseError` "just in case" with no
  evidence that the frontend (which you consume end-to-end) would ever send
  something different — see the defensiveness rule in `review`.
  Illustrates the caveat "does this crash on its own or not?": removing two
  legitimately excessive defensive checks from an endpoint can also remove
  the only range validation on a business fiscal year — with no replacement,
  nothing else failing in its place — reintroducing the bug of persisting a
  record for a nonexistent fiscal period that the check existed to prevent.
  An out-of-range year is still a valid integer for the column: nothing
  crashes on its own.

- **Architecture first, DRF version.** Before accepting a new admin
  interface or endpoint, ask whether another one already solves the use
  case. Before accepting a mixin not seen elsewhere in the repo, or an
  explicit `http_method_names` as a reasonable idiom, run `ast-grep`/`grep`
  to confirm it's genuinely unprecedented.

- **Rename without auditing call sites, Django version.** A service rename
  that changes its signature (from taking the user instance to taking just
  its `id`) updates the class and most call sites, but leaves one passing
  `self.request.user` (the object) instead of `.id` inside a nested
  function. Unit tests miss it when they call the method directly with the
  correct type — only a structural search or a second manual pass catches
  it. See the LSP call-site audit rule in `review`.

- **Invented business justification, ORM version.** An `on_delete=PROTECT`
  against a hard user delete that in practice never happens, when the user
  model already has its own soft-delete via an `is_active` flag — see the
  invented-justification-suspicion rule in `review`'s justification-audit
  pass.

- **Documentation as noise, Django version.** `help_text` is business
  meaning, not format or the rule that already governs it (that lives in
  the validator/serializer). Explaining permission logic that lives in the
  permission class inside a view is the same misplaced-layer failure — see
  the documentation-as-noise rule in `review`.

## Format

Same as `review`: `<file>:L<line>: <problem>. <fix>.` Classify every finding
(bug, risk, nit, question).
