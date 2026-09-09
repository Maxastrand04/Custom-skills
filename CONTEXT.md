# Custom-skills

My personal Claude Code skills, symlinked into `~/.claude/skills/`. Not a distribution. This repo exists so the skills I actually use stay versioned and consistent with each other.

This file is the canonical domain language for the repo. Several skills read it at runtime rather than restating definitions in their own `SKILL.md`.

## Language

**Skill**:
A directory containing a `SKILL.md` plus any files that `SKILL.md` references. Lives one level down, inside a **Category**. The directory is the unit of install.
_Avoid_: plugin, extension, command

**Category**:
A top-level directory grouping Skills by purpose: `kanban/` (the workflow chain), `developer-tools/` (coding Skills off the chain), `behaviour/` (Skills that shape how Claude talks rather than what it builds, borrowed by Skills in any other Category), `schoolwork/` (study and comprehension Skills, for when I'm the learner), `archive/` (retired, never installed). Repo-level metadata only, so it never appears in a Skill's name or invocation. Adding one means adding it to the `CATEGORIES` array in `install.sh`.
_Avoid_: group, namespace, section, folder

**SKILL.md**:
The entrypoint of a Skill. YAML frontmatter declares `name` and `description`; the body is the prompt content Claude Code loads.
_Avoid_: manifest, config

**Bundled file**:
A file inside a Skill directory that `SKILL.md` references via a relative path (e.g., a template, a format spec). Travels with the Skill.
_Avoid_: resource, asset, dependency

**Install**:
Creating a symlink from `~/.claude/skills/<name>` to this repo's `<category>/<name>/` directory so Claude Code loads the Skill. The symlink is always **flat**, because Claude Code discovers Skills by bare directory name and does not read **Categories**. A Skill that has moved between Categories is silently re-pointed on the next `install.sh` run.
_Avoid_: deploy, sync, copy

**TDD cycle**:
The three stations `architect-ticket`, `implement-ticket` and `refactor-ticket`, run in that order on one **Ticket** and one branch, as the red, green and refactor legs of one red-green-refactor cycle. Each Skill's name says which leg it is. Red leaves every **Acceptance test** failing, green takes them all passing, refactor changes only shape underneath them. The cycle is split across three sessions rather than three phases of one session, so the legs hand off through the **Red branch** and then the green suite instead of through accumulated context.
_Avoid_: review stage, QA pass, cleanup pass

**Red branch**:
What `architect-ticket` leaves behind and the only handoff between it and `implement-ticket`: a committed branch carrying the **Public interface** as stubs in the real source files, the **Acceptance tests** written against those stubs, and every one of those tests observed failing. It replaced the plan file, because a signature and a failing test carry the contract exactly where prose could only describe it. `implement-ticket` reads the **Ticket** plus `git diff main...HEAD` and needs nothing else.
_Avoid_: plan, spec branch, scaffold, skeleton

**Public interface**:
The names, parameters, return values, and documented contracts of every entry point a change adds or alters. Settled with the user in `architect-ticket`'s grill, written into the source files as stubs, and frozen from that point: `implement-ticket` may not rename, reorder, add, or drop one. Everything behind it, meaning helpers, control flow, data structures, and private modules, is the implementer's call and needs no approval.
_Avoid_: API, contract surface, signature list

**Acceptance test**:
A test written by `architect-ticket` against the **Public interface** stubs, before any implementation exists. **The acceptance tests are the acceptance criteria**; there is no separate list, and each test's name and docstring is the one place its criterion is written. Derived from the **Ticket**'s user-visible expected behaviour plus the edge cases and failure modes the contract names. Frozen for `implement-ticket`, and checked against the **Ticket** by `refactor-ticket`'s true-to-spec pass.
_Avoid_: AC, criterion, verification test, spec test

**ADR**:
A binding decision about the shape of a codebase, one per file in `docs/adr/`, written as Decision, Reason, Consequence, and Date per `codebase-rules/ADR-FORMAT.md`. There is no softer second kind: a recorded choice is a rule a reviewer cites by number. The Reason names the alternative that lost, which is what stops a later reader undoing the decision by accident, and the Consequence is what lets `refactor-ticket` tell compliance from breach without a check recipe. Any codebase-shaping Skill may write a new one. Changing or retiring an existing one takes a whole `challenge-adr` session, per **Stands**, and that Skill is user-invoked, so no Skill can start it. A blocked Skill names the ADR and stops.
_Avoid_: rule, convention, decision record, guideline

**Stands**:
The default verdict on any **ADR** under challenge, and the whole shape of `challenge-adr`. A recorded decision stands until a challenge beats it, and the burden sits on the challenge: it has to show the codebase gets architecturally better on a named axis, meaning coupling, cohesion, encapsulation, or dependency direction. Inconvenience is the friction the **ADR** was written to create, not an argument against it. When a decision stands and the code has drifted from it, the code is what's wrong.
_Avoid_: still valid, approved, upheld

**Adaptive grill**:
The gap-filling interview in `project-planning` that runs after reading any existing `CONTEXT.md` and the repo's `(N) [epic]` issues. Summarizes current understanding first, then asks only where gaps remain across five areas: problem statement, primary user, success criteria, scope boundaries, and domain language. One question per turn. Stops when all five areas can be stated with confidence, and does not run a fixed N-question script.
_Avoid_: alignment grill, kickoff, scoping session, intake

**Epic**:
A numbered vertical slice of a project, existing only as a `(N) [epic]` GitHub issue. `project-planning` proposes it and files it as an **Epic skeleton**; `map-epic` charts it into **Task** sub-issues. Its state is the issue's state, and an epic already filed is immutable, open or closed.
_Avoid_: sprint, phase, iteration, milestone

**Epic goal**:
The one-sentence observable outcome that defines an epic as done. Written by `project-planning` during epic breakdown, confirmed by the user at the confirm gate, and never edited afterwards by any Skill. It is the Destination line of the epic issue.
_Avoid_: sprint goal, epic description, deliverable, objective

**Epic skeleton**:
The `(N) [epic]` issue as `project-planning` files it: Destination filled with the **Epic goal**, and Notes, Decisions so far, and Not yet specified each left at a `_Not yet charted._` placeholder. `map-epic` detects it by the epic having no sub-issues yet, and fills the rest in with `gh issue edit`.
_Avoid_: stub epic, empty epic, draft issue

**Task**:
A `(N.M)` **Ticket** published by `map-epic` as a sub-issue of an **Epic**, labelled `epic:task`. Represents one thin vertical slice of the **Epic goal**. Its `M` is `max(M) + 1` over the map's existing sub-issue titles, append-only, and its state is the issue's state, closed by `implement-ticket` when the work lands.
_Avoid_: story, to-do, backlog item, task row

**WHAT / HOW split**:
The division of labor between `new-ticket`, which grills WHAT, meaning user-visible behaviour and scope, with no architecture, file paths, or tests, and `architect-ticket`, which grills HOW, meaning the **Public interface**, the **Acceptance tests**, and the structure behind them. The two Skills hand off via a GitHub Issue. The line is drawn where the knowledge is: a **Ticket** is written before anyone reads the code, so pinning an exact bar there pins it blind.
_Avoid_: spec/design split, intake/build split

**Ticket**:
A published GitHub Issue holding one unit of work, in one of two shapes: a task ticket, carrying Goal, Expected behaviour, Out of scope, and Branch, or a question ticket, carrying a Question only. `map-epic` publishes tickets under an epic map issue with the `epic:` label scope; `new-ticket` publishes standalone ones with the `ticket:` scope. Both render the same templates.
_Avoid_: card, story, work item

**Ticket shapes**:
`new-ticket/ticket-shapes.md`, the single source of truth for how any **Ticket** is written and published: body templates, title format, the `<scope>:<type>` label table, branch slug rule, AI disclaimer, `gh` preflight, the preview-edit-approve publish loop, and native sub-issue and blocking wiring. Both `new-ticket` and `map-epic` read it, and neither restates it.
_Avoid_: issue template, ticket spec

**Sub-issue**:
A child **Ticket** published by `new-ticket`'s split path when the parent's expected behaviour spans clearly separable user-visible concerns. Each sub-issue is an independently demoable vertical slice with its own expected behaviour, attached to its parent and wired to its blockers through the GitHub API rather than through body text. The union of sub-issue behaviour must cover the parent's full behaviour, which is what the **two-tier coverage check** enforces, per-slice and systemic.
_Avoid_: child issue, subtask

**Framework test**:
A real, framework-executable test file produced by `generate-framework-tests`, for pytest, vitest, jest, `go test`, `cargo test`, or JUnit Jupiter. It contains no YAML frontmatter and no skill markers. It is plain framework code, and the project's test runner runs it directly.
_Avoid_: test spec, generated test, scaffold test

**Sidecar manifest**:
The JSON file at `.generate-framework-tests/sidecar-manifest.json` written by `generate-framework-tests` after each successful test-file write. Records `source_sha`, `generated_at`, and the `cases[]` list for each source file the skill has ever written tests for. Used for fast-exit and drift-diff on re-invocation. Never hand-edited.
_Avoid_: test manifest, lockfile, index

**Fast-exit**:
The short-circuit check at the start of each `generate-framework-tests` invocation. If all in-scope source files have sidecar-manifest entries whose recorded SHA-256 matches current content, and no new untested source files exist, the skill prints "all tests are up to date, nothing to do" and exits with no plan and no writes.
_Avoid_: cache hit, skip check, staleness check

**Drift-diff**:
The per-source-file algorithm in `generate-framework-tests` that runs when a source file's SHA-256 has changed since the last sidecar-manifest write. Re-derives the proposed case list from the current source, diffs it against the manifest's `cases[]`, and buckets the delta into `+add` / `-remove` / `~update` annotations shown in the approval plan.
_Avoid_: delta detection, change detection, re-gen

**User-added-case immunity**:
The hard invariant in `generate-framework-tests`: any test case present in a framework test file but absent from the sidecar manifest's `cases[]` for that source is treated as user-authored and is never proposed for change, removal, or update, regardless of what drift-diff detects in the source.
_Avoid_: user case protection, manual case preservation

**Green loop**:
`implement-ticket`'s single execution mode. The main thread implements inline, with no implementer subagent, then runs only the **Acceptance tests** the **Red branch** added, reads every failure before fixing any of them, and repeats until the suite is green. The pass number is reported each time, so a loop that isn't converging shows itself.
_Avoid_: phase loop, retry loop, TDD loop

**Point, don't paste**:
The `implement-ticket` context rule. The **Ticket** body, the stubs, and the tests are read at the moment they're needed and never pasted back into a response. It exists because a pasted block repeats verbatim across every retry, and that repetition accumulates in the main thread's own context, which is the main driver of context growth over a multi-phase run. Paired with **Terse verdicts**.
_Avoid_: pointer pattern, lazy loading

**Terse verdicts**:
The `implement-ticket` rule that once a **Green loop** pass returns, the main thread states a one-line verdict and moves on, never re-pasting runner output for a passing test or restating what it just implemented. The `Edit` call is the record. Paired with **Point, don't paste**.
_Avoid_: status update, progress note

**Loop exits**:
The three things that stop `implement-ticket`'s **Green loop** and go to the user, because none is the implementer's to fix: the **Public interface** can't express the behaviour, an **Acceptance test** contradicts the **Ticket** or the stub it sits under, or the same test fails with the same evidence two passes running. The model states its best guess at the cause as a guess, and the user decides: supply a hint, send the contract back to `architect-ticket`, or stop.
_Avoid_: retry budget, escalation rule, attempt cap

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
The standalone decision skill. Weighs an option set and commits to a single recommendation, filling `template_output.md` exactly so every run has the same shape.
_Avoid_: tradeoff skill, decision matrix, options analysis

**Naked term**:
A domain word used in output before it has been glossed, meaning defined in plain words in the same sentence it first appears. Neither **Talk-to Skill** ships one; they differ only in where the floor sits. A term escapes being naked if it is defined in a `CONTEXT.md`, an ADR, or another doc read earlier in the conversation, or, for `talk-to-highschooler`, if it sits on that Skill's assumed floor of algebra and basic programming.
_Avoid_: jargon, unexplained term, technical term

**Talk-to Skill**:
Either of the two model-invoked wording Skills in `schoolwork/`, namely `talk-to-middleschooler` and `talk-to-highschooler`. Each owns the language rules for one level and nothing else, with no persistence and no change to what work gets done. Model-invoked so any other Skill can borrow the voice, the way `grilling` is borrowed for interview mechanics.
_Avoid_: voice skill, tone skill, style guide

**eli Skill**:
Either of the two session modes in `schoolwork/`: `eli5`, which pairs with `talk-to-middleschooler`, and `eli10`, which pairs with `talk-to-highschooler`. Each owns only persistence, staying on every turn, including inside Skills invoked later, until the user says "stop eli5", "stop eli10", or "normal mode". The rules live in the paired **Talk-to Skill**, never restated here.
_Avoid_: simplify mode, plain English skill, dumb it down

**Course folder**:
The directory a `schoolwork/` study Skill operates in. Holds `Lectures/` (slide decks), optionally `Exercises/` and `Exams/`, the `Lecture-notes/` output directory, and `course-index.md`. Both `lecture-notes` and `course-index` resolve the course root and read nothing above or outside it; a missing `Exercises/` or `Exams/` is normal and never triggers a wider search.
_Avoid_: course root dir, subject folder, class directory

**Deck**:
One lecture's slide PDF in `Lectures/`, the single input to a `lecture-notes` run. Read in 20-page batches to its last page, because the Read tool caps a PDF at 20 pages per call.
_Avoid_: slides, presentation, PDF, lecture file

**Provenance tag**:
The marker `lecture-notes` attaches to every sentence in a notes file that did not come from the **Deck**. Three sources, three tags: deck content is untagged, `[🎙 mm:ss]` marks what was said in the lecture video, `[fill]` marks what Claude supplied. Tagged per sentence, never per section. Upholds the notes file's one guarantee, that `grep '\[fill\]'` lists everything a model invented. Untagged filled text silently breaks it.
_Avoid_: citation, source marker, annotation, attribution

**Fill**:
Content `lecture-notes` writes into a notes file that appears in neither the **Deck** nor the transcript, tagged `[fill]` and unverified. Distinct from an unresolved gap, which goes to the notes file's Open questions section instead. A fill is confident and checkable, an open question is neither. A transcript reduces fills but never retires them.
_Avoid_: inference, gap-fill, hallucination, addition

**High-yield**:
A topic in a **Deck** that recurs across a course's past exams, flagged `**[high-yield]**` in the notes with its count. Sourced only from the **Course index**'s topic frequency table, never by reading exam PDFs during a `lecture-notes` run. The flag names the topic and the count; exam questions themselves are never copied into notes.
_Avoid_: important, exam-relevant, priority, key topic

**Course index**:
The `course-index.md` file at a **Course folder**'s root, written by the `course-index` Skill from every PDF in `Exams/` and `Exercises/`. Contains per-file coverage entries plus the topic frequency table sorted by total, descending. That table is the fixed contract `lecture-notes` reads to flag **High-yield** topics; its shape is not changed independently. Never a solutions document.
_Avoid_: table of contents, exam summary, syllabus, catalogue

**Canonical topic**:
A topic name on the **Course index** manifest's `topics` list, reused across every file that tests the same thing however that file words it. Minted only when no existing name covers the topic. Pitched at the level one lecture covers, narrower than a course and broader than a single question. Without this normalization one recurring topic reads as several one-off topics and nothing is ever flagged **High-yield**.
_Avoid_: tag, label, keyword, subject

## Relationships

- A **Skill** contains exactly one **SKILL.md** and zero or more **Bundled files**
- Every **Skill** lives in exactly one **Category**; `install.sh` walks the live Categories (`archive/` excluded) and installs what it finds
- Because **Install** is flat, **Skill** names must be unique across **Categories**. Two Skills with the same name in different Categories would collide on one symlink
- **Install** maps a **Skill** in this repo to a symlink under `~/.claude/skills/`
- A **Bundled file** is only referenced by `SKILL.md` via a path relative to the **Skill** directory, never by an absolute path outside the **Skill**
- One **Skill** may read another's **Bundled file** to avoid restating a shared contract, referenced as `../<skill-name>/<file>`, which resolves at runtime because **Install** is flat and every **Skill** is a sibling under `~/.claude/skills/`. Within one **Category** the path also resolves in the repo; across **Categories** it resolves only after install, which is the case that matters since that is where Skills run. A file may only be reached this way if it declares itself a **shared contract** in its opening lines, and a `SKILL.md` never counts, per ADR-0001. Four files carry that declaration today: `codebase-rules/ADR-FORMAT.md`, **Ticket shapes**, `lecture-notes/map-format.md`, and `lecture-notes/teaching.md`
- `architect-ticket` and `implement-ticket` are the first two legs of the **TDD cycle**, joined by the **Red branch** and nothing else. The first grills the **Public interface**, writes it as stubs, writes the **Acceptance tests**, observes them fail, and commits. The second reads the **Ticket** and the diff, runs the **Green loop** under **Point, don't paste** and **Terse verdicts**, and halts on a **Loop exit** rather than editing a frozen signature or test. On green, its Finalization closes the GitHub issue with `gh issue close`, best-effort and gated on the issue reference being present. Closing the issue is the whole status change, since no file mirrors it. `refactor-ticket` is the third leg, joined to the second by the green suite. It gates the diff true-to-spec against the **Ticket**, then edits shape only, and an affected test going red means the edit changed behaviour and was never a refactor.
- Every **ADR** in `docs/adr/` is written by whichever Skill is shaping the codebase at the time, and all of them render it from the same `ADR-FORMAT.md`. Changing or retiring one takes a whole `challenge-adr` session, because these numbers are cited in review comments and open branches. That Skill is deliberately user-invoked: a Skill that could reach it would eventually reach it to unblock itself, which is the exact pressure the burden of proof exists to resist. So `codebase-rules`' maintenance branch detects drift and hands it back rather than amending anything, `refactor-ticket` fixes code to comply rather than arguing with an **ADR** it dislikes, and `architect-ticket` names a blocking decision and stops rather than designing around it.
- **`behaviour/` is the only model-invoked Category. Everything else sets `disable-model-invocation: true`.** The line is what a Skill does, not what it is about. A `behaviour/` Skill is *borrowed* by work already running, so it has to be reachable: `grilling` supplies interview mechanics to most of the repo, `unslop` always applies, and a **Talk-to Skill** lends its voice to any Skill that needs it. Every other Skill *starts* work, and starting work is my decision, not Claude's.
- Because of that, no Skill ever invokes another outside `behaviour/`. The `kanban/` chain hands off through artifacts instead, meaning an **Epic** issue, a **Ticket**, a **Red branch**, so no station needs to name the next one. `brainstorming` ends by naming a route rather than taking it, and a Skill blocked by an **ADR** stops and names it rather than opening `challenge-adr`. The cost of all this is context load I stop paying, traded for **Cognitive load** I take on instead: I am the index that has to remember these Skills exist.
- `project-planning` lives in `developer-tools/` rather than on the board, since it runs once per project rather than per unit of work, but its **Epic skeleton** issues are what `map-epic` starts from. It runs a **Git-repo guard** first, hard-stopping outside a git repo, then the `gh` preflight from **Ticket shapes**, then the **Adaptive grill**, which reads any existing `CONTEXT.md` and the repo's **Epic** issues and asks only on gaps, then an epic-breakdown confirm gate, then writes `CONTEXT.md` and files one **Epic skeleton** per new epic. Every step runs in the main thread, with no subagent dispatch.
- `map-epic` is the first station on the board and feeds `architect-ticket`. It reads a chosen **Epic** issue, slices its goal into `(N.M)` **Task** sub-issues, and fills in the **Epic skeleton** body around them. It publishes every **Ticket** through **Ticket shapes**, which it reads from `new-ticket/`, rather than through templates of its own. A charted **Task** goes straight to `architect-ticket`.
- `new-ticket` lives in `kanban/` beside the chain rather than on it. It grills WHAT, meaning user-visible behaviour and scope, with no architecture, file paths, or tests, and publishes a **Ticket** for work no **Epic** covers. Its split path publishes a parent plus one **Sub-issue** per vertical slice, in dependency order, gated on the **two-tier coverage check**. It also owns **Ticket shapes**, which `map-epic` reads, so an epic **Ticket** and a standalone one are the same artifact. A **Ticket** it produces feeds `architect-ticket` exactly as a **Task** row does, which is what the **WHAT / HOW split** exists for.
- `course-index` and `lecture-notes` connect through the **Course index** file, not by invocation, the same artifact handoff the `kanban/` chain uses. Both are bounded by the **Course folder**. `course-index` fast-exits on a SHA manifest at `.course-index/manifest.json` the way `generate-framework-tests` does, so re-runs read only added or changed PDFs. `lecture-notes` discloses its video branch to `transcript.md`, reached only when a lecture link is in play; that file owns the two-tier transcript route (yt-dlp captions, then `whisper.cpp` locally) and the rule that Swedish audio uses KB-Whisper while English uses stock `large-v3-turbo`.
- The `schoolwork/` wording family is off the chain and reads no repo artifact. It only rewrites how output is worded. Each **eli Skill** invokes exactly one **Talk-to Skill** for its rules; the pairing is the only place a level is defined twice, and it is defined once. A **Talk-to Skill** treats a project's `CONTEXT.md` as the sole evidence that a term is already known to the user; anything absent from it, and off the level's floor, is a **Naked term**.
- `add-comments` runs **ensure-convention** first, which locates or grills for a **Comment convention**, then **preview-walk**, its per-symbol approve loop. A missing language mid-walk triggers a **Scoped single-language grill** rather than the full grill.
- `generate-framework-tests` is the repo's only live testing Skill. It produces **Framework tests**, meaning real runnable code, that the project's own runner executes. It uses a **Sidecar manifest** to enable **Fast-exit** on re-invocation and **Drift-diff** on changed sources. **User-added-case immunity** is enforced via the manifest's `cases[]` list. The markdown-spec approach it replaced, `generate-test` and `run-tests`, is archived.

## Example dialogue

> **Me:** "Where should the ADR format spec live?"
> **Claude:** "Inside the `codebase-rules` Skill, next to its `SKILL.md`. It's a Bundled file, and every Skill that writes an ADR reaches it as `../codebase-rules/ADR-FORMAT.md`. Skills are self-contained, so the format travels with the Skill that owns it rather than living in a shared `~/.claude/templates/` directory."
