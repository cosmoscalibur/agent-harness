---
name: pull-requests
description: >-
  Write pull request titles and descriptions — scope-specific titles, neutral
  impact descriptions, and explicit out-of-scope notes. Use when opening a PR
  or drafting PR body content after commits are ready to ship.
---

# Pull Requests

## Rules

- Title: specific about scope and observable effect. No "fix bug" or "update
  logic".
- Body: neutral, verifiable impact description. No promotional tone.
- Never attribute the PR to an agent: no `Co-Authored-By` trailer, agent
  signature, or generated-by note in the title, body, or the commits it
  contains — the PR is authored by the developer who approved it.
- Template precedence: fill the repo's PR template if present
  (`.github/pull_request_template.md`, or a template under
  `.github/PULL_REQUEST_TEMPLATE/`); else follow the guidelines here. When
  using a template, skip sections that don't apply and include only what's
  relevant to this PR.
- Distinguish a rejected alternative (a concrete option considered and
  actively decided against, with the reason) from genuine out-of-scope work
  (not done — pending, unrequested, or simply not reached). Never merge them
  under one heading: a rejected alternative gets its own line stating what
  was considered and why it was rejected; out-of-scope work states only what
  remains undone. Don't assume either is inferred from the diff — state both
  explicitly when they apply.
- Compute the PR's described changes/impact against the remote default
  branch, not local state that may be stale or diverged.

## Changelog fragment

- Create the changelog fragment as the final pre-PR step, once scope is
  frozen — never per commit, per change, or during implementation. Exactly
  one fragment file per PR/session.
- When the repo's methodology uses per-PR fragment files and doesn't define
  their naming, name the file from a single stable identifier, in priority
  order: the issue number it closes; else the branch name; else a generic
  session identifier when work lands directly on the default branch.
  Change-types are entries inside that one file, not separate files.
- If the target repo documents a changelog methodology, follow it (directory,
  format, entry syntax). Only when none is defined, use this default: a
  single `CHANGELOG.md` at the repo root, following [Keep a
  Changelog](https://keepachangelog.com/) — an `## [Unreleased]` section with
  the standard category headings (`Added`/`Changed`/`Deprecated`/`Removed`/
  `Fixed`/`Security`), one bullet per change-type entry, created if absent
  and appended to otherwise. Where the repo has no changelog workflow at all,
  still add the entries under this default.

## Branches

- Bring the branch up to date with the remote default branch before
  pushing, through git's configured integration (`git pull origin
  <default-branch>`, which applies the repo's or global `pull.rebase`/
  `merge.ff` settings) rather than a hand-picked rebase or merge. Resolve any
  conflicts first — never push a branch that's behind and let the PR surface a
  stale diff. When no integration is configured (the pull fails on divergent
  branches), stop and flag rather than picking one. When that update rewrites
  commits already pushed, the follow-up `git push --force-with-lease` waits for
  developer approval (`agent-harness.md` §5).

## Note

Open a pull request only on an explicit developer request, once the developer
approves the drafted title and body (`agent-harness.md` §5).
