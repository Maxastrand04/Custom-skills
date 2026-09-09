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

**Invocation follows that grouping exactly.** `behaviour/` is model-invoked. Everything else sets `disable-model-invocation: true` and only starts when I type its name.

The split is about what a skill does, not what it covers. A `behaviour/` skill is borrowed by work already running, so it has to be reachable by name. Every other skill starts work, and deciding what work happens next is my job. So they carry no model-facing description, cost nothing per turn, and no skill in this repo ever invokes another outside `behaviour/`. The chain hands off through artifacts, and `brainstorming` ends by naming a route instead of taking it.

---

## kanban, the workflow

The core of the repo is one chain that runs from "I have an idea" to "the diff is reviewed and pushed". Each step writes an artifact the next step reads, so nothing is re-derived from memory.

```
map-epic  →  architect-ticket  →  implement-ticket  →  refactor-ticket
(N.M) tasks     stubs + failing      bodies filled,     shape fixed against
under the epic  tests, committed     suite green        docs/adr/
                     ↑                    ↑                  ↑
                    red        →        green        →    refactor
```

The board starts from the `(N) [epic]` issues `project-planning` files. That skill lives in `developer-tools/` because it runs once per project rather than once per unit of work.

**The last three stations are one TDD cycle split across three sessions**, on one ticket and one branch, and each name says which leg it is.

**1. `map-epic`**, once per epic. Slices one epic goal into `(N.M)` tickets filed as native sub-issues of the epic, wired with native blocking, and fills in the epic issue's notes, decisions, and fog. Research and prototype tickets are first-class here, so unknowns get charted rather than guessed at.

**2. `architect-ticket`**, once per ticket. Grills hardest on the **public interface**: the names, parameters, return values, and contracts the implementer is held to. Then it writes that interface as stubs into the real source files, writes the acceptance tests against them, runs them, confirms every one fails, and commits. It leaves the branch **red**.

There is no plan file. The commit is the handoff, because a signature in a source file and a failing test say exactly what a plan could only describe. A test that *errors* rather than fails is how a missing dependency surfaces, which is what a prerequisites checklist used to be for.

**3. `implement-ticket`**, takes the branch **green**. Reads the ticket for the why and `git diff main...HEAD` for the what, then fills in the bodies until every acceptance test passes. Signatures and tests are frozen; everything behind them is free. A contract that proves wrong mid-run halts for a real decision instead of being edited quietly.

**4. `refactor-ticket`**, **refactors** under the green suite. First it gates the diff **true-to-spec**, asking whether the acceptance tests genuinely cover the ticket's expected behaviour and whether the code meets it, because green only means the tests pass, not that they were the right tests. A finding halts the session rather than papering over it. Then it edits the code into line with the ADRs in `docs/adr/` and the code-smell baseline, re-runs the affected tests, and commits the refactor separately. Behaviour never changes here. An edit that takes the suite back to red was never a refactor and gets reverted.

---

## developer-tools

Coding skills that aren't stations on the board. No ordering, and no artifacts passed between them. See [developer-tools/README.md](developer-tools/README.md).

| Skill | What it does |
|-------|--------------|
| `project-planning` | Once per project. Grills me on problem, user, success criteria, scope, and domain language, then proposes vertical-slice epics. Writes `CONTEXT.md` and files one `(N) [epic]` skeleton issue per epic, which is where the board picks up. |
| `codebase-rules` | Surveys the codebase and grills me into one-decision-per-file ADRs in `docs/adr/`, shaped `Decision / Reason / Consequence / Date`. These are what `refactor-ticket` cites. |
| `challenge-adr` | The only door into an existing ADR. An ADR stands until a challenge beats it, and the case has to be that the architecture genuinely improves. Amends in place, retires, or rejects; nothing else edits `docs/adr/`. A blocked skill has to stop and hand the decision back to me. |
| `add-comments` | Establishes a persisted `comment-convention.md`, then walks the code symbol by symbol with an approve/edit/skip preview. Missing language mid-walk triggers a scoped grill. |
| `generate-framework-tests` | Real runnable tests for pytest, vitest, jest, go test, cargo test, or JUnit. A sidecar manifest gives fast-exit when nothing changed and drift-diff when it did. User-added cases are never touched. |
| `brainstorming` | The front door to everything else. Grills an idea trying to **kill** it, then gives a binary verdict, either dead or a paragraph of concrete functionality, and routes the survivor to whichever skill is the smallest fit. |
| `pro-con` | Weigh a decision and commit to a recommendation. Fixed output shape. |
| `prune-skill` | Prunes a skill after it is written or changed. Reads it against a fixed list of smells, reports every finding with a verdict, then applies the approved cuts in one pass. |

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
| `eli5` | Explains at middle-school level, assuming zero knowledge of the subject. |
| `eli10` | Explains at high-school level, with algebra and basic programming assumed. |
| `lecture-preview` | Flies over a deck before the lecture. Ranks its topics against `course-index.md`, gives each one a picture, table, or bounded parallel, and says what to listen for. Writes the topic map `lecture-notes` picks up. |
| `lecture-notes` | Teaches one lecture topic by topic. A topic reaches `Lecture-notes/` only once I can explain it back and have worked a real question from `Exercises/`. |
| `course-index` | Reads a course's `Exams/` and `Exercises/` once into `course-index.md`. Incremental via a SHA manifest. Produces the topic frequency table and the per-question prerequisites the other two read. |

The `eli*` pair do one thing, which is point at their wording rules in [`behaviour/`](behaviour/README.md), one source of truth per level, reachable from any other skill the way `grilling` is. Neither holds across turns. They used to claim they did, and the claim never held, so typing the name again is how you get the level again.

The three course skills hand off through `course-index.md` the way the board hands off through GitHub issues. All of them stay inside one course folder.

Still planned: rehearsal, spaced repetition, exam prep.

---

## archive

[`archive/`](archive/) holds skills I've retired. Never installed, not part of any workflow. See [archive/README.md](archive/README.md) for what's in there and why.

---

## Repo conventions

- **A skill is the unit of install.** Everything a skill references lives inside a skill directory, referenced by a relative path. A sibling's file is reachable only if it declares itself a shared contract, and never a `SKILL.md`. See [ADR 0001](docs/adr/0001-skills-are-self-contained.md).
- **Installed by symlink**, so edits are live and the repo can live anywhere. See [ADR 0002](docs/adr/0002-install-via-symlink.md).
- **Grouped by category, installed flat.** Skill names must stay unique across categories, and a new category means a new entry in the `CATEGORIES` array in `install.sh`. See [ADR 0003](docs/adr/0003-skills-grouped-by-category-directory.md).
- **User-invoked outside `behaviour/`.** A skill that starts work only starts when I type its name, so no skill invokes another and every handoff goes through an artifact. See [ADR 0004](docs/adr/0004-skills-are-user-invoked-outside-behaviour.md).
- `CONTEXT.md` holds the domain language for this repo. Several skills read it at runtime for canonical definitions, such as Supervisor, Red phase, and the Verification failure rule, rather than restating them.
