---
name: agent-readiness
description: >-
  Score a repository's readiness for autonomous AI-agent development and
  produce a phased enhancement plan. Use when onboarding a repository for
  AI-assisted development, running a periodic audit of its tooling, docs, CI,
  and agent context for gaps, or planning developer-tooling modernization.
---

# Agent Readiness Evaluation

Evaluate how well a codebase supports autonomous AI-assisted development. Based
on
[Factory AI Agent Readiness](https://docs.factory.ai/web/agent-readiness/overview),
adapted to modern tooling standards and agent platform conventions.

## Workflow

### Step 0 — Gather Project Context

Before starting the evaluation, collect the following context. If the user does
not provide these in the prompt, **ask before proceeding**.

1. **Repository type**: `issues-only`, `pr-only`, or `both`.
   - `pr-only` → K1 (Issue templates) and K3 (Issue labeling) become **N/A**.
   - `issues-only` → K2 (PR template) becomes **N/A**.
   - `both` → all Task Discovery criteria apply.
2. **Documentation language**: e.g., `English`, `Spanish`.
   - Recorded in the Ecosystem table. During evaluation, flag mixed-language
     documentation (docs in one language, comments/commits in another) as ⚠️
     under D1 and D8, recommending uniform language for maintainability.
3. **Project type**: `cloud-service`, `web-app`, `desktop-app`, `cli-tool`,
   `library`, `ai/ml`, `qa-automation`, or `agent`.
   - Determines which criteria are **N/A** — excluded from the scoring
     denominator. See the applicability matrix in Step 2.
4. **Monorepo check**: Does the repository contain multiple project types?
   - If yes, collect all applicable types as a comma-separated list.
   - When multiple project types are declared, a criterion is **N/A only if it
     is N/A for all** declared types. If any type marks it ✅ or ⚠️, the
     criterion applies.
   - The scoring denominator uses the **union** of applicable criteria across
     all declared types.
   - The Ecosystem table records all types. Per-pillar evidence may note which
     subproject a criterion applies to.

### Step 1 — Detect the Ecosystem

Identify the primary language, framework, and platform from root-level
manifests and config, including notebooks/ML dependencies and GCP deploy files.
Record the ecosystem; it selects which sections of
`resources/modernization_recommendations.md` apply.

### Step 2 — Audit Each Pillar

Evaluate the repository against the **9 pillars** listed below. For each
criterion, check whether evidence exists in the repo. Mark as:

- ✅ **Pass** — criterion fully met
- ⚠️ **Partial** — exists but incomplete/outdated
- ❌ **Fail** — not found

#### Pillar 1: Style & Validation

| #   | Criterion                   | What to Look For                                                                |
| --- | --------------------------- | ------------------------------------------------------------------------------- |
| S1  | Linter configured           | Config file for a linter (ruff, eslint, clippy, golangci-lint)                  |
| S2  | Code formatter configured   | Formatter config or "format" in linter config (ruff format, prettier, rustfmt)  |
| S3  | Type checker configured     | Type checker config (pyright/mypy, TypeScript strict, Rust is typed by default) |
| S4  | Pre-commit hooks            | `.pre-commit-config.yaml` or husky/lint-staged; hooks must match current tools  |
| S5  | CI enforces lint/format     | CI workflow step that runs linter and formatter in check mode                   |
| S6  | Import sorting              | Import sort configured (ruff `I`, eslint-plugin-import, goimports)              |
| S7  | Linter targets changed code | Pre-commit and CI scope linting to changed files only (not full project)       |

S7 scope guidance (pre-commit/CI/full-project) and legacy-project handling:
see `resources/pillar1_style_validation.md`.

**Modernization signals**: If the repo uses isort/black/pylint separately →
recommend consolidation to ruff. If it uses tslint → recommend eslint. See
`resources/modernization_recommendations.md`.

#### Pillar 2: Build System

| #   | Criterion                | What to Look For                                                 |
| --- | ------------------------ | ---------------------------------------------------------------- |
| B1  | Build command documented | README or docs describe how to build/run                         |
| B2  | Dependencies pinned      | Lockfile exists (uv.lock, package-lock.json, Cargo.lock, go.sum) |
| B3  | Single-command install   | One command installs all deps (uv sync, npm ci, cargo build)     |
| B4  | Reproducible CI builds   | CI uses lockfile for dependency resolution                       |
| B5  | Dockerized build         | Dockerfile or compose file for containerised builds. See B5 in `resources/pillar2_build_system.md` |

B5 Docker best-practice sub-criteria (B5.1–B5.5) and scoring: see
`resources/pillar2_build_system.md`.

**Modernization signals**: `requirements.txt` → `pyproject.toml` + uv.
`setup.py` only → `pyproject.toml`. `yarn` classic → `yarn berry` or `pnpm`.

#### Pillar 3: Testing

| #   | Criterion                 | What to Look For                                                   |
| --- | ------------------------- | ------------------------------------------------------------------ |
| T1  | Unit tests exist          | Test files in the repo (test\_\*.py, \*.test.ts, \*\_test.go)      |
| T2  | Test framework configured | Config file (pytest.ini, jest.config, Cargo test)                  |
| T3  | Tests runnable locally    | Single documented command to run tests                             |
| T4  | CI runs tests             | CI workflow step that executes tests                               |
| T5  | Coverage tracking         | Coverage config or CI coverage step                                |
| T6  | Coverage threshold        | Minimum coverage enforced (fail_under, coverageThreshold)          |
| T7  | Integration tests exist   | Tests that exercise external dependencies or multi-component flows |
| T8  | Test factories/fixtures   | Data generation patterns (factory_boy, fishery, faker)             |
| T9  | TDD methodology           | Tests-first approach with both positive and negative test cases    |

T9 TDD-methodology evaluation (tests-first, positive/negative patterns) and
scoring: see `resources/pillar3_testing.md`.

**Modernization signals**: unittest → pytest. mocha → jest/vitest.

#### Pillar 4: Documentation

| #    | Criterion                        | What to Look For                                                                                                  |
| ---- | -------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| D1   | README with setup instructions   | Tech stack, prerequisites, build/run/test/lint commands, project structure, env vars (see `resources/documentation_strategy.md`) |
| D2   | Architecture documentation       | `docs/` with design docs, coding patterns, architecture. Auto-generated docs can replace manual docs; manual multi-file structure is needed only when auto-generated docs do not cover all aspects (e.g., examples, tutorials). Must include a `README.md` index (see `resources/documentation_strategy.md`) |
| D3   | Agent context                    | See D3 in `resources/pillar4_documentation.md`                                                                   |
| D4   | Environment variables documented | `.env.example`, settings docs, or env var table in README                                                         |
| D5   | API documentation                | Swagger/OpenAPI, or API docs (drf-spectacular, tsoa, protobuf docs). See D5 sub-checks below                      |
| D5.1 | User manual                      | End-user documentation (applies to `desktop-app` and `cli-tool` project types; N/A for others)                    |
| D5.2 | Auto-generated docs              | Generated documentation (cargo doc, Sphinx, typedoc, etc.) — applies to all project types                         |
| D6   | Contributing guide               | CONTRIBUTING.md or contributing section in README                                                                 |
| D7   | Changelog                        | See D7 in `resources/pillar4_documentation.md`                                                                   |
| D8   | Code conventions documented      | Style guide, naming conventions, patterns documented. Must include domain-specific conventions per project type (see D8 in `resources/pillar4_documentation.md`) |

**Cross-reference accuracy**: For every Documentation criterion, verify that
documented content matches the actual repository. Check that stated
versions match config files, documented commands are runnable, referenced
modules and directories exist, and described patterns reflect current code.
Mark as ⚠️ (partial) if the documentation exists but is outdated.

D3 Agent Context, D7 Changelog, and D8 Code conventions detail (sub-criteria,
scoring, and evaluator guidance): see `resources/pillar4_documentation.md`.

#### Pillar 5: Dev Environment

| #   | Criterion                         | What to Look For                                                                                                                                                                                            |
| --- | --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| E1  | Environment template              | `.env.example` or `envfile.template` with placeholder values                                                                                                                                                |
| E2  | Devcontainer config               | `.devcontainer/devcontainer.json`                                                                                                                                                                           |
| E3  | Docker Compose for local services | `docker-compose.yml` with DB, cache, etc.                                                                                                                                                                   |
| E4  | One-command local setup           | Makefile/justfile target, script, or documented single command. Prefer `just` (command runner) over `make` for new projects or non-build tasks; prefer `make` when incremental/file-based builds are needed. |
| E5  | Seed data mechanism               | Fixtures, seeders, or migration-based data population                                                                                                                                                       |

#### Pillar 6: Debugging & Observability

| #   | Criterion                     | What to Look For                                                          |
| --- | ----------------------------- | ------------------------------------------------------------------------- |
| O1  | Structured logging configured | Logging library with JSON/structured output (structlog, winston, tracing) |
| O2  | Error tracking                | Sentry, Bugsnag, or equivalent integration                                |
| O3  | Debug tools documented        | Debug instructions (debugpy, delve, node --inspect)                       |
| O4  | Distributed tracing           | OpenTelemetry, Jaeger, or cloud-native tracing                            |
| O5  | Health check endpoint         | `/health` or `/readiness` endpoint                                        |

#### Pillar 7: Security

| #   | Criterion                         | What to Look For                                                                  |
| --- | --------------------------------- | --------------------------------------------------------------------------------- |
| X1  | CODEOWNERS file                   | `.github/CODEOWNERS` or `CODEOWNERS`                                              |
| X2  | Security linting rules            | Security rules enabled in linter (ruff S, eslint-plugin-security, cargo-audit)    |
| X3  | Dependency vulnerability scanning | Dependabot, Snyk, or `cargo audit` in CI                                          |
| X4  | Secret scanning                   | GitHub secret scanning, gitleaks, or trufflehog                                   |
| X5  | Branch protection                 | Require PR reviews, status checks (GitHub setting — note if cannot audit locally) |

X3 dependency-update review-cooldown guidance: see
`resources/pillar7_security.md`.

#### Pillar 8: Task Discovery

| #   | Criterion                | What to Look For                                                      |
| --- | ------------------------ | --------------------------------------------------------------------- |
| K1  | Issue templates          | `.github/ISSUE_TEMPLATE/` directory with templates. See K1 in `resources/pillar8_task_discovery.md` |
| K2  | PR template              | `.github/pull_request_template.md`. See K2 in `resources/pillar8_task_discovery.md` |
| K3  | Issue labeling system    | `.github/labels.yml` or documented label taxonomy. See K3 in `resources/pillar8_task_discovery.md` |
| K4  | Project board / tracking | Link to project board or tracking tool                                |

K1 issue-template guidance, K2 PR-template sub-criteria and scoring, and K3
label-consistency guidance (all per repo type): see
`resources/pillar8_task_discovery.md`.

#### Pillar 9: Product & Experimentation

| #   | Criterion                 | What to Look For                                             |
| --- | ------------------------- | ------------------------------------------------------------ |
| P1  | Analytics instrumentation | Analytics SDK configured (Segment, Amplitude, PostHog)       |
| P2  | Feature flags             | Feature flag system (LaunchDarkly, Unleash, env-based flags) |
| P3  | Experiment infrastructure | A/B testing framework or experiment docs                     |

#### Project-Type Applicability Matrix

Criteria marked **N/A** are excluded from the scoring denominator based on the
project type collected in Step 0. Additionally, Task Discovery criteria (K1–K4)
are filtered by the repository type.

| Criterion              | cloud | web | desktop | cli | library | ai/ml | qa-auto | agent |
| ---------------------- | ----- | --- | ------- | --- | ------- | ----- | ------- | ----- |
| B5 Dockerized build    | ✅    | ✅  | N/A     | N/A | N/A     | ⚠️    | ✅      | ✅    |
| T5 Coverage tracking   | ✅    | ✅  | ✅      | ✅  | ✅      | ✅    | N/A     | ✅    |
| T6 Coverage threshold  | ✅    | ✅  | ✅      | ✅  | ✅      | ✅    | N/A     | ✅    |
| D5 API documentation   | ✅    | ✅  | N/A     | ✅  | ✅      | N/A   | ⚠️      | ⚠️    |
| D5.1 User manual       | N/A   | N/A | ✅      | ✅  | N/A     | N/A   | ✅      | ⚠️    |
| D5.2 Auto-gen docs     | ✅    | ✅  | ✅      | ✅  | ✅      | ✅    | ⚠️      | ✅    |
| E3 Docker Compose      | ✅    | ✅  | N/A     | N/A | N/A     | ⚠️    | ✅      | ✅    |
| E5 Seed data           | ✅    | ✅  | N/A     | N/A | N/A     | ✅    | ✅      | ✅    |
| O1 Structured logging  | ✅    | ✅  | ⚠️      | ⚠️  | N/A     | ⚠️    | ⚠️      | ✅    |
| O2 Error tracking      | ✅    | ✅  | ✅      | N/A | N/A     | N/A   | N/A     | ✅    |
| O4 Distributed tracing | ✅    | N/A | N/A     | N/A | N/A     | N/A   | N/A     | ✅    |
| O5 Health check        | ✅    | ✅  | N/A     | N/A | N/A     | ✅    | N/A     | ✅    |
| P1 Analytics           | ✅    | ✅  | ✅      | N/A | N/A     | N/A   | N/A     | N/A   |
| P2 Feature flags       | ✅    | ✅  | ✅      | N/A | N/A     | N/A   | N/A     | ⚠️    |
| P3 A/B testing         | ✅    | ✅  | N/A     | N/A | N/A     | N/A   | N/A     | N/A   |

> [!NOTE]
> ⚠️ in the matrix means the criterion **applies** but is commonly optional —
> still scored normally. Only **N/A** entries are excluded from the denominator.

### Step 3 — Score and Determine Level

Count pass/partial/fail per pillar. Scoring rules:

- ✅ = 1 point
- ⚠️ = 0.5 points
- ❌ = 0 points
- **N/A** = excluded (does not count toward the denominator)

**Level definitions** (based on
[Factory AI](https://docs.factory.ai/web/agent-readiness/overview)):

| Level | Name | Meaning | Decision Question for New Criteria |
| ----- | ---- | ------- | ---------------------------------- |
| L1 | **Functional** | Code works, basic tooling exists — agent can build, run, and get feedback | *Does this make the code functional and give the agent basic feedback?* |
| L2 | **Documented** | Knowledge is captured and accessible — agent understands architecture, domain rules, and conventions | *Does this document knowledge the agent needs to produce correct output?* |
| L3 | **Standardized** | Processes are enforced and reproducible — CI gates, quality thresholds, and automated checks prevent regressions | *Does this standardize a process so quality is enforced automatically?* |
| L4 | **Optimized** | Infrastructure is polished and complete — full observability, debugging, contribution workflows, and self-service | *Does this optimize the development experience for full self-service?* |
| L5 | **Autonomous** | Agent can drive product decisions — experimentation, analytics, and feature management | *Does this enable autonomous product experimentation?* |

Each level's criteria are the **actionable TODO list for repos at that level**.
When ≥ 80% of applicable criteria pass, the repo graduates to the next level.

**Level thresholds** (based on **applicable** criteria — those not marked N/A
for the project type and repository type):

| Level | Requirement |
| ----- | ----------- |
| L1 Functional | Starting point (all repos) |
| L2 Documented | ≥ 80% of L1 criteria pass (S1-S3, B1-B2, T1-T4, D1, D3.1-D3.2, E3, X1) |
| L3 Standardized | L2 + ≥ 80% of L2 criteria (D2, D3.3, D4-D5, E1-E2, O1-O2, K1-K2) |
| L4 Optimized | L3 + ≥ 80% of L3 criteria (S4-S5, S7, B3-B4, T5-T6, T9, X2-X3) |
| L5 Autonomous | L4 + ≥ 80% of L4 criteria (S6, B5, T7-T8, D5.1, D5.2, D6-D8, E4-E5, O3-O5, X4-X5, K3-K4, P1-P3) |

Exclude N/A criteria from each level's set before computing the percentage.

### Step 4 — Generate the Enhancement Plan

Use the template in `resources/evaluation_template.md` to produce the final
report. The plan must follow these rules:

1. **Phase by level**: Group enhancements by the level they unlock.
2. **Modernize, don't pile on**: If a legacy tool exists, recommend migration to
   the modern equivalent (see `resources/modernization_recommendations.md`)
   rather than adding a parallel tool. Mark legacy as "replace" not "add
   alongside".
3. **Agent context**: When no agent context exists, recommend `AGENTS.md` as
   the cross-tool default entry file (with `.agents/workflows/` or equivalent
   for repeatable commands). When the repo is Claude-centric or already uses
   `.claude/`, recommend `CLAUDE.md` (with `.claude/skills/`, `.claude/commands/`,
   `.claude/agents/`); for cross-tool reach, have it import (`@AGENTS.md`) or
   symlink a shared `AGENTS.md` rather than duplicating content. Agent files
   must **reference** `README.md` and `docs/` as the single source of truth —
   never duplicate their content.
4. **Minimal invasiveness**: Prefer config/documentation changes over code
   changes. Code changes only when a modernization migration requires it (e.g.,
   switching test framework).
5. **Explicit breaking changes**: If a modernization would break existing
   workflows (e.g., replacing isort hook with ruff), note it with a
   `> [!WARNING]` callout.
6. **Projected level + re-evaluation**: Each phase must include a **projected
   level** (estimated level if all phase tasks are completed) and a
   **re-evaluation task** instructing the agent to re-run the evaluation after
   changes and report the **actual level** reached.
7. **Pros/Cons table**: Every plan must end with a pros/cons comparison.
8. **Verification plan**: Include automated and manual verification steps.

### Step 5 — Save the Report

Save the completed evaluation to the target repository for historical tracking.

1. Create `docs/agent-readiness/` in the target repo if it does not exist.
2. Save the filled-in evaluation as a markdown file using the naming convention:

   ```text
   agent-readiness_YYYY-MM-DDThh-mm.md
   ```

   Where `YYYY-MM-DDThh-mm` is the evaluation datetime (use the local time of
   the evaluation, with colons replaced by hyphens for filesystem
   compatibility). Example: `agent-readiness_2026-03-09T08-37.md`.
3. Fill the `Date` field in the Ecosystem table with the same datetime value in
   ISO 8601 format (`YYYY-MM-DDThh:mm`).

### Step 6 — Present to User

Present the report and enhancement plan, then wait for the user's review
before implementing any phase. Include questions about:

- Team ownership for CODEOWNERS
- Environment variable sources for `.env.example`
- Preferences on migration breaking changes
- Which phases to implement

## Output Artifacts

The evaluation report with its phased enhancement plan (built from
`resources/evaluation_template.md`), presented in Step 6 and persisted at
`docs/agent-readiness/agent-readiness_YYYY-MM-DDThh-mm.md` (Step 5).
