# Custom-skills

My personal skills for Claude Code and Antigravity (agy). This repo is where I keep them, version them, and reason about how they fit together. It is built around how I work rather than packaged as a general-purpose kit, but it installs cleanly on any machine. See [setup](#setup).

Each skill is a directory with a `SKILL.md` entrypoint plus whatever bundled files it references. They're grouped by purpose:

```
kanban/            the workflow chain, one artifact handed to the next
developer-tools/   everything else for coding, reached for as needed
behaviour/         how the agent talks, not what it builds, borrowed by the rest
schoolwork/        study skills, for when I'm the learner
archive/           retired, never installed
config/            per-agent settings, instruction files, and hooks, reference only
```

`install.sh` walks those categories and symlinks each skill flat into `~/.claude/skills/<name>` for Claude Code and `~/.gemini/config/skills/<name>` for Antigravity (agy). Both tools discover skills by bare directory name, so the category is repo-level organisation only. See [setup](#setup) to install them.

**Invocation follows that grouping exactly.** `behaviour/` is model-invoked. Everything else sets `disable-model-invocation: true` and only starts when I type its name. Antigravity ignores that flag, so there the same split holds only because the descriptions are written for a human reader and not as triggers. See [ADR 0005](docs/adr/0005-support-antigravity-alongside-claude-code.md).

The split is about what a skill does, not what it covers. A `behaviour/` skill is borrowed by work already running, so it has to be reachable by name. Every other skill starts work, and deciding what work happens next is my job. So they carry no model-facing description, cost nothing per turn, and no skill in this repo ever invokes another outside `behaviour/`. The chain hands off through artifacts, and `brainstorming` ends by naming a route instead of taking it.

Behind that split, and behind every setting in [`config/`](config/README.md), is one goal: control what is in the context window, and get the same work out of the same task twice. A skill that only starts when I type its name costs nothing until I want it and does the same thing every time I do. A handoff through a committed artifact means the next session reads a file rather than remembering a conversation. Sessions here are meant to be stateless and repeatable rather than adaptive, because preferences shift between projects and over months, and a rule I can open and edit beats one the model picked up somewhere I cannot see.

---

## Setup

Works with Claude Code and Antigravity (agy). Both read the same `SKILL.md` frontmatter, `name` and `description`, and `install.sh` checks for exactly those.

**1. Clone the repo somewhere permanent.** The install links back to the clone rather than copying files, so moving or deleting the directory later breaks every installed skill.

```bash
git clone https://github.com/Maxastrand04/Custom-skills.git ~/GitHub/Custom-skills
cd ~/GitHub/Custom-skills
```

**2. Run the installer.**

```bash
./install.sh
```

In a terminal this opens a menu. Pick Claude Code, Antigravity, or both, then toggle skills. Skills already installed for that agent start ticked, so pressing enter changes nothing. The menu is a sync: it prints a plan of what it will add and remove, asks once, then links the ticked skills and unlinks the rest. It only ever removes symlinks that point into this repo, so a link to some other skill collection or a real directory is never touched. With `fzf` on your PATH the menu is fzf, tab marks a skill to toggle and enter applies. Without it you get a numbered list and type numbers, a category name, `all`, or `none`.

Skills are linked flat into `~/.claude/skills/<name>` or `~/.gemini/config/skills/<name>`, and `archive/` is never offered. Before anything is linked, every skill in `kanban/`, `developer-tools/`, `behaviour/`, and `schoolwork/` is checked for a `SKILL.md` whose frontmatter carries a `name` and a `description`, with the `name` matching the directory. A skill that fails is reported, hidden from the menu, and the script exits non-zero.

Passing skill names skips the menu and is add-only, so it is safe in scripts and never removes anything. Same for running without a terminal, where it links every skill to both agents. Target flags work in both modes:

```bash
./install.sh grilling unslop               # add two skills to both agents
./install.sh --agy grilling                # add one skill to Antigravity
./install.sh --claude                      # menu for Claude Code only
./install.sh < /dev/null                   # no tty: link everything, add-only
```

**3. Restart the agent.** In Claude Code check with `/skills`. In Antigravity type the skill name as a slash command, `/grilling` for instance.

Re-running `install.sh` is safe. An existing link to the same target is left alone, and a link that points somewhere else inside the repo gets re-pointed, which is what happens when a skill moves between categories. A real file or directory already sitting at the target is never overwritten. That case is reported and skipped for you to resolve by hand.

Because the install is symlinks, `git pull` is the whole update path for skills you already have. Only new skills need `install.sh` again.

### Uninstalling and stale links

Untick a skill in the menu and it is unlinked on apply. A skill that was archived or renamed leaves a link behind whose name no longer matches any live skill. The menu lists those under the plan as stale, with the reason, and removes them on apply. The add-only path reports them and leaves them for you.

To pull everything out by hand instead:

```bash
find ~/.claude/skills ~/.gemini/config/skills -maxdepth 1 -type l -exec sh -c \
  'readlink "$1" | grep -q "/Custom-skills/" && rm "$1"' _ {} \;
```

That form works on both macOS and Linux. `find -lname` is shorter but GNU-only, so it is not there.

### Making them yours

The whole repo is opinionated. It encodes how I work, not a general-purpose kit, so treat a fork as the starting point rather than the finished thing. Adding a skill means dropping a directory with a `SKILL.md` into one of the four categories and re-running `install.sh`. A new category needs an entry in the `CATEGORIES` array in `install.sh` first. Names have to stay unique across categories, since the install is flat.

---

## kanban, the workflow

The core of the repo is one chain that runs from "I have an idea" to "the diff is reviewed and pushed". Each step writes an artifact the next step reads, so nothing is re-derived from memory.

```
map-epic  →  architect-ticket  →  implement-ticket  →  refactor-ticket
(N.M) tasks     stubs + failing      bodies filled,     shape fixed against
under the epic  tests, committed     suite green        the records
                     ↑                    ↑                  ↑
                    red        →        green        →    refactor
```

The board starts from the `(N) [epic]` issues `project-planning` files. That skill lives in `developer-tools/` because it runs once per project rather than once per unit of work.

**The last three stations are one TDD cycle split across three sessions**, on one ticket and one branch, and each name says which leg it is.

**1. `map-epic`**, once per epic. Slices one epic goal into `(N.M)` tickets filed as native sub-issues of the epic, wired with native blocking, and fills in the epic issue's notes, decisions, and fog. Research and prototype tickets are first-class here, so unknowns get charted rather than guessed at.

**2. `architect-ticket`**, once per ticket. Grills hardest on the **public interface**: the names, parameters, return values, and contracts the implementer is held to. Then it writes that interface as stubs into the real source files, writes the acceptance tests against them, runs them, confirms every one fails, and commits. It leaves the branch **red**.

There is no plan file. The commit is the handoff, because a signature in a source file and a failing test say exactly what a plan could only describe. A test that *errors* rather than fails is how a missing dependency surfaces, which is what a prerequisites checklist used to be for.

**3. `implement-ticket`**, takes the branch **green**. Reads the ticket for the why and `git diff main...HEAD` for the what, then fills in the bodies until every acceptance test passes. Signatures and tests are frozen; everything behind them is free. A contract that proves wrong mid-run halts for a real decision instead of being edited quietly.

**4. `refactor-ticket`**, **refactors** under the green suite. First it gates the diff **true-to-spec**, asking whether the acceptance tests genuinely cover the ticket's expected behaviour and whether the code meets it, because green only means the tests pass, not that they were the right tests. A finding halts the session rather than papering over it. Then it edits the code into line with the PCRs in `docs/pcr/`, the ADRs in `docs/adr/`, and the code-smell baseline, re-runs the affected tests, and commits the refactor separately. Behaviour never changes here. An edit that takes the suite back to red was never a refactor and gets reverted.

---

## developer-tools

Coding skills that aren't stations on the board. No ordering, and no artifacts passed between them. See [developer-tools/README.md](developer-tools/README.md).

| Skill | What it does |
|-------|--------------|
| `project-planning` | Once per project. Grills me on problem, user, success criteria, scope, and domain language, then proposes vertical-slice epics. Writes `CONTEXT.md` and files one `(N) [epic]` skeleton issue per epic, which is where the board picks up. |
| `challenge-pcr` | The only door into an existing PCR, the project-wide conventions in `docs/pcr/`. A PCR stands until a challenge beats it, and the case has to be a real project adaption worth the ripple. Amends in place, retires, or rejects; nothing else edits `docs/pcr/`. A blocked skill has to stop and hand the decision back to me. |
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
| `lecture-preview` | Turns one deck into a one-page formula sheet before the lecture. Every formula the deck introduces, its symbols named, one line on when to reach for it. |
| `lecture-notes` | Teaches one lecture topic by topic. A topic reaches `Lecture-notes/` only once I can explain it back and have worked a real question from `Exercises/`. |
| `course-index` | Reads a course's `Exams/` and `Exercises/` once into `course-index.md`. Incremental via a SHA manifest. Produces the topic frequency table and the per-question prerequisites the other two read. |
| `example-workthrough` | Works one example end to end, opening with the theory and formulas it will use. Needs no course folder. Use it when a formula on the sheet is unclear. |
| `write-formula-sheet` | Builds `formulas.md` and `formula-derivations.md` from the lectures, exercises, and exams, grouping formulas by what you use together and ranking the groups by exam frequency from `course-index.md`. |

The `eli*` pair do one thing, which is point at their wording rules in [`behaviour/`](behaviour/README.md), one source of truth per level, reachable from any other skill the way `grilling` is. Neither holds across turns. They used to claim they did, and the claim never held, so typing the name again is how you get the level again.

The four course skills hand off through `course-index.md` the way the board hands off through GitHub issues. All of them stay inside one course folder. `example-workthrough` is the exception, it needs no course folder and only runs when you ask for it by name.

Still planned: rehearsal, spaced repetition, exam prep.

---

## archive

[`archive/`](archive/) holds skills I've retired. Never installed, not part of any workflow. See [archive/README.md](archive/README.md) for what's in there and why.

---

## config

Skills are half of what makes Claude Code and Antigravity work for me. [`config/`](config/README.md) is the other half, split into [`config/claude/`](config/claude/README.md) and [`config/agy/`](config/agy/README.md). Each folder is the full config for that one agent, the instruction file, hooks, and for Claude Code the settings that turn features off and the status line. The two overlap on purpose so either can be read on its own.

**Reference only.** `install.sh` does not touch it. There is one `~/.claude/settings.json` and one `~/.gemini/config/` per machine, and overwriting yours with mine would eat whatever you already had. Read the files, take the parts you want, paste them into your own. Skills are all-or-nothing per skill. Settings are pick and choose.

Every one of those settings serves the same goal as the skills, which is control over what sits in the context window and repeatability across runs. `autoMemoryEnabled: false` is the sharpest example. Memory would open every session with notes from sessions about something else, spending context I did not choose and making this run depend on the last one. Stateless beats adaptive here, because my preferences shift between projects and over months, and a rule I can point at in a file beats a preference the model inferred weeks ago. Same reasoning for `disableBundledSkills`, so the only skills advertised to the model are mine, and for the `deny` block, which drops tools I never use so their descriptions stop riding along in context and nothing reaches for them mid-task. [config/README.md](config/README.md) takes each one in turn.

It also explains the thing that looks like over-engineering from outside, which is `unslop` running three ways at once. It is a model-invoked skill, plus a `SessionStart` hook that injects the full rule set, plus a `UserPromptSubmit` hook (or `PreInvocation` in Antigravity) that re-states the worst offenders before every single reply. A rule read once at turn one loses to the model's defaults by turn twelve, and long output is where the tells come back. The redundancy is the point.

---

## Repo conventions

- **A skill is the unit of install.** Everything a skill references lives inside a skill directory, referenced by a relative path. A sibling's file is reachable only if it declares itself a shared contract, and never a `SKILL.md`. See [ADR 0001](docs/adr/0001-skills-are-self-contained.md).
- **Installed by symlink**, so edits are live and the repo can live anywhere. See [ADR 0002](docs/adr/0002-install-via-symlink.md).
- **Grouped by category, installed flat.** Skill names must stay unique across categories, and a new category means a new entry in the `CATEGORIES` array in `install.sh`. See [ADR 0003](docs/adr/0003-skills-grouped-by-category-directory.md).
- **User-invoked outside `behaviour/`.** A skill that starts work only starts when I type its name, so no skill invokes another and every handoff goes through an artifact. See [ADR 0004](docs/adr/0004-skills-are-user-invoked-outside-behaviour.md).
- **Claude Code and Antigravity, one skill tree.** Both agents get the same symlinks, config is per agent under `config/`, and Antigravity's lack of `disable-model-invocation` is a known gap. See [ADR 0005](docs/adr/0005-support-antigravity-alongside-claude-code.md).
- **The menu syncs, arguments add.** Interactive runs remove unticked and stale links, but only ones pointing into this repo. Skill names on the command line never remove anything. See [ADR 0006](docs/adr/0006-interactive-install-is-a-sync.md).
- `CONTEXT.md` holds the domain language for this repo. Several skills read it at runtime for canonical definitions, such as Supervisor, Red phase, and the Verification failure rule, rather than restating them.
