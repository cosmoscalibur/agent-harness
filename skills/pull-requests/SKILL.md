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
- Template precedence: fill the repo's PR template if present
  (`.github/pull_request_template.md`, or a template under
  `.github/PULL_REQUEST_TEMPLATE/`); else, if this skill bundles one under
  `resources/`, use it; else follow the guidelines here. When using a template,
  skip sections that don't apply and include only what's relevant to this PR.
- State explicitly what was left out of scope. Don't assume it's inferred
  from the diff.
- Compute the PR's described changes/impact against the remote default
  branch, not local state that may be stale or diverged.

## Changelog fragment

- Create the changelog fragment as the final pre-PR step, once scope is
  frozen — never per commit, per change, or during implementation. Exactly
  one fragment file per PR/session.
- Name it from a single stable identifier, in priority order: the issue
  number it closes; else the branch name; else a generic session identifier
  when work lands directly on the default branch. One identifier → one file;
  change-types are entries inside that file, not separate files.
- If the target repo documents a changelog methodology, follow it (directory,
  format, entry syntax). Only when none is defined, use this default. Where
  the repo has no changelog workflow at all, still write the fragment.

## Branches

- Ensure the branch is up to date with the remote default branch before
  pushing (fetch, then rebase or merge as the repo convention dictates).
  Resolve any conflicts first — never push a branch that's behind and let
  the PR surface a stale diff.

## Note

Never open a pull request without an explicit developer request, per the git
safety boundary in `agent-harness.md` §4 and its §5 approval gates.
