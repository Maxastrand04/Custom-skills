---
name: implement-ticket
description: Fills in the stub bodies on a red branch until every acceptance test passes, then closes the issue and commits.
disable-model-invocation: true
---

# implement-ticket

You are the **green** leg of red-green-refactor. `architect-ticket` committed the public interface as stubs and the acceptance tests that fail against them, leaving the branch **red**. You fill in the bodies until every test passes.

**Two things on that diff are frozen: the signatures and the tests.** Never rename a parameter, change a return type, loosen an assertion, or delete a test to get green. Both were settled with the user, and quietly editing either turns a passing suite into a lie.

**Behind the signatures you have full freedom.** No implementation choice needs approval. `refactor-ticket` refactors what's inside the boundary afterwards, so don't polish here and don't ask permission.

---

## Pin the work

1. **The branch.** Take the current branch, or the one the user names. Its name carries the issue number, as in `42-oauth-admin-login`. If the branch name has no number, ask which issue this implements before reading anything.
2. **The ticket.** `gh issue view <number> --json title,body`. Read Goal, Expected behaviour, and Out of scope. This is the *why*, and it is what tells you whether a green test actually shipped the feature.
3. **The diff.** `git diff main...HEAD`, three-dot, against the merge-base. Substitute the base the user names if it isn't `main`. This is the *what*.

Confirm the branch and issue with the user in one line before writing code.

### Precondition

The diff must carry both interface stubs and failing tests. If it carries tests but no stubs, or stubs but no tests, or is empty, halt:

> This branch isn't red. `implement-ticket` starts from a committed interface plus failing acceptance tests. Run `/architect-ticket <issue>` first.

Then run the tests the diff added, once, and confirm they fail. A branch that is already green has nothing to implement, and a test that **errors** rather than fails points at a missing dependency the architect should have caught. Either way, stop and say what you saw.

---

## Read the diff as the spec

Read it once, in full, before writing anything. Three things come out of it, and nothing else should:

- **The stubs.** Every signature and docstring. The docstring is the contract: the errors it names, the invariants it promises, the edge cases it describes. All of that is work you owe, whether or not a test covers it.
- **The tests.** Each test's name and docstring is one acceptance criterion. The assertions are the exact bar.
- **The surrounding code.** Read the region you're about to change, not the whole file. Grep to locate, then read with an offset and a limit.

**Point, don't paste.** Never paste the stubs, the tests, or the ticket body back into your own response. You already read them.

---

## The green loop

1. **Implement.** Fill in the stub bodies, plus whatever private code they need.
2. **Run the tests the diff added.** Not the whole suite. The rest of the suite covers code you haven't touched, and re-proving it buys nothing.
3. **Read every failure before fixing any of them.** Failures surface as a set, so one pass can answer all of them. Fixing one at a time invites a fix that breaks a sibling.
4. **Repeat until green.**

**Track the pass number and report it**, as in "pass 3: 2 of 6 still red", so a loop that isn't converging shows itself.

**Terse verdicts only.** One line per pass. The edit itself is the record, so name the files touched and move on.

Once every added test is green, run the **neighbouring tests**: the existing tests that reach the files you changed. Grep the test tree for each changed file's import path, module name, and exported symbols. A regression here is yours to fix, not `refactor-ticket`'s to find.

**Completion criterion:** every test the diff added passes, every neighbouring test still passes, and no signature or assertion on the diff was edited.

### Loop exits

Four things stop the loop and go to the user, because none is yours to fix:

- **The contract is wrong.** A signature can't express the behaviour, or two parts of it contradict each other. Say which stub and why. Do not fix it in code.
- **A test is wrong.** It asserts something the ticket never asked for, or contradicts the docstring it sits under. Say which test and quote the conflict. Do not weaken it.
- **No progress.** The same test fails with the same evidence two passes running. A third would spin.
- **An ADR blocks the implementation.** Changing one takes a full `/challenge-adr` session, which is the user's to run, never yours and never inline. Name the ADR and what it blocks. Do not code around it.

On any exit, describe the failure in plain English: which test, the evidence, and your best guess at the cause, stated as a guess. Then ask what should happen next and offer the real options: a hint from them, a contract amendment back through `/architect-ticket`, a `/challenge-adr` session, or stopping here.

**A hard-to-reverse decision you had to weigh** is worth an ADR, but you don't write one mid-loop.

---

## Finalization

Bookkeeping, once the suite is green. It runs no tests. In order:

1. **Comment on the issue** with `gh issue comment <N>`: the branch name, and one line per acceptance test naming it and confirming it green. Then `gh issue close <N>`.
2. **Commit** on the branch, as a separate commit from the architect's.

   ```
   Implement #<N>: <ticket title>

   Green.
   Issue: #<N>
   ```

   Don't push unless the user asks.

## Report

Close with these lines, then the two notes below and nothing else:

```
Tests     6 added green, 4 neighbouring green
Files     src/auth/oauth.py, src/auth/session.py
Issue     closed #42
Commit    d4e5f6a
```

Then say `/refactor-ticket` refactors the branch under the green suite. Raise any weighed decision worth an ADR here, in one line, and let the user decide whether it earns one.
