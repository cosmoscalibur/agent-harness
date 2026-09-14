---
name: commit
description: >-
  Write commit messages and structure commits — imperative first line, when
  to add a body, issue references, and grouping so no file spans two commits.
  Use when creating a git commit after review has cleared, when asked to
  draft, propose, or preview a commit message or a commit grouping for
  approval, or when asked how to split/group changes.
---

# Commits

## Rules

- First line: imperative, concise, states the effect of the change.
  Conventional Commits format by default; only deviate if the repo's
  existing commit history shows a different, consistent convention already
  in place.
- Default to a subject-only commit. Apply `agent-harness.md` §2's omission gate,
  decided from the change you just made — not by re-scanning the diff: can you
  name in one clause a *why* the subject plus diff can't show — a non-obvious
  grouping, a removal/rename reason, a breaking change, a migration note, or a
  linked issue? No → subject-only. Yes → that clause is the body. Motivation
  the subject already implies (e.g., that a new capability was previously
  absent) is not such a *why*. If a body runs to bullets, each fact lives in
  one place: none restates a claim the subject already makes, enumerates the
  touched files (`git show --stat` already answers that), or carries
  operational/deployment status or a manual follow-up step that happened
  outside the diff (rollout, manual config, "still needs X" — that belongs in
  the PR description or an ops runbook, not the commit).
- Write for a future reader who lacks this session's context — another
  developer, or your later self, reconstructing *why* from the diff and the
  message alone. State the change and its rationale on their own terms; never
  reference author-side or ephemeral context: internal plan labels ("Tier 1",
  "phase 2"), the review or audit that prompted the work, chat shorthand, or
  "as discussed".
- Never attribute the commit to an agent: omit `Co-Authored-By` trailers and
  any other agent-signature line, even when a harness default instructs
  appending one — the commit is authored by the developer who approved it.
- Reference related issues/PRs at the end of the body, not inline.
- No file spans two commits: a file's whole change set lands in exactly one
  commit, never split or partial. This is *not* "one commit per file". The unit
  is one functional behavior — the smallest set of changes that together
  produce one observable effect, plus the docs describing them. A part with no
  effect on its own (a code path nothing calls yet, a config no code reads) is
  inert alone and ships with the change that activates it. Split two parts into
  separate commits only when each is independently effective *and* independently
  reviewable for correctness — never on layer/mechanism (front-end/back-end,
  code/config) or a discernible sub-topic alone, and never merely because they
  landed in the same session. Default to the fewest commits that clear that
  bar. When one file unavoidably carries two such problems, merge them or
  regroup so the overlap disappears — never a partial commit.
- A version bump or similar release bookkeeping is not its own commit: fold it
  into the commit of the change it marks, or the last commit of a multi-commit
  change that ships together.
- Describing what changed: the developer reviews and approves the drafted
  message and grouping before anything commits, so that review is the
  correctness net — draft from the changes you made this session rather than
  re-reading full diffs by default. Always ground the file set with a cheap
  check (`git status --porcelain` / `git diff --name-status`); it costs almost
  nothing and is the drift detector. Escalate to a full `git diff <ref>` /
  `git show <ref>` only when a staleness trigger fires: the cheap check shows
  files you didn't touch, a system-reminder reports the file was modified by
  the user or a linter/hook, you're describing work you didn't author this
  session or that predates a context compaction, or you're on a
  rebase/squash/amend where history differs from memory. A file already
  modified in the working tree that you don't recognize touching this
  session is included by default in the commit grouping — flag it to the
  developer for transparency, but never exclude it silently or leave it
  permanently uncommitted absent an explicit request to exclude it. That's
  distinct from §1's guard duty against the agent proposing new unsolicited
  work: the change already exists in the working tree, it isn't being
  proposed.

## Note

This skill owns commits end to end — both proposing them for approval and
executing them — and that ownership is exclusive: commit grouping and
messaging never belong to planning or implementation, and are never decided ad
hoc before this skill is invoked. Proposing or previewing *how* to group or
split commits is itself part of this skill, not only writing the final
message: invoke it for any request to commit, draft, propose, preview, or
group commits — not just the literal word "commit". Running `git add`/`git
commit` is the final step: never run them until the developer approves the
drafted proposal, per the git safety boundary in `agent-harness.md` §4 and its
§5 approval gates.
