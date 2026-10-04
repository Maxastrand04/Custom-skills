---
name: unit-test-ticket
description: Headless refactor leg, second session, for kanban-ci. Folds the acceptance file into the unit suite and tidies the changed modules' tests, then hands off to review in a commit.
disable-model-invocation: true
---
<!-- synced-from kanban/unit-test-ticket/SKILL.md blob 86693d72fb62debd263fd050e148d4914731104a -->

# unit-test-ticket, headless

The second of the two sessions that make up the refactor leg of **red-green-refactor**. `refactor-ticket` settled the code: the acceptance tests are true to the ticket, the suite is green, and the refactor is committed. You **fold** and tidy tests under that green. The **acceptance file** is the one test file `architect-ticket` wrote for this ticket. To fold it, filter its tests through the Test rules, move each survivor into its module's test file, and delete it. A folded test is an ordinary unit test. It reads as if it had always lived in that file, and nothing in it points back at this ticket.

**You never edit code.** Every change you make is to a test file. A test that shows the code is wrong is a finding for the reviewer, not a fix.

## Running headless

The kanban-ci loop starts you with `claude -p`. Nobody reads this session and nobody answers. Never ask a question and never wait.

- **The invocation** carries the issue number and the base branch, as in `#42 base:main`. Under it the loop puts the **suite summary**, the result of the whole suite run right after `refactor-ticket`. Default the base to `main`.
- **The handoff to you** is the body of `HEAD`. Read it with `git log -1 --format=%B` before anything else. If the loop sent you back because the suite was red after your own handoff, the invocation says so; one of your test edits is wrong, so go to step 3.
- **Never run the whole suite.** The loop runs it after you. You run the module test files in scope and single tests.
- **Never push, open a PR, comment on the issue, or edit labels.** The loop owns GitHub.
- **You end with exactly one handoff commit**, described under Handoff. Then print the report and stop.

## 1. Pin the work and check the handoff

Take the current branch. Its name carries the issue number. Fetch the ticket with `gh issue view <number>`. If the invocation's number and the branch's disagree, hand off to `review` and name both.

The diff is `git diff <base>...HEAD`, three-dot, on that branch. Find the runner command.

Check all three, in order, and hand off on the first that fails:

- **Refactored.** `git log <base>..HEAD` has a commit whose subject starts `Refactor:`. If not, hand off to `refactor-ticket`.
- **Not yet folded.** The diff adds exactly one acceptance file. If it adds none, the fold already ran, so hand off to `review` and say so.
- **Green.** The suite summary says the whole suite passes. If it doesn't, hand off to `refactor-ticket` with the failing tests. If the summary is missing, as on a hand-started run, run the whole suite once yourself.

The **module scope** is every non-test source file the diff changes, plus each one's module test file.

The rules are the **Test rules** in `test-standards.md`, the file beside this `SKILL.md`. Read it from this skill's directory, never from the repo. A Project Convention Record (PCR) in `docs/pcr/` that covers tests, such as the runner or the layout, wins over any rule it contradicts.

## 2. Tidy and fold

1. **Filter the acceptance file.** Drop every tautological test. Rewrite a structure-sensitive test through the public interface when it is the only test of a behaviour, and drop it otherwise.
2. **Fold what survives.** Move each test into the test file for the module its entry point lives in, in that file's naming and fixture style, creating the module test file if none exists. Where an existing test already asserts the same thing, keep the acceptance version and drop the other. Delete the acceptance file.
3. **Tidy the module scope.** Delete every tautological test and fix every rule not marked report only. Design worsened for testability goes to the reviewer.
4. **Break check** every test this step wrote or rewrote.

**A new test that fails on the untouched code has found a bug.** Delete it from the branch, since the code is not yours to fix and a red suite can't merge. Log it for the reviewer with the assertion that failed. Behaviour that `too few tests` reports as undefined goes there too.

**Completion criterion:** the acceptance file is gone, and every test it held is either in a module test file exactly once or logged as dropped or rewritten. Every fixable rule is applied across the module scope, every test written or rewritten was observed red in its break check, and every bug-exposing test is logged for the reviewer.

## 3. Run

Run the module test files in scope. The code hasn't moved, so red means a test edit is wrong. Fix the test, never the code. Repeat until green.

---

## Handoff

One commit, the last you make, carrying both trailers. Use `git commit -F <file> --trailer "Handoff-From: unit-test-ticket" --trailer "Handoff-To: <next>"`, adding `--allow-empty` when there is nothing to stage.

**Done**, `Handoff-To: review`:

```
Tests #<N>: tidy and fold

<one line per acceptance test: its new file, or dropped, <kind>>
<one line per other rule fixed: test, rule, action>

For the reviewer
- <bug-exposing test: the behaviour, what it asserted, what the code did>
- <undefined behaviour, design worsened for testability>
```

Leave `For the reviewer` out when it would be empty.

**Back to refactor**, `Handoff-To: refactor-ticket`: subject `Tests #<N>: not ready to fold`, the check that failed and its evidence.

**Halted**, `Handoff-To: review`: subject `Tests #<N>: halted, <why in a few words>`, the evidence, and a `For the reviewer` section.

`For the reviewer` is a plain line followed by `- ` items and ended by a blank line. The loop collects these into the PR body, so each item must read on its own.

## Report

Print these lines and stop:

```
Commits  tests e3f4a5b
Tests    acceptance folded into tests/test_order.py, 2 dropped
Handoff  review, 1 item for the reviewer
```
