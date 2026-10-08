---
name: refactor-ticket
description: Refactor leg, first session. Gates the green ticket branch true-to-spec, reconciles the suite, and refactors the code under it. unit-test-ticket runs after it.
disable-model-invocation: true
---

# refactor-ticket

The first of the two sessions that make up the refactor leg of **red-green-refactor**. The branch is **green** against its **acceptance file**, the one test file `architect-ticket` wrote for this ticket, and you refactor under that green. You own the code. `unit-test-ticket`, the second session, folds the acceptance file into the unit suite and tidies the tests.

**Refactor** means the behaviour is already right and only the shape changes. Before any edit, ask whether a caller would see a difference. If one would, it is not a refactor. Steps 1 to 4 make the branch safe to refactor, step 5 is the refactor, and the rest records it. Wherever a step names no stop for the user, decide and act.

`code-standards.md`, `../unit-test-ticket/test-standards.md` and `../architect-ticket/RECORD-FORMAT.md` resolve from this skill's directory. Never read a same-named file from the repo.

Word every question and report per the `gloss-me` skill.

## 1. Pin the work and the diff

The branch carries its GitHub issue number in the name, following the branch-naming convention every ticket publishes. Take the current branch, or the one the user names, extract the number, and fetch the ticket with `gh issue view <number>`.

**The spec is two things.** The ticket's **Expected behaviour** is the user-visible bar. The **acceptance file** is the exact bar. Each test's name and docstring is one criterion. Step 2 asks whether the second is true to the first.

- If the branch name carries no issue number, the convention was skipped. Ask the user which issue this closes, and flag that the branch should be renamed to include the number.
- If the issue doesn't already record which branch implements it, backfill the link with `gh issue comment <number>` and a one-line ``Refactored on branch `<branch>` ``.

The diff is `git diff main...HEAD`, three-dot, against the merge-base, on that branch. Substitute the base the user names if it isn't `main`. Confirm the branch resolves, the diff is non-empty, and the diff adds exactly one acceptance file. If one fails, stop and name it. Find the runner command for the whole suite.

The **module scope** is every non-test source file the diff changes, plus each one's module test file. Step 4 works inside it, and so does `unit-test-ticket`.

**Completion criterion:** ticket fetched, all three checks pass, suite command found, module scope listed.

## 2. True-to-spec

**Make no edits in this step.** Work through the ticket's expected behaviour one item at a time:

- **Is a test true to it?** Find the acceptance test covering it. A test that asserts something weaker, stubs out the behaviour it should exercise, or is a **tautological test** per `../unit-test-ticket/test-standards.md` is not true to spec, green or not. A tautological test is a finding here only when it is the behaviour's sole cover. The rest are `unit-test-ticket`'s to delete.
- **Is it covered at all?** A behaviour the ticket asked for with no test behind it is the worst finding here, because a green suite says otherwise.
- **Does the diff meet it?** Where no test can reach the behaviour, read the code against the ticket directly.
- **Did anything arrive the ticket never asked for?** Check it against Out of scope. Scope creep is a spec finding too.

**Don't run the acceptance file here.** The branch is already green against it, and you are reading for true-to-spec, not for a pass.

**Completion criterion:** every expected behaviour in the ticket accounted for, each one either true-to-spec or a named finding.

Zero findings means the spec is settled, so go to step 3. Any finding goes to the user before you refactor.

### Spec findings

Print the findings as the **True-to-spec** table from step 8 and nothing else, then ask the user whether to fix the acceptance **tests** so they're true to the ticket. Only the tests. The ticket body is the single source of truth and is never edited here, and neither is a signature already settled on the branch.

With their go-ahead, fix the tests and run the acceptance file:

- **Still green.** The implementation was right and the test was merely thin. Continue to step 3.
- **Now red.** The weak test was hiding a real gap, and a red branch is not yours to refactor. Taking it green is `implement-ticket`'s job. Hand the failing tests back and wait.

## 3. Reconcile the suite

Run the whole suite. `implement-ticket` ran only the acceptance file, so this is the first time the ticket meets every test written before it. Every red test outside the acceptance file is one of two things, and the acceptance file tells them apart:

- **Stale.** An acceptance test asserts the contrary. **The newest requirement is the truth**, so rewrite the old test to it, or delete it where the acceptance test now covers the same thing. No approval needed; the ticket already decided this when the user filed it.
- **A regression.** No acceptance test contradicts it, so the ticket never asked for this behaviour to change and the implementer broke it. Fix it inline when the fix stays behind the settled interface, no signature touched. A regression fix is not a refactor, so commit it on its own as `Fix #<N>: <what broke>`. Stop and ask when the fix would need a signature change or a behaviour the ticket doesn't cover. That is a contract problem, and taking it back through `/architect-ticket` is the user's call.

**Completion criterion:** the whole suite is green, and every test that was red has a Reconciled row naming it stale or a regression.

## 4. The module halt

Every question about what counts as public goes to the user here, all at once, before code or tests move. The definitions are `code-standards.md`'s **Leaky public interface** entry and the **Test rules** in `../unit-test-ticket/test-standards.md`.

List, across the module scope:

- every function Leaky public interface escalates,
- every test that calls a private function or reads a private field, counting helpers step 5 is about to make private,
- every other structure-sensitive test.

Give each a recommendation. A function gets public or private with the reason. A test gets **delete** by default, because a helper has no contract of its own. Recommend **rewrite** through the public interface only when deleting would leave a behaviour a caller can see untested, and **keep** only when the user rules its function public.

Nothing listed means no question, so go to step 5. Otherwise print the list as one table, `Item | Kind | Recommendation`, capped like the step 8 tables, ask, and wait.

With the answers, apply every test change, break check each rewrite per `test-standards.md`, and run the whole suite. No code has moved since step 3, so red means a rewrite is wrong or found a real bug. Fix a wrong rewrite; take a real bug to the user. On green, commit as `Tests #<N>: module halt`.

**Completion criterion:** every listed item has the user's answer applied, every rewrite observed red in its break check, the suite green, one commit. Or nothing was listed.

## 5. Refactor

Edit the code directly.

Three tiers, read per `../architect-ticket/RECORD-FORMAT.md`:

1. **PCRs in `docs/pcr/`** hold the project conventions. A breach is a **hard violation**. Fix the code, cite `PCR-NNNN` in the report, and never touch the file. A PCR you disagree with is not a finding. It binds until a `/challenge-pcr` session says otherwise, so fix the code to comply, say so in one line, and point the user at `/challenge-pcr` as separate work.
2. **ADRs in `docs/adr/`** hold the design decisions. A breach is a hard violation too. Fix it and cite `ADR-NNNN`. Nothing pre-selects them, so take the whole set and judge yourself which the changed files fall under. Read each one's **Decision** for what's required and its **Consequence** for what a breach looks like in a diff.
   - **Amend an ADR only when it contradicts a signature already settled on this branch.** The architect settled that signature with the user and it is frozen, so the record is what moves. Amend it per the format file. Any other disagreement with an ADR is fixed in the code and reported, not amended.
   - **Write a new ADR when the diff introduces a shape neighbouring code will copy** and no record names it: a new layer, a new kind of module, a dependency direction the first of its kind establishes. Run it through the ADR tests in the format file. Most refactors write none.
   - If the diff itself adds a file under `docs/adr/` or `docs/pcr/`, it is the architect's and you leave it alone.
   - If neither directory exists, this step runs on the baseline alone, and the Records table collapses to `**Records** no docs/pcr/ or docs/adr/`.
3. **The baseline in `code-standards.md`** applies everywhere no record covers. It carries its own gates for deciding which entries a given codebase has, and applying them is yours.

Two standing rules, over all three tiers:

- **Tests are frozen.** Step 4 already settled the tests this step's visibility changes would break, and `unit-test-ticket` handles every other test change. Never edit a test from here on.
- **A refactor never changes behaviour.** If a caller would see the difference, it is not a refactor. Leave the code alone and report it as a finding for the user.

**Completion criterion:** every changed non-test file has been read against the whole `docs/pcr/` and `docs/adr/` sets and every applicable entry in `code-standards.md`, and each finding is either fixed or recorded as a deliberate non-fix with a reason.

## 6. Update the docs

1. **`CONTEXT.md`** at the project root, if it exists. Skip if not, and never create one. Revise the Language and Relationships entries where the branch introduced or shifted a domain term.
2. **`README.md`** only if the branch alters something a new contributor needs to run or use the project: a new entry point, a new install or run command, changed configuration. Skip internal-only changes and invent nothing.

Judge both against the whole branch diff, not just your refactor edits.

**Completion criterion:** both files checked, each either edited or recorded unchanged in the report.

## 7. Re-run and commit

Run the whole suite:

- **All green.** Commit the refactor, the docs, and any record together as one commit on the branch, so the refactor stays separately readable from the rest of the branch. Subject: `Refactor: <ticket title>`. An amended ADR adds one line under the body, `Amends ADR-0003: <why, one line>`, since the file carries no history. Don't push unless the user asks.
- **Back to red.** The break is yours, and code that turned a test red was not a refactor. Fix or revert it, then re-run.

## 8. Report

Eight tables, in this order, same shape throughout.

- **Findings only.** No hit, no row. Never narrate what you checked, never wrap a table in prose.
- **Empty collapses.** A table with no rows becomes one line, `**Code smells** none`. Nothing follows it.
- **Cap every cell.** Middle column 6 words, last column 8. No sentences, no trailing periods. Truncate a deep path from the left, `.../handlers/order.ts:17`.

**True-to-spec**

| Behaviour | Test | Problem |
|---|---|---|
| discount shown per line | `test_discount_rate` | asserts total, not rate |
| refunds partial orders | none | uncovered |

**Reconciled**

| Test | Verdict | Change |
|---|---|---|
| `test_discount_flat` | stale, contra `test_discount_rate` | rewritten to rate |
| `test_tax_rounding` | regression | fixed `src/tax.py:40` |

**Records**

| File | Record | Fix |
|---|---|---|
| `src/order.ts:17` | ADR-0004, no DB in handlers | query moved to `OrderRepository` |
| `src/order.ts:3` | PCR-0002, no ORM imports | rewritten to `db.query` |
| `src/repos/` | none | ADR-0009 written, repositories own SQL |

**Code smells**

| File | Smell | Fix |
|---|---|---|
| `src/pricing.ts:42` | duplicated code (6.4) | extracted `applyDiscount`, 2 call sites |

**Architecture**

| File | Issue | Fix |
|---|---|---|
| `src/ui/cart.ts:8` | presentation past controller (5.3) | data returned from `CartController` |

**Tests**

Every test change from step 4.

| Test | Rule | Action |
|---|---|---|
| `test_cart_items` | structure-sensitive | rewritten to `total()` |
| `test_apply_rate` | private access | deleted, user approved |

**Found, not fixed**

| File | Issue | Why |
|---|---|---|
| `src/tax.ts:60` | feature envy (6.4) | fix changes behaviour |

**Spec fixes**

| Behaviour | Test | Change |
|---|---|---|
| discount shown per line | `test_discount_rate` | added rate assertion, user approved |

Close with five lines, then one line handing off: ``Next, run `/unit-test-ticket` in a fresh session.`` Nothing follows them except `gloss-me`'s footer. A new term in a table gets its gloss in a `gloss-me` block before that table.

The five lines:

```
Changes  7 across 4 files
Records  ADR-0009 written, ADR-0003 amended
Docs     CONTEXT.md updated, README.md unchanged
Commits  fix b0c1d2e, halt c9d8e7f, refactor a1b2c3d
Tests    suite green, 2 reconciled, 2 changed at module halt
```
