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

**Prerequisite**:
A row in a plan's `## Phase 0: Prerequisites`, naming something the implementation calls into but does not build: a module, a function, a feature that must already work, a file the plan modifies, a third-party library, or an external resource. Carries a `Where` and a `How to check` concrete enough to confirm in one action. Drafted by `implementation-planning`'s **Prerequisites sweep** and confirmed row by row by `implementation-plan-execute` before Red starts. A missing or broken one halts the plan, since it has to be implemented or fixed first.
_Avoid_: blocker, preflight item, dependency, assumption

**Prerequisites sweep**:
The `implementation-planning` grill step that runs once the `## Public interface` is settled and works out what that interface leans on. Drafted from Exploration rather than asked cold, and closed by asking whether any of it is missing or broken today. Anything absent is work that must land before the plan can run, and the user decides whether it joins this plan, becomes its own, or blocks it.
_Avoid_: dependency check, prereq grill, blocker sweep

**Red phase**:
The mandatory `## Phase 1: Red` that `implementation-planning` puts second in every plan, right after Phase 0. Its rows name a test function and a file and nothing else; the assertions come from the `AC-N` whose `Verify:` clause names that test. It writes the failing tests and no production code. Green phases make those tests pass, and `Phase N: Verification` runs them and expects green. This makes every generated plan test-driven at the phase level, not just at the acceptance-criteria level.
_Avoid_: write-acceptance-tests phase, test phase, TDD phase

**Supervisor**:
Opus in the main thread, orchestrating one `claude` implementer per attempt and one **Reviewer** per run, in `implement-tdd`. Owns the tests, the runner, and every conversation with the user, but never writes production code. `implementation-plan-execute` has no Supervisor: it implements inline and dispatches nothing but its exploration sweep.
_Avoid_: orchestrator, coordinator, driver

**Reviewer**:
An `Explore` subagent that reads the implementation diff and tests after the test-pass loop, explains in plain English what changed mapped to files, and surfaces concerns. Read-only; never edits.
_Avoid_: code reviewer, auditor, checker

**Runner preflight**:
The auto-detect-then-confirm step at the start of test-first skills that locks down which test runner command will gate the implementation loop.
_Avoid_: test setup, harness setup, runner detection

**Adaptive grill**:
The gap-filling interview in `project-planning` that runs after reading any existing `CONTEXT.md` and `project_plan.md`. Summarizes current understanding first, then asks only where gaps remain across five areas: problem statement, primary user, success criteria, scope boundaries, and domain language. One question per turn. Stops when all five areas can be stated with confidence, and does not run a fixed N-question script.
_Avoid_: alignment grill, kickoff, scoping session, intake

**Epic**:
A numbered vertical slice of a project plan, each with a one-sentence epic goal and a status marker (⬜ / 🟡 / ✅). Epics are proposed by `project-planning` and broken into **Task** rows by `epic-planning`. Completed (✅) epics are immutable across re-runs.
_Avoid_: sprint, phase, iteration, milestone

**Epic goal**:
The one-sentence observable outcome that defines an epic as done. Written by `project-planning` during epic breakdown, confirmed by the user at the confirm gate, and never edited once the epic is ✅.
_Avoid_: sprint goal, epic description, deliverable, objective

**Project plan**:
The `project_plan.md` file written by `project-planning` at the consuming project's repo root. Contains a project goal, epic list (each with status marker + epic goal + tasks placeholder), out-of-scope section, and a directory-tree section left at its placeholder. Shared contract consumed by `epic-planning` and `implementation-planning`.
_Avoid_: roadmap file, plan doc

**Task**:
A `(N.M)` row written by `epic-planning` under an epic in `project_plan.md`. Represents one thin vertical slice of the epic goal, sized to become a single GitHub issue. The Plan column starts blank and is filled by `implementation-planning`. The Issue column is optional, and is used only when a **Task** happens to have been filed via the standalone `new-issue`.
_Avoid_: ticket, story, to-do, backlog item

**WHAT / HOW split**:
The division of labor between `new-issue`, which grills WHAT, meaning behavior, scope, and acceptance criteria, with no architecture or file paths, and `implementation-planning`, which grills HOW, meaning architecture, modules, files, tests, and rollout. The two skills hand off via a GitHub Issue.
_Avoid_: spec/design split, intake/build split

**Sub-issue**:
A child GitHub Issue published by `new-issue`'s multi-plan path when the parent's acceptance criteria span clearly separable user-visible concerns. Each sub-issue is an independently demoable vertical slice with its own acceptance criteria and explicit `Blocked by` refs. The union of sub-issue acceptance criteria must cover the parent's full acceptance criteria, which is what the **two-tier coverage check** enforces, per-slice and systemic.
_Avoid_: child issue, subtask, ticket

**From-issue path**:
The branch of `implementation-planning` that starts from an existing GitHub Issue, reached by an explicit `<issue-ref>` arg or by strict-and-confirm auto-detect when `new-issue` just ran in-session. It skips the WHAT topics, since they're already in the issue body, and runs only the HOW topics. Contrasts with the **standalone path**, which runs the full WHAT and HOW grill from scratch.
_Avoid_: issue mode, linked mode, resumption

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

**Phase loop**:
`implementation-plan-execute`'s single execution mode. The main thread implements each phase inline, with no `claude` implementer subagent. The plan's `## Public interface` is the contract, and everything behind it is the model's call, so no implementation choice is gated on user approval. Nothing is tested as a phase completes; testing runs once, in the mandatory Verification phase. If the contract itself proves wrong or incomplete mid-run, the loop halts for a user decision rather than changing a signature silently. Reads the **Exploration summary file** instead of re-reading whole files, per **Point, don't paste**.
_Avoid_: group loop, hands-on mode, supervise mode, parallel mode

**Point, don't paste**:
The `implementation-plan-execute` context rule. Plan sections are read from the plan file at the moment they're needed, never pasted into a response or into a subagent brief. It exists because a pasted block repeats verbatim across every retry, and that repetition accumulates in the main thread's own context, which is the main driver of context growth over a multi-phase run. Paired with **Terse verdicts**.
_Avoid_: pointer pattern, lazy loading

**Terse verdicts**:
The `implementation-plan-execute` rule that once a phase finishes or Verification returns a result, the main thread states a one-line verdict and moves on, never re-pasting a report or restating a prior phase. The plan file's checkboxes are the sole source of truth for cross-phase state. Paired with **Point, don't paste**.
_Avoid_: status update, progress note

**Verification failure rule**:
The single failure-handling mechanism in `implementation-plan-execute`. No phase is retried on its own. Only the mandatory `Phase N: Verification` can fail, and it escalates to the user on the **first** failing `AC-N`, every time, with no automatic retry and no attempt cap. The model names its best guess at the responsible phase and says what it thinks happened, but the user decides the next action: redo a phase, fix it manually, amend the `AC-N` or the `## Public interface` contract, or stop the plan. Whatever they choose runs once, then Verification reruns fresh, and a repeat failure escalates again the same way.
_Avoid_: retry budget, phase-level retry, attempt cap

**Bootstrap exploration sweep**:
The `implementation-plan-execute` step that runs once before Phase 0, refreshed per feature phase thereafter, dispatching one `Explore` subagent on haiku to summarize the current shape of the files the plan touches. It writes to the **Exploration summary file**, so the discovery legwork happens in a subagent's disposable context rather than the main thread's. It is the only subagent the skill dispatches.
_Avoid_: pre-scan, discovery pass, warmup sweep

**Exploration summary file**:
The scratch file, such as `implementation_plans/.exploration-summary_N.N.md`, that `implementation-plan-execute`'s bootstrap exploration sweep writes to before Phase 0, refreshed per phase by overwriting the changed entries. The main thread reads its own scoped slice before implementing a phase. Its contents are never held in context beyond that scoped read, and never pasted into a response. Deleted during Finalization, since it is scratch, not a plan artifact.
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
The standalone decision skill. Weighs an option set and commits to a single recommendation, filling `template_output.md` exactly so every run has the same shape. Manual-invocation only, via `disable-model-invocation: true`, so it never fires on its own mid-task.
_Avoid_: tradeoff skill, decision matrix, options analysis

**Naked term**:
A domain word used in output before it has been glossed, meaning defined in plain words in the same sentence it first appears. Neither **Talk-to Skill** ships one; they differ only in where the floor sits. A term escapes being naked if it is defined in a `CONTEXT.md`, an ADR, or another doc read earlier in the conversation, or, for `talk-to-highschooler`, if it sits on that Skill's assumed floor of algebra and basic programming.
_Avoid_: jargon, unexplained term, technical term

**Talk-to Skill**:
Either of the two model-invoked wording Skills in `schoolwork/`, namely `talk-to-middleschooler` and `talk-to-highschooler`. Each owns the language rules for one level and nothing else, with no persistence and no change to what work gets done. Model-invoked so any other Skill can borrow the voice, the way `grilling` is borrowed for interview mechanics.
_Avoid_: voice skill, tone skill, style guide

**eli Skill**:
Either of the two manual-invocation modes in `schoolwork/`: `eli5`, which pairs with `talk-to-middleschooler`, and `eli10`, which pairs with `talk-to-highschooler`. Each owns only persistence, staying on every turn, including inside Skills invoked later, until the user says "stop eli5", "stop eli10", or "normal mode". The rules live in the paired **Talk-to Skill**, never restated here.
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
- `implementation-plan-execute` is a single-mode driver Skill. Its **Phase loop** implements each phase inline, in the main thread, against the plan's `## Public interface`. It reads the **Bootstrap exploration sweep**'s **Exploration summary file** rather than re-reading source, follows **Point, don't paste** everywhere, and reports under **Terse verdicts**. Nothing is tested as a phase completes: the plan's mandatory `Phase N: Verification` is the only place tests run, and the only place a failure can occur, per the **Verification failure rule**. On a from-issue plan's Verification pass, Finalization closes the GitHub issue with `gh issue close` and marks the matching `(N.M)` **Task** ✅ in the **Project plan**. Both steps are best-effort and gated on the issue reference being present.
- A **Supervisor** running `implement-tdd` performs a **Runner preflight**, writes the red tests itself, dispatches one `claude` implementer per attempt against them, and dispatches one **Reviewer** once the tests pass. `implement-tdd` is the only Skill that dispatches an implementer.
- `project-planning` runs a **Git-repo guard** first, hard-stopping outside a git repo, then the **Adaptive grill**, which reads any existing `CONTEXT.md` and **Project plan** and asks only on gaps, then an epic-breakdown confirm gate, then writes `CONTEXT.md` and the **Project plan**. Every step is Opus-direct, with no subagent dispatch. The plan's Directory tree section is left at its placeholder; nothing populates it.
- `epic-planning` sits between `project-planning` and `implementation-planning` in the chain. It reads the **Project plan**, slices a chosen **Epic**'s goal into **Task** rows `(N.M)` appended to the plan, and creates or updates the epic's parent `(N)` GitHub issue. It does not call `new-issue`. A charted **Task** goes straight to `implementation-planning`.
- `new-issue` is **off the chain**, a standalone Skill for filing an issue that no **Epic** covers. It grills WHAT, meaning behavior, scope, and acceptance criteria, with no architecture or file paths, and publishes a GitHub Issue. Its multi-plan path publishes a parent Issue plus one **Sub-issue** per vertical slice, in dependency order, gated on the **two-tier coverage check**. An issue it produces can still be picked up by `implementation-planning`'s **From-issue path**, which is what the **WHAT / HOW split** exists for, though the normal route into a plan is a **Task** row, not an Issue.
- `course-index` and `lecture-notes` connect through the **Course index** file, not by invocation, the same artifact handoff the `kanban/` chain uses. Both are manual-invocation only, so neither pays context load, and both are bounded by the **Course folder**. `course-index` fast-exits on a SHA manifest at `.course-index/manifest.json` the way `generate-framework-tests` does, so re-runs read only added or changed PDFs. `lecture-notes` discloses its video branch to `transcript.md`, reached only when a lecture link is in play; that file owns the two-tier transcript route (yt-dlp captions, then `whisper.cpp` locally) and the rule that Swedish audio uses KB-Whisper while English uses stock `large-v3-turbo`.
- The `schoolwork/` wording family is off the chain and reads no repo artifact. It only rewrites how output is worded. Each **eli Skill** invokes exactly one **Talk-to Skill** for its rules; the pairing is the only place a level is defined twice, and it is defined once. A **Talk-to Skill** treats a project's `CONTEXT.md` as the sole evidence that a term is already known to the user; anything absent from it, and off the level's floor, is a **Naked term**.
- `add-comments` runs **ensure-convention** first, which locates or grills for a **Comment convention**, then **preview-walk**, its per-symbol approve loop. A missing language mid-walk triggers a **Scoped single-language grill** rather than the full grill.
- `generate-framework-tests` is the repo's only live testing Skill. It produces **Framework tests**, meaning real runnable code, that the project's own runner executes. It uses a **Sidecar manifest** to enable **Fast-exit** on re-invocation and **Drift-diff** on changed sources. **User-added-case immunity** is enforced via the manifest's `cases[]` list. The markdown-spec approach it replaced, `generate-test` and `run-tests`, is archived.

## Example dialogue

> **Me:** "Where should the implementation-plan template live?"
> **Claude:** "Inside the `implementation-planning` Skill, next to its `SKILL.md`. It's a Bundled file. Skills are self-contained, so the template travels with the Skill rather than living in a shared `~/.claude/templates/` directory."
