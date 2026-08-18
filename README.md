# Custom-skills

My personal Claude Code skills. This repo is where I keep them, version them, and reason about how they fit together — it isn't a distribution.

Each skill is a directory with a `SKILL.md` entrypoint plus whatever bundled files it references. They're grouped by purpose:

```
kanban/            the workflow chain — one artifact handed to the next
developer-tools/   everything else for coding, reached for as needed
schoolwork/        study skills — for when I'm the learner
archive/           retired, never installed
```

`install.sh` walks those categories and symlinks each skill flat into `~/.claude/skills/<name>` — Claude Code discovers skills by bare name, so the category is repo-level organisation only.

---

## kanban — the workflow

The core of the repo is one chain that runs from "I have an idea" to "the diff is reviewed and pushed". Each step writes an artifact the next step reads, so nothing is re-derived from memory.

```
project-planning  →  epic-planning  →  implementation-planning  →  implementation-plan-execute  →  review-edits
   CONTEXT.md         (N.M) tasks        implementation_plans/        code + green ACs               verdict
   project_plan.md    + epic issue       N.N_name.md
```

**1. `project-planning`** — once per project. Grills me on problem, user, success criteria, scope, and domain language, then proposes vertical-slice epics. Writes `CONTEXT.md` (the project's language) and `project_plan.md` (the epic roadmap). Re-runs only ask about gaps; ✅ epics are immutable.

**2. `epic-planning`** — once per epic. Slices one epic goal into `(N.M)` task rows in `project_plan.md` and files the epic's parent GitHub issue with native sub-issue blocking. Research and prototype tickets are first-class here — unknowns get charted, not guessed at.

**3. `implementation-planning`** — once per task. Grills the whole thing: behaviour and acceptance criteria, then architecture, modules, files, tests, rollout. Writes `implementation_plans/N.N_short_name.md` — phases, Groups, acceptance criteria, and a mandatory Phase 1 that writes the failing acceptance tests before any production code.

**4. `implementation-plan-execute`** — drives the plan. Implements each Group inline in the main thread after I approve a one-paragraph architecture statement for it. No per-Group testing; the plan's final Verification phase runs the acceptance tests once as the single source of truth for "does it work", then commits. A structural surprise mid-Group halts for a real decision instead of being improvised.

**5. `review-edits`** — judges the committed diff on two axes: **Standards** (does it obey the rule-ADRs in `docs/adr/`, plus code smells) and **Spec** (does it actually meet the acceptance criteria, with no scope creep). Handles both a plan-backed run and a small change done inline.

---

## developer-tools

Coding skills that aren't stations on the board — no ordering, no artifacts passed between them. See [developer-tools/README.md](developer-tools/README.md).

| Skill | What it does |
|-------|--------------|
| `implement-tdd` | The small-change bypass around the board. Not everything deserves the full chain: runner preflight, grill the test suite, write the red tests, dispatch an implementer per attempt, review once green. |
| `codebase-rules` | Surveys the codebase and grills me into one-rule-per-file ADRs in `docs/adr/`, shaped `Rule / Why / How-to-check`. These are what `review-edits` cites. |
| `add-comments` | Establishes a persisted `comment-convention.md`, then walks the code symbol by symbol with an approve/edit/skip preview. Missing language mid-walk triggers a scoped grill. |
| `generate-framework-tests` | Real runnable tests (pytest / vitest / jest / go test / cargo test / JUnit). Sidecar manifest gives fast-exit when nothing changed and drift-diff when it did; user-added cases are never touched. |
| `new-issue` | WHAT grill → GitHub Issue, for work no epic covers. Deliberately **not** in the chain — the board goes straight from an epic task to a plan. Splits oversized scope into linked sub-issues. |
| `grilling` | The bare interview loop — one question at a time, recommended answer first, down every branch until shared understanding. The primitive most of `kanban/` is built on. |
| `brainstorming` | The front door to everything else. Grills an idea trying to **kill** it, then gives a binary verdict — dead, or a paragraph of concrete functionality — and routes the survivor to whichever skill is the smallest fit. |
| `pro-con` | Weigh a decision and commit to a recommendation. Fixed output shape. Manual invocation only. |

---

## schoolwork

Skills for when I'm the learner rather than the builder. See [schoolwork/README.md](schoolwork/README.md).

| Skill | What it does |
|-------|--------------|
| `eli5` | Persistent plain-language mode. Assumes zero knowledge and bans naked terms — no domain word used before it's glossed. Manual invocation only. |

Still planned: note-taking, rehearsal, spaced repetition, exam prep.

---

## archive

[`archive/`](archive/) holds skills I've retired — `generate-test`, `run-tests`, `directory-tree`. Never installed, not part of any workflow. See [archive/README.md](archive/README.md) for why each one is there.

---

## Repo conventions

- **A skill is the unit of install.** Everything a skill references lives inside its own directory, referenced by a relative path — see [ADR 0001](docs/adr/0001-skills-are-self-contained.md).
- **Installed by symlink**, so edits are live and the repo can live anywhere — see [ADR 0002](docs/adr/0002-install-via-symlink.md).
- **Grouped by category, installed flat** — skill names must stay unique across categories, and a new category means a new entry in the `CATEGORIES` array in `install.sh` — see [ADR 0003](docs/adr/0003-skills-grouped-by-category-directory.md).
- `CONTEXT.md` holds the domain language for this repo. Several skills read it at runtime for canonical definitions (Supervisor, Group, Verification tester, …) rather than restating them.
