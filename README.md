# Custom-skills

My personal Claude Code skills. This repo is where I keep them, version them, and reason about how they fit together. It isn't a distribution.

Each skill is a directory with a `SKILL.md` entrypoint plus whatever bundled files it references. They're grouped by purpose:

```
kanban/            the workflow chain, one artifact handed to the next
developer-tools/   everything else for coding, reached for as needed
behaviour/         how Claude talks, not what it builds, borrowed by the rest
schoolwork/        study skills, for when I'm the learner
archive/           retired, never installed
```

`install.sh` walks those categories and symlinks each skill flat into `~/.claude/skills/<name>`. Claude Code discovers skills by bare name, so the category is repo-level organisation only.

---

## kanban, the workflow

The core of the repo is one chain that runs from "I have an idea" to "the diff is reviewed and pushed". Each step writes an artifact the next step reads, so nothing is re-derived from memory.

```
project-planning  →  epic-planning  →  implementation-planning  →  implementation-plan-execute  →  review-diff
   CONTEXT.md         (N.M) tasks        implementation_plans/        code + green ACs           cleaned + committed
   project_plan.md    + epic issue       N.N_name.md
```

**1. `project-planning`**, once per project. Grills me on problem, user, success criteria, scope, and domain language, then proposes vertical-slice epics. Writes `CONTEXT.md`, the project's language, and `project_plan.md`, the epic roadmap. Re-runs only ask about gaps, and ✅ epics are immutable.

**2. `epic-planning`**, once per epic. Slices one epic goal into `(N.M)` task rows in `project_plan.md` and files the epic's parent GitHub issue with native sub-issue blocking. Research and prototype tickets are first-class here, so unknowns get charted rather than guessed at.

**3. `implementation-planning`**, once per task. Grills hardest on the **public interface**: the names, parameters, return values, and contracts the implementer is held to. Also sweeps for **prerequisites**: what the change calls into but doesn't build, so a missing module surfaces at planning time rather than halfway through. Writes `implementation_plans/N.N_short_name.md`, carrying acceptance criteria, that interface as copyable stubs, a Phase 0 prerequisite inventory, and a mandatory `Phase 1: Red` that writes the failing acceptance tests before any production code.

**4. `implementation-plan-execute`**, drives the plan. Confirms every Phase 0 prerequisite exists before writing anything, then implements each phase inline in the main thread against that public interface, with full freedom on the code behind it. Nothing is tested as a phase completes: the plan's final Verification phase runs the acceptance tests once as the single source of truth for "does it work", then commits. A contract that proves wrong mid-run halts for a real decision instead of being changed silently.

**5. `review-diff`**, cleans up the committed diff. First gates it **true-to-spec**, asking whether the acceptance tests genuinely test the acceptance criteria and whether the code meets them. A finding halts the session rather than papering over it. Then it edits the code into line with the rule-ADRs in `docs/adr/` and the code-smell baseline, re-runs the ACs, commits the cleanup separately, and reports each change as *what it found* then *how it fixed it*. Handles both a plan-backed run and an issue-only branch.

---

## developer-tools

Coding skills that aren't stations on the board. No ordering, and no artifacts passed between them. See [developer-tools/README.md](developer-tools/README.md).

| Skill | What it does |
|-------|--------------|
| `implement-tdd` | The small-change bypass around the board, for work that doesn't deserve the full chain. Runner preflight, grill the test suite, write the red tests, dispatch an implementer per attempt, review once green. |
| `codebase-rules` | Surveys the codebase and grills me into one-rule-per-file ADRs in `docs/adr/`, shaped `Rule / Why / How-to-check`. These are what `review-diff` cites. |
| `add-comments` | Establishes a persisted `comment-convention.md`, then walks the code symbol by symbol with an approve/edit/skip preview. Missing language mid-walk triggers a scoped grill. |
| `generate-framework-tests` | Real runnable tests for pytest, vitest, jest, go test, cargo test, or JUnit. A sidecar manifest gives fast-exit when nothing changed and drift-diff when it did. User-added cases are never touched. |
| `new-issue` | A WHAT grill that publishes a GitHub Issue, for work no epic covers. Deliberately **not** in the chain, since the board goes straight from an epic task to a plan. Splits oversized scope into linked sub-issues. |
| `brainstorming` | The front door to everything else. Grills an idea trying to **kill** it, then gives a binary verdict, either dead or a paragraph of concrete functionality, and routes the survivor to whichever skill is the smallest fit. |
| `pro-con` | Weigh a decision and commit to a recommendation. Fixed output shape. Manual invocation only. |

---

## behaviour

Skills that change how Claude talks rather than what it builds. No ordering, no artifacts. Each is a wording or interaction rule any other skill can borrow, which is why they sit at the root. See [behaviour/README.md](behaviour/README.md).

| Skill | What it does |
|-------|--------------|
| `grilling` | The bare interview loop: one question at a time, recommended answer first, down every branch until shared understanding. Most of `kanban/` is built on it. |
| `unslop` | Cuts AI tells from any writing: puffery, em dashes, inline-header lists, filler, passive voice. Always applies. |
| `talk-to-middleschooler` | Wording rules for a reader who knows nothing about the subject. No naked terms, no equations. |
| `talk-to-highschooler` | Wording rules for a reader with algebra and basic programming. Naked terms allowed once glossed. |

---

## schoolwork

Skills for when I'm the learner rather than the builder. See [schoolwork/README.md](schoolwork/README.md).

| Skill | What it does |
|-------|--------------|
| `eli5` | Turns on middle-school mode for the session, assuming zero knowledge of the subject. Manual invocation only. |
| `eli10` | Turns on high-school mode for the session, with algebra and basic programming assumed. Manual invocation only. |
| `lecture-notes` | Slide PDF in, markdown revision file out. Pulls a YouTube lecture transcript when there is one, fills the rest, and tags every line by source so `grep '\[fill\]'` lists everything a model invented. |
| `course-index` | Reads a course's `Exams/` and `Exercises/` once into `course-index.md`. Incremental via a SHA manifest. Produces the topic frequency table that `lecture-notes` flags high-yield material from. |

The `eli*` pair own only persistence. The rules live in [`behaviour/`](behaviour/README.md), one source of truth per level, reachable from any other skill the way `grilling` is.

`lecture-notes` and `course-index` hand off through `course-index.md` the way the board hands off through `project_plan.md`. Both stay inside one course folder.

Still planned: rehearsal, spaced repetition, exam prep.

---

## archive

[`archive/`](archive/) holds skills I've retired: `generate-test`, `run-tests`, and `directory-tree`. Never installed, not part of any workflow. See [archive/README.md](archive/README.md) for why each one is there.

---

## Repo conventions

- **A skill is the unit of install.** Everything a skill references lives inside its own directory, referenced by a relative path. See [ADR 0001](docs/adr/0001-skills-are-self-contained.md).
- **Installed by symlink**, so edits are live and the repo can live anywhere. See [ADR 0002](docs/adr/0002-install-via-symlink.md).
- **Grouped by category, installed flat.** Skill names must stay unique across categories, and a new category means a new entry in the `CATEGORIES` array in `install.sh`. See [ADR 0003](docs/adr/0003-skills-grouped-by-category-directory.md).
- `CONTEXT.md` holds the domain language for this repo. Several skills read it at runtime for canonical definitions, such as Supervisor, Red phase, and the Verification failure rule, rather than restating them.
