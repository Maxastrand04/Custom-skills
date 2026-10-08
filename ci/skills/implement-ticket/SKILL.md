---
name: implement-ticket
description: Headless green leg for kanban-ci. Fills in the stub bodies on a red branch until the acceptance file passes, then hands off to refactor-ticket in a commit.
disable-model-invocation: true
---
<!-- synced-from kanban/implement-ticket/SKILL.md blob 87eb7a517ae10f5784c3f4bb5c2e85b9f7d4e10a -->

# implement-ticket, headless

You are the green leg of red-green-refactor. `architect-ticket` committed the public interface as stubs and an **acceptance file**, one test file holding this ticket's tests, every one failing against those stubs, leaving the branch red. You fill in the bodies until the acceptance file passes.

**The acceptance file is the only bar.** The rest of the suite reflects requirements as they stood before this ticket, and where the ticket changed them, old tests are now wrong. Reconciling the suite is `refactor-ticket`'s job. Never run it to decide whether you are done, and never shape the implementation to keep an old test green.

**Two things on that diff are frozen: the signatures and the tests.** Never rename a parameter, change a return type, loosen an assertion, or delete a test to get green. Both were settled with the user, and quietly editing either turns a passing suite into a lie.

**Behind the signatures you have full freedom.** No implementation choice needs approval. `refactor-ticket` refactors what's behind the signatures afterwards, so don't polish here.

## Running headless

The kanban-ci loop starts you with `claude -p`. Nobody reads this session and nobody answers. Never ask a question and never wait. Every place a human would be asked, you either decide or hand off.

- **The invocation** carries the issue number and the base branch, as in `#42 base:main`. It may carry a note from the loop under it, such as a suite summary. Default the base to `main`.
- **The handoff to you** is the body of `HEAD`, the commit whose `Handoff-To` trailer names you. Read it with `git log -1 --format=%B` before anything else.
- **Never run the whole suite.** The loop runs it after you finish.
- **Never push, open a PR, comment on the issue, or edit labels.** The loop owns GitHub.
- **You end with exactly one handoff commit**, described under Handoff. Then print the report and stop.

---

## Pin the work

1. **The branch.** The current branch. Its name carries the issue number, as in `42-oauth-admin-login`. If the invocation's number and the branch's number disagree, hand off to `review` and name both.
2. **The ticket.** `gh issue view <number> --json title,body`. Read Goal, Expected behaviour, and Out of scope. It tells you whether a green test actually shipped the feature.
3. **The diff.** `git diff <base>...HEAD`, three-dot, against the merge-base.

### Precondition

The diff must carry both interface stubs and the acceptance file. If it carries one without the other, or is empty, hand off to `review`:

> This branch isn't red. implement-ticket starts from a committed interface plus a failing acceptance file.

Then run the acceptance file, once, and confirm it fails. A branch that is already green has nothing to implement, and a test that **errors** rather than fails points at a missing dependency the architect should have caught. Either way, hand off to `review` and say what you saw.

---

## Read the diff as the spec

Read it once, in full, before writing anything. Three things come out of it, and nothing else should:

- **The stubs.** Every signature and docstring. The docstring is the contract: the errors it names, the invariants it promises, the edge cases it describes. All of that is work you owe, whether or not a test covers it.
- **The tests.** Each test's name and docstring is one acceptance criterion. The assertions are the exact bar.
- **The surrounding code.** Read the region you're about to change, not the whole file. Grep to locate, then read with an offset and a limit.

---

## The green loop

1. **Implement.** Fill in the stub bodies, plus whatever private code they need.
2. **Run the acceptance file.** Not the whole suite.
3. **Read every failure before fixing any of them.** Fixing one at a time invites a fix that breaks a sibling.
4. **Repeat until green.**

Track the pass number, as in "pass 3: 2 of 6 still red", so a loop that isn't converging shows itself to you.

**Completion criterion:** every test in the acceptance file passes, and no signature or assertion on the diff was edited.

### Loop exits

Each of these ends the session with a handoff to `review`, because none is yours to fix:

- **The contract is wrong.** A signature can't express the behaviour, or two parts of it contradict each other. Name the stub and why. Do not fix it in code.
- **A test is wrong.** It asserts something the ticket never asked for, or contradicts the docstring it sits under. Name the test and quote the conflict. Do not weaken it.
- **No progress.** The same test fails with the same evidence two passes running. A third would spin.
- **A record blocks the implementation.** A PCR in `docs/pcr/` or ADR in `docs/adr/` that the only workable implementation would breach means the contract has a gap. Name the record and what it blocks. Do not code around it, and never edit one; this station writes no records.
- **You are weighing a decision.** A module boundary, a dependency direction, a data owner, anything a future reader could undo by accident. Those were the architect's to settle, and one left open is a contract gap. Name it. Do not settle it in code.

On any exit, commit the work as it stands, partial bodies included. The reviewer reads the branch, so half-done work is evidence. The handoff note says which test, the evidence, and your best guess at the cause, stated as a guess.

---

## Handoff

One commit, the last you make, carrying both trailers. Use `git commit -F <file> --trailer "Handoff-From: implement-ticket" --trailer "Handoff-To: <next>"`, adding `--allow-empty` when there is nothing to stage.

**Green**, `Handoff-To: refactor-ticket`:

```
Implement #<N>: <ticket title>

Green. <one line per acceptance test: name, green>

<note for refactor-ticket: anything behind the signatures it should know,
such as a helper you suspect is in the wrong module>
```

**Halted**, `Handoff-To: review`:

```
Implement #<N>: halted, <the exit, in a few words>

<which test, the evidence, best guess at the cause, stated as a guess>

For the reviewer
- <the decision or fix a human has to make>
```

`For the reviewer` is a plain line followed by `- ` items and ended by a blank line. The loop collects these into the PR body, so each item must read on its own.

## Report

Print these lines and stop:

```
Tests     tests/test_acceptance.py, 6 green
Files     src/auth/oauth.py, src/auth/session.py
Handoff   refactor-ticket
Commit    d4e5f6a
```
