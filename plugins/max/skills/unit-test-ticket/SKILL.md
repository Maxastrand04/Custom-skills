---
name: unit-test-ticket
description: Refactor leg, second session. Folds the acceptance file into the unit suite and tidies the changed modules' tests against test-standards.md. Runs after refactor-ticket.
---

# unit-test-ticket

The second of the two sessions that make up the refactor leg of **red-green-refactor**. `refactor-ticket` settled the code: the acceptance tests are true to the ticket, the suite is green, and the refactor is committed. The **acceptance file** is the one test file `architect-ticket` wrote for this ticket. Under that green you fold it into the unit suite, then tidy the tests around it.

**Fold** means every acceptance test ends as an ordinary unit test or is gone. A folded test sits in the test file of the module it exercises, in that file's naming and fixture style, and nothing in it points back at this ticket: no ticket number, no acceptance wording, no fixture shared only with other acceptance tests. Before you place, name or keep an acceptance test, ask whether someone reading that module's tests could tell it came from this ticket. If they could, it is not folded.

**You never edit code.** Every change you make is to a test file. A test that shows the code is wrong is a finding for the reviewer, not a fix.

`test-standards.md` and `../pr-ticket/ticket-pr.md` resolve from this skill's directory. Never read a same-named file from the repo.

Word every halt, question, and report per the `gloss-me` skill.

## 1. Pin the work and check the handoff

The branch carries its **GitHub issue number** in the name. Take the current branch, or the one the user names, extract the number, and fetch the ticket with `gh issue view <number> --comments`, read as the current Spec in `../pr-ticket/ticket-pr.md`. If the name carries no number, ask the user which issue this is. Then open or reuse the branch's **ticket PR** per the same file.

The diff is `git diff main...HEAD`, three-dot, on that branch. Substitute the base the user names if it isn't `main`. Find the runner command for the whole suite.

Halt unless all three hold, naming the one that failed:

- **Refactored.** `git log main..HEAD` has a commit whose subject starts `Refactor:`. If not, say to run `$max:refactor-ticket` first.
- **Not yet folded.** The diff adds exactly one acceptance file. If it adds none, the fold already ran, so say so and stop.
- **Green.** The whole suite passes. If not, say `$max:refactor-ticket` left it red and hand the failing tests back.

The **module scope** is every non-test source file the diff changes, plus each one's module test file.

The rules are the **Test rules** in `test-standards.md`. A Project Convention Record (PCR) in `docs/pcr/` that covers tests, such as the runner or the layout, wins over any rule it contradicts.

## 2. Tidy and fold

1. **Filter the acceptance file.** Drop every tautological test. Rewrite a structure-sensitive test through the public interface when it is the only test of a behaviour, and drop it otherwise.
2. **Fold what survives.** Move each test into the test file for the module its entry point lives in, creating the module test file if none exists. Where an existing test already asserts the same thing, keep the acceptance version and drop the other. Delete the acceptance file.
3. **Tidy the module scope.** Apply every rule, and put each report-only hit in Found.
4. **Break check** every test this step wrote or rewrote.

**A new test that fails on the untouched code has found a bug.** Delete it from the branch, since a red suite can't merge. Record it in Found and in the PR comment at step 4, so the reviewer can decide whether it becomes a new ticket. Behaviour that `too few tests` reports as undefined goes to the same two places.

**Completion criterion:** the acceptance file is folded. It is gone, and every test it held is either in a module test file exactly once or a Tests row saying dropped or rewritten. Every fixable rule is applied across the module scope, every test written or rewritten was observed red in its break check, and every bug-exposing test is in Found.

## 3. Run and commit

Run the whole suite. The code hasn't moved, so red means a test edit is wrong. Fix the test. On green, commit as `Tests #<N>: tidy and fold`, then push with `git push`, so step 4's comment points at commits the ticket PR shows.

## 4. Comment on the ticket PR

`gh pr comment <PR>` with one line per acceptance test naming its new file, or `dropped, <kind>`.

If Found holds a bug-exposing test or undefined behaviour, add a `For the reviewer` heading under those lines, with one line per item: the behaviour, what the test asserted, and what the code did.

Never close the issue. Merging the branch closes it.

## 5. Report

Two tables.

- **Findings only.** No hit, no row. Never narrate what you checked, never wrap a table in prose.
- **Empty collapses.** A table with no rows becomes one line, `**Found, not fixed** none`. Nothing follows it.
- **Cap every cell.** Middle column 6 words, last column 8. No sentences, no trailing periods. Truncate a deep path from the left, `.../tests/test_order.py:30`.

**Tests**

| Test | Rule | Action |
|---|---|---|
| `test_order.py:30` | too many assertions | split into 5 |
| `test_total_nonneg` | tautological | dropped |
| `test_discount_rate` | folded | moved to `tests/test_pricing.py` |

**Found, not fixed**

| File | Issue | Why |
|---|---|---|
| `src/cart.ts:12` | design worsened for testability | report only |
| `src/tax.ts:31` | negative total accepted | bug, test deleted, on PR |

Close with four lines. Nothing follows them except `gloss-me`'s footer. A new term in a table gets its gloss in a `gloss-me` block before that table.

```
Commits  tests e3f4a5b, pushed
Tests    suite green, acceptance folded into tests/test_order.py, 2 dropped
PR       commented #57, 1 item for the reviewer
Next     $max:pr-ticket pushes and marks the ticket PR ready
```
