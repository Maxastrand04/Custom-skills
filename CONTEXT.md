# Custom-skills

My personal agent skills for Claude Code, Antigravity, and Codex. AI Society members install the shared set as the `max` **Plugin**. I choose my personal set through `install.sh`. Claude Code and Antigravity link to the source folders. Codex links to generated copies under `.codex-build/skills/`, with a separate shared set under `plugins/max/skills/`. This repo exists so the skills I use stay versioned and consistent with each other.

This file is the canonical domain language for the repo. Several skills read it at runtime rather than restating definitions in their own `SKILL.md`.

## Language

**Skill**:
A directory containing a `SKILL.md` plus any files that `SKILL.md` references. Lives one level down, inside a **Category**. The directory is the unit of install.
_Avoid_: extension, command

**Category**:
A top-level directory grouping Skills by purpose: `kanban/` (the workflow chain), `developer-tools/` (Skills off the chain, including the **eli Skills**), `behaviour/` (Skills that shape how Claude talks rather than what it builds, borrowed by Skills in any other Category), `schoolwork/` (study and comprehension Skills, for when I'm the learner), `archive/` (retired, never installed). Repo-level metadata only, so it never appears in a Skill's name or invocation. Adding one means adding it to the `CATEGORIES` array in `install.sh`.
_Avoid_: group, namespace, section, folder

**SKILL.md**:
The entrypoint of a Skill. YAML frontmatter declares `name` and `description`; the body is the prompt content the agent loads.
_Avoid_: manifest, config

**Bundled file**:
A file inside a Skill directory that `SKILL.md` references via a relative path (e.g., a template, a format spec). Travels with the Skill.
_Avoid_: resource, asset, dependency

**Install**:
Creating a symlink from the agent's skill directory so it can load the Skill. Claude Code uses `~/.claude/skills/<name>` and Antigravity uses `~/.gemini/config/skills/<name>`, both pointing to `<category>/<name>/`. Codex uses `~/.agents/skills/<name>`, pointing to generated copies under `.codex-build/skills/<name>/`. Every destination is **flat**. A source edit is live for Claude Code and Antigravity, while Codex needs another installer run to rebuild its copies. The interactive menu removes unticked and **stale** links only when they point into this repo.
_Avoid_: deploy, copy

**Plugin**:
The shared set distributed as `max`. Claude Code reads its selection from `.claude-plugin/marketplace.json`, with the repo root as its source. Codex reads `.agents/plugins/marketplace.json`, which points to the generated package under `plugins/max/`, built from the same Skill list, so the two marketplaces always match. Skills carry the `max:` prefix, as in `/max:grilling` for Claude Code and `$max:grilling` for Codex. The list is independent of the personal installer. See ADR-0007 and ADR-0008.
_Avoid_: package, bundle

**Stale link**:
An installed symlink that points into this repo but whose name no longer matches any live Skill, because the Skill was archived or renamed. Listed with its reason in the menu's plan and removed on apply. Reported and left alone on the add-only path.
_Avoid_: dangling (too narrow, an archived Skill's link still resolves), orphan

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
An Architecture Decision Record. A binding decision about the shape of one region of a codebase, one per file in `docs/adr/`, written as Decision, Reason, Consequence, and Date per **Record format**. It names something with a spine: a module's purpose and shape, what code inside it may not do, a dependency direction, a data owner, a public interface that beat a real alternative. There is no softer second kind: a recorded choice is a rule a reviewer cites by number. `architect-ticket` writes them at its diff gate, one per argument the grill had, and `refactor-ticket` writes one when a diff introduces a shape neighbours will copy. Those two stations may also amend one in-session when the work gives them a reason; the reason goes in the session and the commit message, never in the file. `implement-ticket` and `autopilot-ticket` write none, since neither makes decisions.
_Avoid_: rule, convention, decision record, guideline

**PCR**:
A Project Convention Record. A binding convention that holds across the whole project, one per file in `docs/pcr/`, same four fields as an **ADR**: tech stack, allowed libraries, naming, comment convention, object-oriented or not, test runner and layout. The test is ripple: changing one touches every file, which is why only a `challenge-pcr` session may, per **Stands**. `architect-ticket` writes one when its ticket is the first to settle something project-wide. A PCR overrides any entry of `refactor-ticket`'s `code-standards.md` baseline it contradicts. A Skill blocked by one names it and stops.
_Avoid_: standard, style guide, project rule, config

**Record format**:
The shared contract for both record kinds, `kanban/architect-ticket/RECORD-FORMAT.md`. Holds the template, the tests for what earns an **ADR** and what earns a **PCR**, the one-decision-per-file rule, and who may write or change each. Every Skill that touches `docs/adr/` or `docs/pcr/` reads it at runtime rather than restating it.
_Avoid_: ADR template, ADR-FORMAT

**Stands**:
The default verdict on any **PCR** under challenge, and the whole shape of `challenge-pcr`. A recorded convention stands until a challenge beats it, and the burden sits on the challenge: it has to show the whole project gets better and that the ripple is worth paying, which is a project adaption, not an edit. Inconvenience is the friction the **PCR** was written to create, not an argument against it. When a convention stands and the code has drifted from it, the code is what's wrong.
_Avoid_: still valid, approved, upheld

**Epic**:
A numbered vertical slice of a project, existing only as a `(N) [epic]` GitHub issue. `map-epic` files it as an **Epic skeleton**, then charts it into **Task** sub-issues. Its state is the issue's state, and an epic already filed is immutable, open or closed.
_Avoid_: sprint, phase, iteration, milestone

**Epic goal**:
The one-sentence observable outcome that defines an epic as done. Written when `map-epic` files the epic, confirmed by the user before the issue is created, and never edited afterwards by any Skill. It is the Destination line of the epic issue.
_Avoid_: sprint goal, epic description, deliverable, objective

**Epic skeleton**:
The `(N) [epic]` issue as `map-epic`'s filing mode files it: Destination filled with the **Epic goal**, and Notes, Decisions so far, and Not yet specified each left at a `_Not yet charted._` placeholder. `map-epic` detects it by the epic having no sub-issues yet, and fills the rest in with `gh issue edit`.
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

**pro-con**:
The standalone decision skill. Weighs an option set and commits to a single recommendation, filling `template_output.md` exactly so every run has the same shape.
_Avoid_: tradeoff skill, decision matrix, options analysis

**Naked term**:
A domain word used in output before it has been glossed, meaning defined in plain words in a gloss block placed before the first paragraph that uses it. `gloss-me` owns the rule and no Skill that borrows it ships one. A term escapes being naked if it sits on the floor, is in the **Glossary** under a domain heading or the current project's heading, or was glossed earlier in the conversation. A definition in `CONTEXT.md`, an ADR, or any other project doc does not count, since project docs describe the project and not what I know. The floor defaults to algebra and basic programming, and `talk-to-middleschooler` lowers it to nothing.
_Avoid_: jargon, unexplained term, technical term

**Glossary**:
The user's personal list of terms they already know, at `~/.claude/glossary.md`, shared by every project and by both agents. Bare terms under domain headings and per-project headings, no definitions, since the agent knows the meanings and the file only records that I do. A known-terms list rather than an unknown-terms list because the unknown set is endless, so a missing entry costs one extra gloss instead of a **Naked term**. Project vocabulary I have confirmed goes under a `## Project: <project-name>` heading and counts as known only inside that project. `CONTEXT.md` defines the project's terms; the Glossary records which of them I know. `gloss-me` is its only agent writer; I may edit it by hand.
_Avoid_: dictionary, vocabulary list, term index

**gloss-me**:
The `behaviour/` Skill that decides which terms get glossed. It reads the **Glossary** once per conversation, glosses every **Naked term** in a `New terms` block right before the paragraph that first uses it, chaining glosses so each leans only on known terms or lines above it, and ends each response that glossed one with a single footer asking which new terms I'm comfortable with. Confirmed terms get appended. A rejected term starts the clarify loop, which offers synonyms, a new gloss, or a rewrite without the term, then resumes the interrupted work once I get it. Silence adds nothing. With no task in progress, `/gloss-me` seeds the Glossary one domain at a time. It owns which terms get glossed, never the wording level, which stays with the **Talk-to Skill** when one is active.
_Avoid_: glossary skill, term checker

**Talk-to Skill**:
Either of the two model-invoked wording Skills in `behaviour/`, namely `talk-to-middleschooler` and `talk-to-highschooler`. Each owns the language rules for one level and nothing else, and borrows `gloss-me` for which terms get glossed, with no persistence and no change to what work gets done. Model-invoked so any other Skill can borrow the voice, the way `grilling` is borrowed for interview mechanics.
_Avoid_: voice skill, tone skill, style guide

**eli Skill**:
Either of the two user-invoked level Skills in `developer-tools/`: `eli5`, which pairs with `talk-to-middleschooler`, and `eli10`, which pairs with `talk-to-highschooler`. Each sets the level for one explanation and nothing else. The level does not persist; the user types the name again to get it again. The rules live in the paired **Talk-to Skill**, never restated here.
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
- **Install** maps a **Skill** to a symlink in the selected agent's skill directory. Codex rebuilds its flat copies first, per ADR-0008.
- A **Bundled file** is only referenced by `SKILL.md` via a path relative to the **Skill** directory, never by an absolute path outside the **Skill**
- One **Skill** may read another's **Bundled file** through `../<skill-name>/<file>` only when the file declares itself a shared contract. A `SKILL.md` never counts, per ADR-0001. A same-Category link resolves in the sources. A cross-Category link fails when the filesystem follows a symlink into the source folder, even though the installed links appear flat. The Codex builder resolves this by placing copies beside one another. The Claude Plugin keeps the Category layout, so cross-Category links still fail there. A Codex marketplace copy includes referenced shared files even when their owning Skill is excluded.
- `architect-ticket` and `implement-ticket` are the first two legs of the **TDD cycle**, joined by the **Red branch** and nothing else. The first grills the **Public interface**, writes it as stubs, writes the **Acceptance tests**, observes them fail, and commits. The second reads the **Ticket** and the diff, runs the **Green loop** under **Point, don't paste** and **Terse verdicts**, and halts on a **Loop exit** rather than editing a frozen signature or test. On green, its Finalization closes the GitHub issue with `gh issue close`, best-effort and gated on the issue reference being present. Closing the issue is the whole status change, since no file mirrors it. `refactor-ticket` is the third leg, joined to the second by the green suite. It gates the diff true-to-spec against the **Ticket**, then edits shape only, and an affected test going red means the edit changed behaviour and was never a refactor.
- Every **ADR** and **PCR** renders from the same **Record format**, and the two differ by blast radius. An **ADR** binds one region, so the station that has the argument in front of it, `architect-ticket` at its grill or `refactor-ticket` against a frozen signature, may amend it and carry the reason in the commit. A **PCR** binds every file, so changing one takes a whole `challenge-pcr` session. That Skill is deliberately user-invoked: a Skill that could reach it would eventually reach it to unblock itself, which is the exact pressure the burden of proof exists to resist. So `refactor-ticket` fixes code to comply rather than arguing with a **PCR** it dislikes, `architect-ticket` names a blocking convention and stops rather than designing around it, and `implement-ticket` treats a decision it finds itself weighing as a contract gap and halts, since the architect was meant to have settled it. Records accumulate as the board runs; there is no separate Skill that surveys a codebase for them.
- **`behaviour/` is the only model-invoked Category. Everything else sets `disable-model-invocation: true`.** Codex copies replace that setting with `policy.allow_implicit_invocation: false` in `agents/openai.yaml`. The line is what a Skill does, not what it is about. A `behaviour/` Skill is *borrowed* by work already running, so it has to be reachable: `grilling` supplies interview mechanics to most of the repo, `unslop` always applies, a **Talk-to Skill** lends its voice to any Skill that needs it, and `gloss-me` glosses for every Skill that talks to me. `gloss-me` is also the one `behaviour/` Skill that writes a file, the **Glossary**, which lives outside the repo and belongs to me, not to any project. Every other Skill *starts* work, and starting work is my decision, not Claude's.
- Because of that, no Skill ever invokes another outside `behaviour/`. The `kanban/` chain hands off through artifacts instead, meaning an **Epic** issue, a **Ticket**, a **Red branch**, so no station needs to name the next one. `brainstorming` ends by naming a route rather than taking it, and a Skill blocked by a **PCR** stops and names it rather than opening `challenge-pcr`. The cost of all this is context load I stop paying, traded for **Cognitive load** I take on instead: I am the index that has to remember these Skills exist.
- `map-epic` is the first station on the board and feeds `architect-ticket`. It files a new **Epic** as an **Epic skeleton**, charts a chosen one by slicing its goal into `(N.M)` **Task** sub-issues and filling in the skeleton body around them, and graduates fog into tickets on later runs. It publishes every **Ticket** through **Ticket shapes**, which it reads from `new-ticket/`, rather than through templates of its own. A charted **Task** goes straight to `architect-ticket`.
- `new-ticket` lives in `kanban/` beside the chain rather than on it. It grills WHAT, meaning user-visible behaviour and scope, with no architecture, file paths, or tests, and publishes a **Ticket** for work no **Epic** covers. Its split path publishes a parent plus one **Sub-issue** per vertical slice, in dependency order, gated on the **two-tier coverage check**. It also owns **Ticket shapes**, which `map-epic` reads, so an epic **Ticket** and a standalone one are the same artifact. A **Ticket** it produces feeds `architect-ticket` exactly as a **Task** row does, which is what the **WHAT / HOW split** exists for.
- `course-index` and `lecture-notes` connect through the **Course index** file, not by invocation, the same artifact handoff the `kanban/` chain uses. Both are bounded by the **Course folder**. `course-index` fast-exits on a SHA manifest at `.course-index/manifest.json` the way `generate-framework-tests` does, so re-runs read only added or changed PDFs. `lecture-notes` discloses its video branch to `transcript.md`, reached only when a lecture link is in play; that file owns the two-tier transcript route (yt-dlp captions, then `whisper.cpp` locally) and the rule that Swedish audio uses KB-Whisper while English uses stock `large-v3-turbo`.
- The wording family, the **eli Skills** and the **Talk-to Skills**, is off the chain and reads no repo artifact. It only rewrites how output is worded. Each **eli Skill** invokes exactly one **Talk-to Skill** for its rules; the pairing is the only place a level is defined twice, and it is defined once. Which terms count as known is `gloss-me`'s call, never the **Talk-to Skill**'s. It reads the level's floor and the **Glossary**, and anything absent from both is a **Naked term**, even if the project's `CONTEXT.md` defines it.
- `gloss-me` reaches the Skills that talk to me through three doors. `grilling` borrows it, which covers `architect-ticket`, `map-epic`, `new-ticket`, and `brainstorming`. Each **Talk-to Skill** borrows it, which covers the **eli Skills**. `pro-con` names it directly. The global instruction file names it for every other session, so `implement-ticket`, `autopilot-ticket`, and a plain question with no Skill all gloss too. The per-Skill wiring is redundant with that line on purpose, so the Skills still gloss for anyone who copies them without my config.
- `generate-framework-tests`, now archived, produces **Framework tests**, meaning real runnable code, that the project's own runner executes. It uses a **Sidecar manifest** to enable **Fast-exit** on re-invocation and **Drift-diff** on changed sources. **User-added-case immunity** is enforced via the manifest's `cases[]` list. The markdown-spec approach it replaced, `generate-test` and `run-tests`, is archived.

## Example dialogue

> **Me:** "Where should the ADR format spec live?"
> **Claude:** "Inside the `architect-ticket` Skill, next to its `SKILL.md`, as `RECORD-FORMAT.md`. It's a Bundled file, and every Skill that writes an ADR or a PCR reaches it as `../architect-ticket/RECORD-FORMAT.md`. Skills are self-contained, so the format travels with the Skill that writes most records rather than living in a shared `~/.claude/templates/` directory."
