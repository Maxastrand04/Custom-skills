# Project Setup — Artifact Checklist

**Purpose.** This checklist enumerates every artifact category a fresh project might need (metadata, runtime, build, quality gates, docs, CI, etc.), the decisions to elicit per category, the recommended default for each decision, and the concrete filesystem action the skill takes the moment the user answers. It is the single source of truth the `project-setup` skill walks the user through after `CONTEXT.md` has been written.

**Usage.** `SKILL.md` walks these in order; skip categories that don't apply based on `CONTEXT.md` (e.g. skip `## Database` for a pure CLI tool, skip `## Observability` for a one-shot script).

**Interaction protocol.** One question per turn. Every question includes (1) a recommendation and (2) one-sentence reasoning grounded in `CONTEXT.md` or the chosen language defaults. `skip` is allowed per item — the skill notes the skip and moves on. Decisions are persisted as they are made; the user can re-run the skill to fill in skipped items later.

The only external files this checklist references are bundled siblings: `SKILL.md` (the skill driver) and `template_project_plan.md` (the planning template copied alongside this file).

**Manifest files are built incrementally.** A language manifest (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`) accumulates decisions across many categories below — Package management seeds it, then Build & artifacts, Code quality, Testing, and others each append their own tables or entries to the **same file**. The skill must amend or append the affected section in place; it must **never** overwrite a manifest or discard decisions persisted by earlier categories.

---

## Project metadata

Decisions to elicit:
- **Project name** — default: basename of the current working directory.
- **One-line description** — default: extracted from the problem statement in `CONTEXT.md`.
- **Author** — default: `git config user.name` (fall back to `git config --global user.name`).
- **License** — default: `MIT`.

Filesystem actions on answer:
- Write/update the project-name field in the language-native manifest if one exists (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`).
- Create `LICENSE` at repo root from the standard SPDX text for the chosen license.
- Stash author + description for downstream sections (README, manifest).

---

## Language & runtime

Decisions to elicit:
- **Primary language and version** — default: inferred from `CONTEXT.md` ("project shape" + existing files); else ask.
- **Version-pinning file** — default per language: `.python-version` (Python), `.nvmrc` (Node), `rust-toolchain.toml` (Rust), `.tool-versions` (mise/asdf polyglot).
- **Additional languages** — detect any secondary language signaled in `CONTEXT.md` (e.g. TypeScript frontend + Python backend) and queue a follow-up runtime question per language.

Filesystem actions on answer:
- Create the version-pin file with the exact version string.
- If polyglot, create `.tool-versions` listing every language+version.

---

## Package management

Decisions to elicit:
- **Package manager** — defaults: `uv` (Python), `pnpm` (Node), `cargo` (Rust), `go mod` (Go).
- **Lockfile-commit policy** — default: commit lockfiles (`uv.lock`, `pnpm-lock.yaml`, `Cargo.lock` for apps, `go.sum`).
- **Workspaces / monorepo tooling** — default: single-package unless `CONTEXT.md` indicates multiple deployables; then `pnpm` workspaces or `uv` workspaces or `cargo` workspaces as appropriate.

Filesystem actions on answer:
- Run the manager's init command to create the manifest (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`) if missing.
- Ensure lockfile is NOT in `.gitignore` (or remove it if it is, per policy).
- For workspaces: write the workspace root config (`pnpm-workspace.yaml`, `[workspace]` in `Cargo.toml`, `tool.uv.workspace`).
- The manifest file is built **incrementally** across categories: this category seeds it; later categories (Build & artifacts, Code quality, Testing, etc.) append their tool entries to the same file rather than starting fresh.

---

## Directory layout

Decisions to elicit:
- **`src/` vs flat** — default: `src/` layout for libraries and applications; flat for one-file scripts.
- **Test location** — default: top-level `tests/` for Python and Rust; sibling `*.test.ts` for TS/JS; sibling `*_test.go` for Go.
- **Monorepo vs single package** — default: single package unless `CONTEXT.md` says otherwise.

Filesystem actions on answer:
- Create `src/<package_name>/__init__.py` (or equivalent entry directory per language).
- Create `tests/` (or wire sibling-test conventions into the chosen test runner config).
- For monorepo: scaffold `packages/` (or `apps/` + `libs/`) with placeholder packages reflecting `CONTEXT.md` parts.

---

## Build & artifacts

Decisions to elicit:
- **Build tool** — defaults: `setuptools`/`hatchling` via `pyproject.toml` (Python), `vite` (TS app), `tsc` (TS lib), `cargo build` (Rust), `go build` (Go).
- **Output directory** — defaults: `dist/` (JS/TS, Python wheels), `target/` (Rust), `build/` (Go binaries).
- **Compile target** — defaults: native for Rust/Go; `es2022` + browser/node for TS; pure-Python wheel for Python.

Filesystem actions on answer:
- Write the build configuration into the language manifest or a dedicated config file (`vite.config.ts`, `tsconfig.json`, `[build]` table in `Cargo.toml`).
- Add the output directory to `.gitignore` (see `## VCS / GitHub`).

---

## Code quality

Decisions to elicit:
- **Linter** — defaults: `ruff` (Python), `eslint` (TS/JS), `clippy` (Rust), `golangci-lint` (Go).
- **Formatter** — defaults: `ruff format` (Python), `prettier` (TS/JS), `rustfmt` (Rust), `gofmt`/`goimports` (Go).
- **Type checker** — defaults: `mypy` or `pyright` (Python), `tsc --noEmit` (TS), built-in (Rust/Go).
- **Pre-commit hooks** — default: `pre-commit` framework running lint + format + type-check on staged files.
- **EditorConfig** — default: yes (`.editorconfig` with project's indent + line-ending conventions).

Filesystem actions on answer:
- Append `[tool.ruff]` / `[tool.mypy]` sections to `pyproject.toml`, or write `eslint.config.js` / `.prettierrc` / `tsconfig.json`.
- Write `.pre-commit-config.yaml` and run `pre-commit install`.
- Write `.editorconfig`.

---

## Testing

Decisions to elicit:
- **Framework** — defaults: `pytest` (Python), `vitest` (Vite-based TS), `jest` (other TS), `cargo test` (Rust), `go test` (Go).
- **Coverage tool + threshold** — defaults: `coverage.py` (Python) / `c8` (Node) / built-in (Rust, Go); threshold 80% lines.
- **TDD posture** — default: agent-only TDD (the `tdd`/`implement-tdd` skills are used by Claude; human-authored code is test-after). Other options: strict TDD for everyone, test-after for everyone.
- **Test types** — default: unit + integration; add e2e only if `CONTEXT.md` lists a UI or HTTP surface.
- **Fixtures location** — default: `tests/fixtures/` (Python/Rust), `tests/__fixtures__/` (TS).

Filesystem actions on answer:
- Add the framework + coverage tool to the project's dev dependencies.
- Write a `tests/test_smoke.py` (or equivalent) that asserts the package imports successfully.
- Write coverage config (`pyproject.toml` `[tool.coverage.*]`, `vitest.config.ts`, etc.) with the agreed threshold.
- Create `tests/fixtures/.gitkeep`.

---

## Architecture / design

Decisions to elicit:
- **Architectural style** — options: MVC, hexagonal/ports-and-adapters, layered, vertical slice, none (scripts). Default: vertical slice for apps, none for scripts/libraries.
- **DDD opt-in** — default: no, unless `CONTEXT.md` describes a rich domain.
- **GoF patterns** — favor: strategy, adapter, facade. Avoid by default: singleton, abstract factory (unless domain-warranted).
- **FP vs OO bias** — default: FP-leaning for data pipelines, OO for stateful long-lived services.
- **Async pattern** — defaults: `asyncio` (Python services), promises/`async`-`await` (TS), `tokio` (Rust), goroutines (Go).
- **Error handling** — defaults: exceptions (Python, TS), `Result<T, E>` (Rust), explicit error returns (Go). Override with result-type libs (`returns` for Python) only if `CONTEXT.md` justifies it.
- **Logging library** — defaults: `structlog` (Python), `pino` (Node), `tracing` (Rust), `slog` (Go).

Filesystem actions on answer:
- Write a one-page `docs/architecture.md` capturing the style, async pattern, and error-handling stance.
- Drop an ADR (`docs/adr/0001-architecture-style.md`) recording the chosen style.
- Add the logging library to dependencies and create `src/<package>/logging.py` (or equivalent) with a configured logger factory.

---

## Documentation

Decisions to elicit:
- **README skeleton** — default: yes. Populated with real content from `CONTEXT.md` (problem, goal, audience) plus install/run/test commands derived from prior decisions.
- **CHANGELOG** — default: yes, keep-a-changelog format.
- **LICENSE text** — already written in `## Project metadata`; this confirms the file exists.
- **CONTRIBUTING.md** — default: yes for OSS, skip for private/solo.
- **Code of Conduct** — default: yes for OSS (`CODE_OF_CONDUCT.md`, Contributor Covenant).
- **ADRs** — default: yes. Create `docs/adr/` with `0000-record-architecture-decisions.md` (Nygard template) explaining the ADR process; subsequent ADRs follow Nygard format.
- **Docstring style** — defaults: Google-style (Python), TSDoc (TS), rustdoc (Rust), godoc (Go).
- **API doc generator** — defaults: `mkdocs` + `mkdocstrings` (Python), `typedoc` (TS), `cargo doc` (Rust), `pkgsite` (Go). Skip entirely for apps with no public API.

Filesystem actions on answer:
- Write `README.md` with real sections (no `[TODO]` placeholders — pull every value from `CONTEXT.md` and prior answers).
- Write `CHANGELOG.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` as opted in.
- Create `docs/adr/` and write the Nygard template + the seeding ADR.
- Configure docstring linting in the chosen linter.
- Write the API-doc generator's config file when opted in.

---

## VCS / GitHub

Decisions to elicit:
- **`.gitignore`** — default: fetch the canonical file for the chosen language from the `github/gitignore` repo and append IDE entries (`.idea/`, `.vscode/`, `.DS_Store`).
- **Branching model** — defaults: trunk-based with short-lived feature branches; `main` is the trunk.
- **Commit-message convention** — default: Conventional Commits.
- **Branch protection rules** — defaults: require PR, require status checks, require linear history, disallow force-push.
- **PR template** — default: yes (`.github/pull_request_template.md`).
- **Issue templates** — default: yes (`.github/ISSUE_TEMPLATE/bug.md`, `feature.md`, `chore.md`).
- **Label set** — default: `bug`, `enhancement`, `chore`, `tracer-bullet`, `blocked`.
- **GitHub Project board** — default: yes if `CONTEXT.md` implies multi-week scope; otherwise Issues-only.
- **CODEOWNERS** — default: yes for team repos (single author = repo owner); skip for solo.

Filesystem actions on answer:
- Write `.gitignore` from the GitHub source + IDE appendix.
- Write `.github/pull_request_template.md` and `.github/ISSUE_TEMPLATE/*.md`.
- Apply labels via `gh label create` for each label in the set.
- If branch protection opted in: emit a `gh api` snippet to apply rules (or apply directly if `gh auth status` is OK).
- Write `CODEOWNERS` (`.github/CODEOWNERS`) listing the author as owner of `*`.
- If Conventional Commits opted in: add `commitlint` (Node) or `commitizen` (Python) hook to `.pre-commit-config.yaml`.

---

## CI/CD

Decisions to elicit:
- **Provider** — default: GitHub Actions.
- **Gates** — defaults: test, lint, type-check, build, security scan (all required on PR).
- **Release automation** — defaults: `semantic-release` (Node), `changesets` (Node monorepo), manual `git tag` + GitHub Release (Python/Rust/Go) unless the project publishes to a registry, in which case wire `release-please` or `cargo-release`.
- **Deploy target** — default: none unless `CONTEXT.md` names one (see `## Containerization / deploy`).

Filesystem actions on answer:
- Write `.github/workflows/ci.yml` with the chosen gates.
- Write `.github/workflows/release.yml` if release automation opted in.
- Write `.github/workflows/deploy.yml` only if a deploy target is set.

---

## Security

Decisions to elicit:
- **Dependency scanning** — default: Dependabot for GitHub-hosted projects (`.github/dependabot.yml`), with `renovate` as the alternative for teams that prefer batching.
- **Secret scanning** — default: enable GitHub-native secret scanning and add `gitleaks` to pre-commit + CI.
- **`SECURITY.md`** — default: yes (single-line contact + responsible disclosure policy).

Filesystem actions on answer:
- Write `.github/dependabot.yml` (or `renovate.json`).
- Add `gitleaks` to `.pre-commit-config.yaml` and to `.github/workflows/ci.yml`.
- Write `SECURITY.md` with the user's contact email (default: `git config user.email`).

---

## Containerization / deploy

Decisions to elicit:
- **Dockerfile** — default: yes if the project is a long-running service; no for libraries and CLIs.
- **`docker-compose.yml`** — default: yes if a database or multiple services are present.
- **Deploy target** — options: Vercel, Fly.io, Railway, AWS, GCP, Kubernetes, none. Default: none.

Filesystem actions on answer:
- Write a multi-stage `Dockerfile` tuned to the chosen language.
- Write `docker-compose.yml` referencing the DB chosen in `## Database` and any other declared services.
- Write `.dockerignore`.
- Write the deploy-target config file (`vercel.json`, `fly.toml`, `railway.toml`, `k8s/` manifests) as applicable.

---

## Configuration

Decisions to elicit:
- **Env-var strategy** — default: `.env.example` checked in + `.env` ignored + `direnv` (`.envrc`) for local-shell loading.
- **Config file format** — defaults: `toml` (Python, Rust), `json` (Node), `yaml` (services with hand-edited config).
- **Secrets management** — defaults: local `.env`, CI uses provider's secret store (e.g. GitHub Actions secrets), production uses the deploy target's secret store (Vercel env, Fly secrets, AWS Secrets Manager).

Filesystem actions on answer:
- Write `.env.example` enumerating every required variable inferred from prior decisions (DB URL if DB chosen, API keys if APIs declared in `CONTEXT.md`).
- Add `.env` to `.gitignore`.
- Write `.envrc` if `direnv` opted in.
- Write the config-file scaffold (`config/default.toml`, `config/default.yaml`, etc.).

---

## Observability

(Ask only if `CONTEXT.md` describes an app or service — skip for libraries, CLIs, and scripts.)

Decisions to elicit:
- **Logging** — already chosen in `## Architecture / design`; this confirms the destination (stdout JSON for cloud, pretty console for local).
- **Metrics** — defaults: Prometheus client lib for services, none for one-shot jobs.
- **Tracing** — default: OpenTelemetry SDK if multiple services, none otherwise.

Filesystem actions on answer:
- Add metrics and tracing libraries to dependencies.
- Write `src/<package>/observability.py` (or equivalent) wiring the logger, meter, and tracer.
- If OpenTelemetry opted in: write `otel-collector-config.yaml` next to `docker-compose.yml`.

---

## Database

(Ask only if `CONTEXT.md` indicates persistence — skip for stateless tools.)

Decisions to elicit:
- **Choice** — defaults: SQLite for local-first apps and prototypes; PostgreSQL for hosted services; none if no persistence.
- **ORM / query builder** — defaults: SQLAlchemy + Alembic (Python), Prisma or Drizzle (TS), SQLx + sqlx-cli (Rust), `database/sql` + `sqlc` (Go).
- **Migration tool** — default: whatever pairs with the ORM (Alembic, Prisma Migrate, Drizzle Kit, sqlx-cli, goose).

Filesystem actions on answer:
- Add the DB driver, ORM, and migration tool to dependencies.
- Create `migrations/` (or the ORM-specific dir) with a `0001_init.sql` placeholder.
- Append `DATABASE_URL` to `.env.example`.
- If PostgreSQL + docker-compose was chosen, add a `postgres` service block to `docker-compose.yml`.

---

## Claude-specific

Decisions to elicit:
- **`CLAUDE.md`** — default: yes. Write a real stub (not a placeholder) that:
  - links to `CONTEXT.md` as the source of project shape and language,
  - lists the methodology decisions taken in earlier categories (architectural style, TDD posture, commit convention, branching model),
  - encodes the convention **"1 implementation plan = 1 GitHub issue, close the issue when validation passes"**,
  - points at `implementation_plans/` and the bundled `project-setup/template_project_plan.md` for planning workflows.
- **`.claude/settings.json`** — default: yes. Seed with permissions for the project's package manager, test runner, and `gh`; add a stop-hook only if the user asks.
- **Skills to symlink in** — defaults: `tdd`, `implement-tdd`, `plan-build`, `plan-execute`, `code-review`. User can add/remove.
- **`claude_ignore/` opt-in** — opt-in, **default yes** per the user's global preference. When yes, create `claude_ignore/` at the repo root and add a `.gitkeep` so it tracks; the directory is treated as off-limits for Claude reads/writes by convention.

Filesystem actions on answer:
- Write `CLAUDE.md` at the repo root with the content described above.
- Write `.claude/settings.json` with the seed permissions.
- Symlink each chosen skill from the user's skills directory into `.claude/skills/`.
- If `claude_ignore/` opted in (default yes): `mkdir -p claude_ignore && touch claude_ignore/.gitkeep`.

---

## Planning artifacts

Decisions to elicit:
- **`implementation_plans/` directory** — default: yes. Created at repo root.
- **Planning template** — always drop a copy of the bundled `project-setup/template_project_plan.md` next to the planning workflow (referenced via skill-relative path; do not fetch from elsewhere).
- **Project-tracking choice** — exactly four options:
  1. **GitHub Issues + Project board only** — every plan is also an issue; the Project board is the single source of progress truth.
  2. **`project_plan.md` only** — a single Markdown file at the repo root tracks phases and steps; reads the skill-bundled `project-setup/template_project_plan.md` via skill-relative path and copies it to `project_plan.md`.
  3. **Both** — `project_plan.md` for the human-readable phase/step map at the repo root, and GitHub Issues + Project board for granular execution tracking.
  4. **Neither** — no formal tracker; suitable for one-off scripts and throwaways.

Per-project-shape recommendation logic (indexed off `CONTEXT.md` "project shape" field):
- **Throwaway / prototype** — recommend option 4 (neither). Reasoning: lifecycle too short to justify ceremony.
- **Solo CLI / library** — recommend option 2 (`project_plan.md` only). Reasoning: one author, no collaboration overhead, but multi-phase enough to want a map.
- **Solo app / service** — recommend option 3 (both). Reasoning: phases need a map AND individual work items want issues for AFK agent dispatch.
- **Team project (any shape)** — recommend option 1 (GitHub Issues + Project board only). Reasoning: shared queue and shared visibility outweigh having a per-repo Markdown file.
- **OSS library / public project** — recommend option 1 (GitHub Issues + Project board only). Reasoning: external contributors expect issues; a Markdown plan would duplicate state.

Filesystem actions on answer:
- `mkdir -p implementation_plans/` and write a `README.md` inside it explaining the `N.N_short_name.md` naming convention.
- For options 2 and 3: copy `project-setup/template_project_plan.md` to `<repo-root>/project_plan.md` (skill-relative source, not an external fetch).
- For options 1 and 3: create the GitHub Project board via `gh project create` and seed the label set chosen in `## VCS / GitHub`.
- For option 4: no further action.
