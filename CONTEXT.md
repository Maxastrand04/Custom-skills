# Custom-skills

My personal Claude Code skills, symlinked into `~/.claude/skills/`. Not a distribution — this repo exists so the skills I actually use stay versioned and consistent with each other.

This file is the canonical domain language for the repo. Several skills read it at runtime rather than restating definitions in their own `SKILL.md`.

## Language

**Skill**:
A directory containing a `SKILL.md` plus any files that `SKILL.md` references. Lives one level down, inside a **Category**. The directory is the unit of install.
_Avoid_: plugin, extension, command

**Category**:
A top-level directory grouping Skills by purpose: `kanban/` (the workflow chain), `developer-tools/` (coding Skills off the chain), `schoolwork/` (study Skills, empty for now), `archive/` (retired, never installed). Repo-level metadata only — it never appears in a Skill's name or invocation. Adding one means adding it to the `CATEGORIES` array in `install.sh`.
_Avoid_: group, namespace, section, folder

**SKILL.md**:
The entrypoint of a Skill. YAML frontmatter declares `name` and `description`; the body is the prompt content Claude Code loads.
_Avoid_: manifest, config

**Bundled file**:
A file inside a Skill directory that `SKILL.md` references via a relative path (e.g., a template, a format spec). Travels with the Skill.
_Avoid_: resource, asset, dependency

**Install**:
Creating a symlink from `~/.claude/skills/<name>` to this repo's `<category>/<name>/` directory so Claude Code loads the Skill. The symlink is always **flat** — Claude Code discovers Skills by bare directory name and does not read **Categories**. A Skill that has moved between Categories is silently re-pointed on the next `install.sh` run.
_Avoid_: deploy, sync, copy

**Group**:
A plan-time bundle of tasks within a phase that constitutes one fully independent vertical slice — verifiable on its own, with no read-dependency on any sibling Group in the same phase. Implemented inline by the Supervisor, one Group at a time, per the **Group loop**. If two task bundles cannot be verified independently, they belong in the same Group (or in different phases), not two Groups in the same phase. Authored during planning, not decided at supervision time. No Group is tested on its own — cross-Group correctness is checked once, in the plan's mandatory **Verification tester** pass.
_Avoid_: batch, cluster, chunk

**Verification tester**:
An `Explore` subagent dispatched only inside the plan's mandatory final `Phase N — Verification` — one for the Architecture sweep Group, one for the Acceptance criteria Group. No Group or feature phase before Verification is tested; testing runs exactly once, at the end, per the **Verification failure rule**.
_Avoid_: verifier, checker, group tester, phase tester

**Write-acceptance-tests phase**:
The mandatory `## Phase 1 — Write acceptance tests` that `implementation-planning` puts second in every plan, right after Phase 0. Its Groups write the actual failing (red) automated tests named in each non-`(manual)` `AC-N`'s `Verify:` clause — no production code. Implementation phases (`Phase 2` onward) make those tests pass; `Phase N — Verification` re-runs them and expects green. Makes every generated plan test-driven at the phase level, not just the acceptance-criteria level.
_Avoid_: test phase, red phase, TDD phase

**Supervisor**:
Opus in the main thread, orchestrating implementer and tester subagents per the `implementation-plan-execute` skill (supervise mode). Owns plan-file bookkeeping but never writes production code.
_Avoid_: orchestrator, coordinator, driver

**Reviewer**:
An `Explore` subagent that reads the implementation diff and tests after the test-pass loop, explains in plain English what changed mapped to files, and surfaces concerns. Read-only; never edits.
_Avoid_: code reviewer, auditor, checker

**Runner preflight**:
The auto-detect-then-confirm step at the start of test-first skills that locks down which test runner command will gate the implementation loop.
_Avoid_: test setup, harness setup, runner detection

**Adaptive grill**:
The gap-filling interview in `project-planning` that runs after reading any existing `CONTEXT.md` and `project_plan.md`. Summarizes current understanding first, then asks only where gaps remain across five areas (problem statement, primary user, success criteria, scope boundaries, domain language) — one question per turn. Stops when all five areas can be stated with confidence; does not run a fixed N-question script.
_Avoid_: alignment grill, kickoff, scoping session, intake

**Sprint**:
A numbered vertical slice of a project plan, each with a one-sentence sprint goal and a status marker (⬜ / 🟡 / ✅). Sprints are proposed by `project-planning` and broken into **Task** rows by `sprint-planning`. Completed (✅) sprints are immutable across re-runs.
_Avoid_: phase, iteration, milestone

**Sprint goal**:
The one-sentence observable outcome that defines a sprint as done. Written by `project-planning` during sprint breakdown, confirmed by the user at the confirm gate, and never edited once the sprint is ✅.
_Avoid_: sprint description, deliverable, objective

**Project plan**:
The `project_plan.md` file written by `project-planning` at the consuming project's repo root. Contains a project goal, sprint list (each with status marker + sprint goal + tasks placeholder), out-of-scope section, and a directory-tree section left at its placeholder. Shared contract consumed by `sprint-planning` and `implementation-planning`.
_Avoid_: roadmap file, plan doc

**Task**:
A `(N.M)` row written by `sprint-planning` under a sprint in `project_plan.md`. Represents one thin vertical slice of the sprint goal, sized to become a single GitHub issue. The Plan column starts blank and is filled by `implementation-planning`. The Issue column is optional — only used when a **Task** happens to have been filed via the standalone `new-issue`.
_Avoid_: ticket, story, to-do, backlog item







**WHAT / HOW split**:
The division of labor between `new-issue` (grills WHAT — behavior, scope, acceptance criteria, with no architecture or file paths) and `implementation-planning` (grills HOW — architecture, modules, files, tests, rollout). The two skills hand off via a GitHub Issue.
_Avoid_: spec/design split, intake/build split

**Sub-issue**:
A child GitHub Issue published by `new-issue`'s multi-plan path when the parent's acceptance criteria span clearly separable user-visible concerns. Each sub-issue is an independently demoable vertical slice with its own acceptance criteria and explicit `Blocked by` refs. The union of sub-issue acceptance criteria must cover the parent's full acceptance criteria — the **two-tier coverage check** (per-slice + systemic).
_Avoid_: child issue, subtask, ticket



**From-issue path**:
The branch of `implementation-planning` that starts from an existing GitHub Issue (explicit `<issue-ref>` arg or strict-and-confirm auto-detect when `new-issue` just ran in-session). Skips WHAT topics — they're already in the issue body — and runs only HOW topics. Contrasts with the **standalone path**, which runs the full WHAT+HOW grill from scratch.
_Avoid_: issue mode, linked mode, resumption

**Framework test**:
A real, framework-executable test file (pytest / vitest / jest / `go test` / `cargo test` / JUnit Jupiter) produced by `generate-framework-tests`. Contains no YAML frontmatter or skill markers — it is plain framework code and can be run directly by the project's test runner.
_Avoid_: test spec, generated test, scaffold test

**Sidecar manifest**:
The JSON file at `.generate-framework-tests/sidecar-manifest.json` written by `generate-framework-tests` after each successful test-file write. Records `source_sha`, `generated_at`, and the `cases[]` list for each source file the skill has ever written tests for. Used for fast-exit and drift-diff on re-invocation. Never hand-edited.
_Avoid_: test manifest, lockfile, index

**Fast-exit**:
The short-circuit check at the start of each `generate-framework-tests` invocation. If all in-scope source files have sidecar-manifest entries whose recorded SHA-256 matches current content, and no new untested source files exist, the skill prints "all tests are up to date — nothing to do" and exits with no plan and no writes.
_Avoid_: cache hit, skip check, staleness check

**Drift-diff**:
The per-source-file algorithm in `generate-framework-tests` that runs when a source file's SHA-256 has changed since the last sidecar-manifest write. Re-derives the proposed case list from the current source, diffs it against the manifest's `cases[]`, and buckets the delta into `+add` / `-remove` / `~update` annotations shown in the approval plan.
_Avoid_: delta detection, change detection, re-gen

**User-added-case immunity**:
The hard invariant in `generate-framework-tests`: any test case present in a framework test file but absent from the sidecar manifest's `cases[]` for that source is treated as user-authored and is never proposed for change, removal, or update — regardless of what drift-diff detects in the source.
_Avoid_: user case protection, manual case preservation

**Group loop**:
`implementation-plan-execute`'s single execution mode: the main thread implements each Group inline — no `claude` implementer subagent — after the user has approved an architecture statement per Group. Architecture review is the user's role throughout; no functionality or architecture testing runs per Group or per phase — that happens once, in the mandatory Verification phase. A structural choice discovered mid-implementation (not covered by the approved statement) halts immediately for a fresh user decision, rather than being improvised. Uses the **Exploration summary file** directly (read by the Supervisor itself, not an implementer) to avoid whole-file reads before stating architecture — see **Point, don't paste**.
_Avoid_: hands-on mode, inline mode, supervise mode, parallel mode

**Point, don't paste**:
The `implementation-plan-execute` dispatch rule: every **Verification tester** brief carries the plan file's path and a scope label, never a pasted copy of plan sections. The subagent reads its own scope from the plan file directly. Exists because pasted blocks repeat verbatim across every retry, and that repetition accumulates in the **Supervisor**'s own context rather than the subagent's — the main driver of context growth over a multi-phase run. Paired with **Terse verdicts**.
_Avoid_: pointer pattern, lazy loading

**Terse verdicts**:
The `implementation-plan-execute` rule that after a Group finishes or a Verification result returns, the **Supervisor** states only a one-line verdict and moves on — never re-pasting a report or restating a prior phase. The plan file's checkboxes are the sole source of truth for cross-phase state. Paired with **Point, don't paste**.
_Avoid_: status update, progress note

**Verification failure rule**:
The single failure-handling mechanism in `implementation-plan-execute`. No Group or feature phase is retried on its own — only the mandatory `Phase N — Verification` can fail, and it escalates to the user on the **first** failure, every time: no automatic retry, no attempt cap. The Supervisor names (or asks the user to name) the responsible Group and states what it thinks happened, but the user decides the next action (re-dispatch, fix manually, amend an AC/AD, or stop). Whatever they choose runs once, then the full Verification phase reruns fresh; a repeat failure escalates again the same way.
_Avoid_: retry budget, group-level retry, phase-level retry, attempt cap

**Bootstrap exploration sweep**:
The `implementation-plan-execute` step that runs once before Phase 0 (and is refreshed per feature phase thereafter), dispatching one `Explore` (haiku) subagent to summarize the current shape of the files the plan touches. Writes to the **Exploration summary file** — the discovery legwork happens in a subagent's disposable context, not the Supervisor's.
_Avoid_: pre-scan, discovery pass, warmup sweep

**Exploration summary file**:
The scratch file (e.g. `implementation_plans/.exploration-summary_N.N.md`) that `implementation-plan-execute`'s bootstrap exploration sweep writes to before Phase 0, refreshed per phase by overwriting the changed entries. The Supervisor reads its own scoped slice before stating architecture for each Group. Its contents are never held in the Supervisor's own context beyond that scoped read, nor pasted into a response. Deleted during Finalization — it is scratch, not a plan artifact.
_Avoid_: in-memory summary, exploration cache

**Comment convention**:
A `comment-convention.md` file at a user-chosen location in a project that stores per-language comment rules. Structured as `# Comment Convention` H1, optional `## Global rules`, then one `## <Language>` H2 per language. Produced by `add-comments`'s grill and consumed by its preview-walk.
_Avoid_: comment config, style guide, lint config

**ensure-convention**:
The `add-comments` sub-flow that locates the nearest-ancestor `comment-convention.md` from the target path. If found, loads it. If not found, runs the full multi-language grill (referencing `grill-topics.md`) and writes a new file. No source files are read or written during the grill.
_Avoid_: convention lookup, convention setup

**preview-walk**:
The `add-comments` sub-flow that iterates source files in scope, shows a per-symbol fenced-code preview of proposed comment changes, and collects user responses (approve / edit / skip / accept-file). Approved changes are held in memory and flushed per-file on completion.
_Avoid_: comment loop, review loop, preview loop

**Scoped single-language grill**:
A focused `add-comments` grill that runs only the topics for one missing language when the current `comment-convention.md` lacks a section for the target file's language. Appends a new `## <Language>` H2 to the existing convention file, then resumes the walk. Contrasts with the full multi-language grill in `ensure-convention`.
_Avoid_: mini-grill, partial grill, language grill


**pro-con**:
The standalone decision skill. Weighs an option set and commits to a single recommendation, filling `template_output.md` exactly so every run has the same shape. Manual-invocation only (`disable-model-invocation: true`) — it never fires on its own mid-task.
_Avoid_: tradeoff skill, decision matrix, options analysis

## Relationships

- A **Skill** contains exactly one **SKILL.md** and zero or more **Bundled files**
- Every **Skill** lives in exactly one **Category**; `install.sh` walks the live Categories (`archive/` excluded) and installs what it finds
- Because **Install** is flat, **Skill** names must be unique across **Categories** — two Skills with the same name in different Categories would collide on one symlink
- **Install** maps a **Skill** in this repo to a symlink under `~/.claude/skills/`
- A **Bundled file** is only referenced by `SKILL.md` via a path relative to the **Skill** directory — never by an absolute path outside the **Skill**
- `implementation-plan-execute` is a single-mode driver Skill: the **Group loop** implements each Group inline, in the main thread, gated on the user's real-time architecture approval. It uses the **Bootstrap exploration sweep**'s **Exploration summary file**. Every dispatch follows **Point, don't paste** and every Supervisor judgment follows **Terse verdicts**. The `## Verification phase loop` and `## Finalization step` sections of SKILL.md are the only place a **Verification tester** runs, per the **Verification failure rule**. On a from-issue plan's Verification pass, Finalization closes the GitHub issue (`gh issue close`) and marks the matching `(N.M)` **Task** ✅ in the **Project plan** (`project_plan.md`); both steps are best-effort and gated on the issue reference being present.
- A **Supervisor** implements each **Group** inline and flips it ✅ directly on completion — no per-Group or per-Phase tester runs. The plan's mandatory final Verification phase is the only place a **Verification tester** runs, per the **Verification failure rule**.
- A **Supervisor** running `implement-tdd` performs a **Runner preflight**, dispatches one `claude` implementer per attempt against a **Reviewer**-confirmed test suite, then dispatches one **Reviewer** once tests pass.
- `project-planning` runs a **Git-repo guard** first (hard-stops outside a git repo), then the **Adaptive grill** (reads existing `CONTEXT.md` + **Project plan**, asks only on gaps), then a sprint-breakdown confirm gate, then writes `CONTEXT.md` + **Project plan**; all steps are Opus-direct — no Group / Verification tester dispatch. The plan's Directory tree section is left at its placeholder — the `directory-tree` skill that used to fill it is archived.
- `sprint-planning` sits between `project-planning` and `implementation-planning` in the chain: it reads the **Project plan**, slices a chosen **Sprint**'s goal into **Task** rows `(N.M)` appended to the plan, and creates or updates the sprint's parent `(N)` GitHub issue. It does not call `new-issue` — a charted **Task** goes straight to `implementation-planning`.
- `new-issue` is **off the chain** — a standalone Skill for filing an issue that no **Sprint** covers. It grills WHAT (behavior, scope, acceptance criteria, no architecture or file paths) and publishes a GitHub Issue; its multi-plan path publishes a parent Issue plus one **Sub-issue** per vertical slice, in dependency order, gated on the **two-tier coverage check**. An issue it produces can still be picked up by `implementation-planning`'s **From-issue path**, which is what the **WHAT / HOW split** exists for — but the normal route into a plan is a **Task** row, not an Issue.
- `add-comments` runs **ensure-convention** first (locates or grills for a **Comment convention**), then **preview-walk** (per-symbol approve loop). A missing language mid-walk triggers a **Scoped single-language grill** rather than the full grill.
- `generate-framework-tests` is the repo's only live testing Skill — it produces **Framework tests** (real runnable code) that the project's own runner executes. It uses a **Sidecar manifest** to enable **Fast-exit** on re-invocation and **Drift-diff** on changed sources. **User-added-case immunity** is enforced via the manifest's `cases[]` list. The markdown-spec approach it replaced (`generate-test` / `run-tests`) is archived.

## Example dialogue

> **Me:** "Where should the implementation-plan template live?"
> **Claude:** "Inside the `implementation-planning` Skill, next to its `SKILL.md`. It's a Bundled file — Skills are self-contained, so the template travels with the Skill rather than living in a shared `~/.claude/templates/` directory."
