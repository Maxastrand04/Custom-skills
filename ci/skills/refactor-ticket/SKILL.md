---
name: refactor-ticket
description: Headless refactor leg, first session, for kanban-ci. Gates the green branch true-to-spec, reconciles the suite from the loop's summary, settles visibility itself, refactors, and hands off to unit-test-ticket in a commit.
disable-model-invocation: true
---
<!-- synced-from kanban/refactor-ticket/SKILL.md blob 6fd723d108134d2ec4c7c2257160beec3c051aff -->

# refactor-ticket, headless

The first of the two sessions that make up the refactor leg of **red-green-refactor**. The branch is **green** against its **acceptance file**, the one test file `architect-ticket` wrote for this ticket, and you refactor under that green. You own the code. `unit-test-ticket`, the second session, folds the acceptance file into the unit suite and tidies the tests.

**Refactor** means the behaviour is already right and only the shape changes. Before any edit, ask whether a caller would see a difference. If one would, it is not a refactor. Steps 1 to 4 make the branch safe to refactor, step 5 is the refactor, and the rest records it.

`code-standards.md`, `test-standards.md` and `RECORD-FORMAT.md` resolve from this skill's directory, `test-standards.md` from `../unit-test-ticket/`. Never read a same-named file from the repo.

## Running headless

The kanban-ci loop starts you with `claude -p`. Nobody reads this session and nobody answers. Never ask a question and never wait. Every place the interactive version asks the user, this file says what you decide or where you hand off.

- **The invocation** carries the issue number and the base branch, as in `#42 base:main`. Under it the loop puts the **suite summary**, the result of the whole suite run right after the previous station. Default the base to `main`.
- **The handoff to you** is the body of `HEAD`, the commit whose `Handoff-To` trailer names you. Read it with `git log -1 --format=%B` before anything else. If the loop sent you back because the suite was red after your own handoff, the invocation says so; treat those failures as your edit changing behaviour, and go to step 7.
- **Never run the whole suite.** The loop runs it after you. You run only the narrow sets named in each step.
- **Never push, open a PR, comment on the issue, or edit labels.** The loop owns GitHub.
- **Log every call you made in the user's place** under `For the reviewer` in the handoff commit. The reviewer can only overrule what they can see.
- **You end with exactly one handoff commit**, described under Handoff. Then print the report and stop.

## 1. Pin the work and the diff

Take the current branch. Its name carries the issue number. Fetch the ticket with `gh issue view <number>`. If the invocation's number and the branch's disagree, hand off to `review` and name both.

**The spec is two things.** The ticket's **Expected behaviour** is the user-visible bar. The **acceptance file** is the exact bar. Each test's name and docstring is one criterion. Step 2 asks whether the second is true to the first.

The diff is `git diff <base>...HEAD`, three-dot, against the merge-base. Confirm the diff is non-empty and adds exactly one acceptance file. If either fails, hand off to `review` and name it. Find the runner command, since you will run named test files and single tests with it.

The **module scope** is every non-test source file the diff changes, plus each one's module test file. Step 4 works inside it, and so does `unit-test-ticket`.

**Completion criterion:** ticket fetched, both checks pass, runner command found, module scope listed.

## 2. True-to-spec

**Make no edits while you read.** Work through the ticket's expected behaviour one item at a time:

- **Is a test true to it?** Find the acceptance test covering it. A test that asserts something weaker, stubs out the behaviour it should exercise, or is a **tautological test** per `test-standards.md` is not true to spec, green or not. A tautological test is a finding here only when it is the behaviour's sole cover. The rest are `unit-test-ticket`'s to delete.
- **Is it covered at all?** A behaviour the ticket asked for with no test behind it is the worst finding here, because a green suite says otherwise.
- **Does the diff meet it?** Where no test can reach the behaviour, read the code against the ticket directly.
- **Did anything arrive the ticket never asked for?** Check it against Out of scope. Scope creep is a spec finding too.

**Completion criterion:** every expected behaviour in the ticket accounted for, each one either true-to-spec or a named finding.

Zero findings means the spec is settled, so go to step 3.

### Spec findings

Fix the acceptance **tests** so they're true to the ticket. Only the tests. The ticket body is the single source of truth and is never edited here, and neither is a signature already settled on the branch. Scope creep and a diff that misses a behaviour no test can reach are not test fixes; log them for the reviewer and carry on.

Then run the acceptance file:

- **Still green.** The implementation was right and the test was merely thin. Commit the test fixes as `Tests #<N>: true to spec`, log each one for the reviewer, and continue to step 3.
- **Now red.** The weak test was hiding a real gap, and a red branch is not yours to refactor. Commit the fixed tests as the handoff commit with `Handoff-To: implement-ticket`. The note names each failing test and the behaviour it now pins.

## 3. Reconcile the suite

Read the suite summary in the invocation. `implement-ticket` ran only the acceptance file, so this is the first time the ticket met every test written before it. If the summary is missing, as on a hand-started run, run the whole suite once yourself.

Every red test outside the acceptance file is one of two things, and the acceptance file tells them apart:

- **Stale.** An acceptance test asserts the contrary. **The newest requirement is the truth**, so rewrite the old test to it, or delete it where the acceptance test now covers the same thing.
- **A regression.** No acceptance test contradicts it, so the ticket never asked for this behaviour to change and the implementer broke it. Fix it inline when the fix stays behind the settled interface, no signature touched. A regression fix is not a refactor, so commit it on its own as `Fix #<N>: <what broke>`. When the fix would need a signature change or a behaviour the ticket doesn't cover, it is a contract problem. Commit what you have and hand off to `review`, naming the test and the signature.

Then run every test file that was red, plus the acceptance file. Not the whole suite.

**Completion criterion:** every test that was red is green, and each has a Reconciled line naming it stale or a regression.

## 4. Visibility, decided

The interactive version asks the user about every visibility question here. You decide them, the same way the interactive version would recommend, and the reviewer sees each call. The definitions are `code-standards.md`'s **Leaky public interface** entry and the **Test rules** in `test-standards.md`.

List, across the module scope:

- every function Leaky public interface escalates,
- every test that calls a private function or reads a private field, counting helpers step 5 is about to make private,
- every other structure-sensitive test.

Decide each one. A function goes public or private on the reason Leaky public interface gives. A test is **deleted** by default, because a helper has no contract of its own. **Rewrite** it through the public interface only when deleting would leave a behaviour a caller can see untested, and **keep** it only when you ruled its function public.

Apply every test change, break check each rewrite per `test-standards.md`, and run the module test files in scope plus the acceptance file. No code has moved since step 3, so red means a rewrite is wrong or found a real bug. Fix a wrong rewrite. A real bug is the reviewer's: delete the rewrite, log the bug, and carry on. On green, commit as `Tests #<N>: visibility`.

Log every decision for the reviewer as `<item>: <public|private|deleted|rewritten|kept>, <reason>`. The interactive version gave these to the user before acting, so they are the calls most likely to be overruled.

**Completion criterion:** every listed item decided and logged, every rewrite observed red in its break check, the narrow run green, one commit. Or nothing was listed.

## 5. Refactor

Edit the code directly.

Three tiers, read per `RECORD-FORMAT.md`:

1. **PCRs in `docs/pcr/`** hold the project conventions. A breach is a **hard violation**. Fix the code and never touch the file. A PCR you disagree with is not a finding. It binds until a `/challenge-pcr` session says otherwise, so fix the code to comply and log one line for the reviewer.
2. **ADRs in `docs/adr/`** hold the design decisions. A breach is a hard violation too. Fix it. Nothing pre-selects them, so take the whole set and judge yourself which the changed files fall under. Read each one's **Decision** for what's required and its **Consequence** for what a breach looks like in a diff.
   - **Amend an ADR only when it contradicts a signature already settled on this branch.** The architect settled that signature with the user and it is frozen, so the record is what moves. Amend it per the format file and log it for the reviewer. Any other disagreement with an ADR is fixed in the code.
   - **Write a new ADR when the diff introduces a shape neighbouring code will copy** and no record names it: a new layer, a new kind of module, a dependency direction the first of its kind establishes. Run it through the ADR tests in the format file. Most refactors write none. Log every ADR you write for the reviewer.
   - If the diff itself adds a file under `docs/adr/` or `docs/pcr/`, it is the architect's and you leave it alone.
   - If neither directory exists, this step runs on the baseline alone.
3. **The baseline in `code-standards.md`** applies everywhere no record covers. It carries its own gates for deciding which entries a given codebase has, and applying them is yours.

Two standing rules, over all three tiers:

- **Tests are frozen.** Step 4 already settled the tests this step's visibility changes would break, and `unit-test-ticket` handles every other test change. Never edit a test from here on.
- **A refactor never changes behaviour.** If a caller would see the difference, it is not a refactor. Leave the code alone and log it for the reviewer as found, not fixed.

**Completion criterion:** every changed non-test file has been read against the whole `docs/pcr/` and `docs/adr/` sets and every applicable entry in `code-standards.md`, and each finding is either fixed or logged as a deliberate non-fix with a reason.

## 6. Update the docs

1. **`CONTEXT.md`** at the project root, if it exists. Skip if not, and never create one. Revise the Language and Relationships entries where the branch introduced or shifted a domain term.
2. **`README.md`** only if the branch alters something a new contributor needs to run or use the project: a new entry point, a new install or run command, changed configuration. Skip internal-only changes and invent nothing.

Judge both against the whole branch diff, not just your refactor edits.

## 7. Re-run and hand off

Run the acceptance file, the module test files in scope, and every test file that imports a file you changed. Grep the test tree for each changed file's import path to find them. Not the whole suite.

- **All green.** Commit the refactor, the docs, and any record together as the handoff commit, `Handoff-To: unit-test-ticket`.
- **Back to red.** The break is yours, and code that turned a test red was not a refactor. Fix or revert it, then re-run.

---

## Handoff

One commit, the last you make, carrying both trailers. Use `git commit -F <file> --trailer "Handoff-From: refactor-ticket" --trailer "Handoff-To: <next>"`, adding `--allow-empty` when there is nothing to stage. Where the exit falls after other commits, the earlier commits keep their own subjects and only the last one carries trailers.

**Done**, `Handoff-To: unit-test-ticket`:

```
Refactor: <ticket title>

<one line per finding fixed: file, record or smell, fix>
Docs: <CONTEXT.md updated|unchanged>, <README.md updated|unchanged>

<note for unit-test-ticket: the module scope, and any test you saw that
breaks a Test rule>

For the reviewer
- <every spec fix, Reconciled line, visibility decision, ADR written or
  amended, PCR complied with under protest, and found-not-fixed item>
```

An amended ADR adds one line under the body, `Amends ADR-0003: <why, one line>`, since the file carries no history.

**Back to implement**, `Handoff-To: implement-ticket`: subject `Tests #<N>: true to spec, red`, the failing tests and the behaviour each pins.

**Halted**, `Handoff-To: review`: subject `Refactor #<N>: halted, <why in a few words>`, the evidence, and a `For the reviewer` section naming the decision a human has to make.

`For the reviewer` is a plain line followed by `- ` items and ended by a blank line. The loop collects these into the PR body, so each item must read on its own.

## Report

Print these lines and stop:

```
Changes  7 across 4 files
Records  ADR-0009 written, ADR-0003 amended
Docs     CONTEXT.md updated, README.md unchanged
Commits  fix b0c1d2e, visibility c9d8e7f, refactor a1b2c3d
Handoff  unit-test-ticket
```
