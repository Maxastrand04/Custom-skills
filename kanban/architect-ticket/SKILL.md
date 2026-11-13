---
name: architect-ticket
description: Third station, the red leg of red-green-refactor. Turns a ticket into a branch of interface stubs and failing acceptance tests, committed and pushed once you approve the diff.
disable-model-invocation: true
---

# architect-ticket

You are the **red** leg of red-green-refactor, and you turn a ticket into a **red branch**: the public interface written as stubs in the real source files, the acceptance tests written against those stubs, every test failing, committed once the user approves the diff.

That commit is the whole handoff. `implement-ticket` takes it **green** and `refactor-ticket` refactors under that green. The implementer reads the issue and this diff and needs nothing else.

**The user owns the contract; the implementer owns everything behind it.** You settle the names, parameters, return values, and documented behaviour of every entry point the change adds or alters.

**The tests are the acceptance criteria.** The ticket's Behaviour lines are the bar; you convert them into named test functions. Never write an AC list beside the tests it duplicates.

**They all land in one acceptance file.** One new file at the root of the test tree, named in the project's style, `tests/test_acceptance.py` or `tests/acceptance.test.ts`, holding this ticket's tests and nothing else. It lives only on this branch; `unit-test-ticket` folds it into the module test files before the branch merges.

---

## Phase 1: Setup

### Resolve the ticket

This skill starts from a ticket. Resolve one of:

1. **An explicit reference** in the invocation, meaning `42`, `#42`, a GitHub issue URL, or a description of an existing issue. Resolve URLs and descriptions to the number with `gh issue list` and `gh issue view`.
2. **A ticket published in this session** by `new-ticket` or `map-epic`. Confirm with the user before adopting it.
3. **Neither.** Ask which issue this is, and point at `/new-ticket` if none exists. Do not architect from a conversation.

Then read the ticket in full with `gh issue view <ref> --comments`, read as the current Spec per `../pr-ticket/ticket-pr.md`. Take **Goal**, **Spec**, and **Out of scope** as given. Spec's **Interface** lines name the pieces without naming them in code, and its **Behaviour** lines trace the flow between them. Naming those pieces is this session's work.

Pick the **branch name**, which is `<issue-number>-<slug>`. Take the slug from the ticket's `## Branch` section when it has one. Otherwise derive it from the title: 2 to 4 words, kebab-case, no articles, no issue number.

### Exploration, runs before any question

1. **Project-level reads**, where present: `CONTEXT.md`, top-level `README.md`, the project root listing, and every file in `docs/pcr/` and `docs/adr/`.
2. **Change-specific reads.** Grep and read the modules the change will touch, their neighbours, and the **existing public interface** the new one sits beside: signatures, naming, error types, module layout.
3. **The test tree.** Find where tests live, how they are named, what fixtures and factories exist, and the runner command. You are about to write tests here, so their shape has to match.

Emit a short **"What I found"** summary covering the relevant modules, the conventions in the affected area, the interface the change plugs into, and the runner command. **Wait for the user to correct misreads.**

### Branch and ticket PR

`git checkout -b <issue-number>-<slug>`, or `git checkout` it if it already exists. If the working tree carries unrelated uncommitted changes, surface that before switching rather than dragging them across.

Then open or reuse the branch's **ticket PR** per `../pr-ticket/ticket-pr.md`, before writing any file.

---

## Phase 2: Grill the interface

You are a developer grilling a project leader about code structure. Invoke the `grilling` skill for how to ask a question and give a recommendation.

**No code in chat.** No signatures, no snippets, no calls, no test names. The code goes into the source files, where the user reads it in their own editor. Chat names things and argues for them. Write all chat output per the `unslop` skill when it is installed.

### Questions before code

Some decisions have to come before any code can exist: whether the change belongs in this repo at all, a Behaviour line ambiguous enough that two readings need different interfaces, a PCR or ADR in the way. Ask these first, as one round in `grilling`'s format. With none, go straight to the stub loop.

**Record conflicts.** State a PCR or ADR in the way in two lines, then ask the decision like any other question. Give no reasons or consequences, since the record holds them.

```
ADR-0003 says: tokens never leave `auth/`.
The ticket wants: the admin panel reads the token directly.
```

- **A PCR is not yours to override.** The user either accepts a different interface or stops to run `/challenge-pcr` as its own session. Do not design against a convention you expect to fall.
- **An ADR is yours to argue.** Settle with the user whether the interface bends to the ADR or the ADR is amended. An amendment is written with the records in Phase 3. Until it is settled the ADR binds.

### The stub loop

Settle the interface one entry point at a time, in the order the ticket's flow reaches them. Start with the entry point the ticket's trigger calls first, then follow the Behaviour steps.

**1. Write it.** Write the entry point into its real source file, complete:

- **Name**, in the naming style Exploration found.
- **Parameters**, each with its type, whether it's required, and its default.
- **Return value**, its type and what it means to the caller.
- **Guarantees** in the docstring: errors raised and when, edge-case behaviour, invariants, side effects.
- **A body** that raises the language's not-implemented error, and nothing else.

A parameter with no type, a return described only as "the result", or an error path nobody named is not done yet. Create a file only when the interface needs a new one, and prefer the module the surrounding interface already lives in. Write nothing behind the contract: no helpers, no control flow, no data structures.

**2. Defend it.** A few lines of plain prose saying why this shape fits what already exists. Name the entry point and its file so the user can open it. When you weighed a real contender, name it and say in one short line why it lost. No headers, no labels, no template.

**3. Wait.** The user's reply decides what comes next:

- **A question or a suggested edit** keeps you on this entry point. Edit the file, defend again, and wait.
- **An approval**, such as "ok", "approved", "confirmed" or "settled", settles it. Move to the next entry point.

Rules for the loop:

- **Grill the interface, not the implementation.** "One function or a class with three methods?" is the contract. "A dict or an LRU cache for the tokens?" sits behind the contract, so don't spend the user's attention on it.
- **A settled entry point can still be wrong.** When a later one shows it, say so, edit the earlier one, and settle it with the user before going on.
- **Keep the ticket true.** When the code shows a Spec line is wrong, amend it per `../pr-ticket/ticket-pr.md` before going on. Never depart from the ticket silently.
- **Mark every argument.** When an entry point settles *against* a named contender, note it to yourself in one line as a **record candidate**. These are what Phase 3 writes. An entry point the user approved without a contest is not a candidate.

The loop ends when every Interface line in the ticket has at least one settled entry point. Then say:

> "Interface settled. Writing the tests now."

and go on without waiting to be prompted.

---

## Phase 3: Write the red branch

### 1. Tests

Write every acceptance test into the acceptance file in one pass, without asking the user to approve names or a list. Call the code **only through the stubs as written**.

Every Behaviour line is covered by at least one test. Interface lines become stubs, never tests. A flow step that only sets up the next one, such as "the player clicks", is covered by the test of the step it leads to. Then sweep for what the ticket didn't say:

- **Edge cases and failure modes** the contract names. Every error in a docstring earns a test.
- **Boundary values.** Empty, missing, zero, duplicate, and conflicting inputs.
- **Behaviour this change must not break**, wherever it extends something that already ships.

**One behaviour per test.** A test asserting three things fails ambiguously, and the implementer reads a failure as an instruction. Split it. Each test's docstring states the behaviour it enforces, in one sentence.

**Never write a structure-sensitive test**, as `../unit-test-ticket/test-standards.md` defines it.

Two things stop the pass:

- **A Behaviour line no settled stub reaches.** Stop, go back to the stub loop to reopen or add that entry point, settle it with the user, then finish the tests.
- **A Behaviour line two readings would test differently.** Ask that one line in prose, in `grilling`'s format, then carry on. Never write a test from a guess.

**State plainly to the user any behaviour no automated test can reach.** It is a manual check, not a test. Don't fake one.

### 2. Go red

Run the tests. Every one must **fail because the behaviour doesn't exist yet**.

Two ways this goes wrong, and both mean you are not done:

- **A test passes.** It asserts nothing real, or the behaviour already ships. Sharpen it, or take it to the user if the ticket asked for something already built.
- **A test errors** on a typo, a bad import, a missing fixture, or a missing module. That is broken, not red. Fix a typo yourself, but **halt on an absent dependency** and take it to the user, because building it is separate work and is theirs to schedule.

What the test run can't reach is external: a credential, a running service, a created bucket or queue. Name those to the user in one line if the contract needs any.

**Completion criterion:** every Behaviour line covered by a test, every error the contract names tested, and every test observed failing for the right reason. Not "should fail". Observed.

### 3. Records

Read `RECORD-FORMAT.md`, the file beside this `SKILL.md`, and run every record candidate from the stub loop through its ADR tests. Write one ADR per candidate that passes, taking the next free number, and drop the rest without comment. A ticket whose grill argued nothing writes nothing, and that is the common case.

Write any **amendments** settled in Phase 2 the way that file describes.

Write a **PCR** only when this ticket is the first to settle something project-wide.

Write without asking; the user reads the Decision line at the diff gate like everything else.

### 4. The diff gate

Leave the stubs, the acceptance file, and any record on disk, **unstaged**, and **stop**. This is the session's only commit gate. The user reads the changes in their own editor, so never paste the diff or any file into chat.

Post four lines, plus any manual checks or external resources the user still owns:

```
Branch    42-oauth-admin-login
Stubs     src/auth/oauth.py, src/auth/session.py
Tests     tests/test_acceptance.py, 6 written, 6 red
Records   ADR-0007 written, ADR-0003 amended
```

The Records line reads `none` when nothing was written. End with one line saying the changes are on disk, unstaged, for the user to read before approving.

**Do not stage, commit, or push until the user approves.**

Corrections come in two kinds:

- **A fix inside the contract**, meaning a name, a type, a missing test, a wrong assertion. Edit the working tree, re-run the tests, then post the four lines again plus one line per file you changed, such as `Edited    tests/test_acceptance.py`.
- **A change to the contract itself**, meaning the contract drawn in the wrong place, an entry point that shouldn't exist, a behaviour no signature can reach. **Return to the stub loop** for the entry points it touches and settle them again. Code already on disk is not evidence the shape was right. Never patch a stub to absorb an objection that is really about the design.

If the user abandons the session, this session has staged and committed nothing, apart from the empty start commit `../pr-ticket/ticket-pr.md` makes when it opens a PR on a branch with no commits. When this session opened the ticket PR, `gh pr close <PR> --delete-branch`, then `git checkout <previous-branch> && git branch -D <branch>` drops the branch. Your edits stay in the working tree, so list them with `git status --short` and let the user say what goes.

### 5. Commit

On approval, `git add` exactly the files you wrote or edited this session, each by path. Never `git add -A` or `git add .`, since the user may have unrelated edits open in their editor, and a blanket add sweeps them into the red commit. Then commit on the branch.

```
Architect #<N>: <ticket title>

Interface and acceptance tests. Red.
Issue: #<N>
```

An amended ADR adds one line per amendment under the body, `Amends ADR-0003: <why, one line>`, since the file itself carries no history.

Then push with `git push -u origin <branch>`, and post one line on the ticket PR with `gh pr comment <PR>`: `Red at <short hash>, <count> acceptance tests failing in <acceptance file>`.

### 6. Confirm

Two lines, `Commit    a1b2c3d` and `PR        <ticket PR URL>`, then say that `/implement-ticket` takes it green.
