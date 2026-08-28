---
name: review-diff
description: Clean up the committed diff before it's pushed. First gate it true-to-spec, confirming the acceptance tests genuinely test the acceptance criteria, then edit the code into line with the rule-ADRs in `docs/adr/` and the `code-standards.md` baseline, and report what was found and how it was fixed. Use when the user finishes work, says "review-diff", "review the diff", "clean up this branch", or "run the code-review session".
---

# review-diff

The last station on the board, run when changes are ready to push. The implementer had wide freedom in *how* the code got written, so this session is **cleanup**. You don't just judge the diff, you fix it.

Two passes, in order, and the first gates the second:

1. **True-to-spec.** The acceptance tests genuinely test the acceptance criteria, and the code satisfies them. Read-only.
2. **Cleanup.** Edit the code into line with the rule-ADRs in `docs/adr/` and this skill's own `code-standards.md` baseline.

Cleaning code that's wrong spec-wise is wasted work, so pass 1 exists to prove only cleaning is left.

## 1. Pin the work, the diff, and the affected tests

Find the source of truth for this change, either a plan or an issue:

**Plan-backed.** The invocation says `plan N.N`, or a plan file in `implementation_plans/` matches the work. Read `**Branch:**`, `## Public interface`, and `## Acceptance criteria` from it. Each `AC-N` names its test in a `Verify:` line, and Verification already ran them green.

**Issue-only.** There is no plan. The branch under review carries its **GitHub issue number** in the name, following the branch-naming convention every issue publishes. Take the current branch, or the one the user names, extract the number, and fetch it with `gh issue view <number>`. Its acceptance criteria are the contract, and **no Verification ran**, so nothing is known-green yet.

- If the branch name carries no issue number, the convention was skipped. Ask the user which issue this closes, and flag that the branch should be renamed to include the number.
- If the issue doesn't already record which branch implements it, backfill the link with `gh issue comment <number>` and a one-line ``Reviewed on branch `<branch>` ``.

Then, both ways: the diff under review is `git diff main...HEAD`, three-dot, against the merge-base, on that branch. Substitute the base the user names if it isn't `main`. Confirm the branch resolves and the diff is non-empty before going further.

### The affected tests

The **affected tests** are the only tests this session runs, in either pass. Build the list from the diff before running anything:

1. Every test named in an AC `Verify:` line, or on the issue-only path, every test that claims to cover a criterion.
2. Every existing test that reaches a file the diff changes. Grep the test tree for each changed file's import path, module name, and exported symbols.
3. Every test file the diff itself adds or edits.

**Never run the whole suite.** A test over code the diff doesn't touch re-proves what the base branch already proved, and its runtime buys nothing. If you can't resolve which tests cover a changed file, widen to the nearest enclosing test directory, not to the suite, and give it a **Found, not fixed** row.

A changed non-test file that no test reaches is a finding, not a reason to widen. Record it under **Found, not fixed**.

**Completion criterion:** every changed non-test file is mapped either to the tests that reach it or to the uncovered list, and you can name the exact command that runs the affected tests and nothing else.

## 2. Pass one, true-to-spec

**Make no edits in this pass.** Work through the acceptance criteria one at a time:

- **Is the test true to the criterion?** Read the test named in the AC's `Verify:` line on the plan-backed path, or the test that claims to cover it on the issue-only path. A test that asserts something weaker than the criterion, stubs out the behaviour it should exercise, or passes vacuously is **not** true to spec, green or not.
- **Does the diff meet the criterion?** For `(manual)` criteria and anything no test covers, read the code against the AC directly.
- **Did anything arrive that no criterion asked for?** Scope creep is a spec finding too.

On the plan-backed path, **don't run the AC tests here**. Verification already ran them, and you're reading for faithfulness. On the issue-only path, nothing gated them, so run the affected tests once.

**Completion criterion:** every acceptance criterion accounted for, each one either true-to-spec or a named finding.

Zero findings means the spec is settled, so go to pass 2. Any finding means **halt**.

### The spec halt

Stop, print the findings as the **True-to-spec** table from step 5 and nothing else, then ask the user whether to fix the acceptance **tests** so they're true to their criteria. Only the tests. The AC text itself is the plan's or issue's single source of truth and is never edited here.

With their go-ahead, fix the tests and run the affected tests:

- **Still green.** The implementation was right and the test was merely thin. Continue to pass 2.
- **Now red.** The weak test was hiding a real gap. **Stop here.** Closing that gap is implementation work, not cleanup, so hand the failing tests back to a fresh implementer and wait. Don't implement it yourself.

## 3. Pass two, cleanup

Edit the code directly. This pass produces changes, not a list of suggestions.

Two tiers:

1. **Rule-ADRs in `docs/adr/`** hold the enforceable rules, in `**Rule:** … **How to check:** …` form. A breach is a **hard violation**: fix it, and cite `ADR-NNNN` in the report. No plan pre-selects rules, so take the **whole `docs/adr/` set** and judge yourself which rules the changed files fall under.
   - If the diff itself modifies files under `docs/adr/`, meaning a rule was added or amended during the work, flag it for the user rather than acting on it.
   - If `docs/adr/` doesn't exist, this pass runs on the baseline alone. The Rule-ADRs table collapses to `**Rule-ADRs** no docs/adr/`.
2. **The baseline in `code-standards.md`** applies everywhere no ADR covers, and **any rule-ADR overrides it**. It ships with this skill, so read it from the skill's own directory, the file sitting beside this `SKILL.md`. Never search the repo for it, and if the repo holds a file by that name, it is not this one. Read it before you edit anything in this pass. It carries its own gates for deciding which entries a given codebase has, and applying them is yours.

Two standing exemptions, over both tiers:

- **Tests are exempt.** A test that is true to its AC stays as written, duplication, long setup and all. Only a rule-ADR that explicitly governs tests touches them.
- **Cleanup never changes behaviour.** If a fix would alter what the code does, it isn't cleanup. Leave the code alone and report it as a finding for the user.

**Completion criterion:** every changed non-test file has been read against the whole `docs/adr/` set and every applicable entry in `code-standards.md`, and each hit is either fixed or recorded as a deliberate non-fix with a reason.

## 4. Re-run and commit

The affected tests are the safety net under the refactor. Run all of them, and only them:

- **All green.** Commit the cleanup as its own commit on the branch, so the implementer's work and the cleanup stay separately readable. Subject: `Cleanup: <plan title or issue title>`. Don't push unless the user asks.
- **Any red.** The break is yours, not the implementer's. Fix or revert the cleanup edit that caused it, then re-run. Never amend a test to accommodate a cleanup edit.

## 5. Report

A checklist, not a report. Seven tables, in this order, same shape throughout.

- **Findings only.** No hit, no row. Never narrate what you checked, never wrap a table in prose.
- **Empty collapses.** A table with no rows becomes one line, `**Code smells** none`. Nothing follows it.
- **Cap every cell.** Middle column 6 words, last column 8. No sentences, no trailing periods. Truncate a deep path from the left, `.../handlers/order.ts:17`.

**True-to-spec**

| AC | Test | Problem |
|---|---|---|
| AC-3 | `test_discount_rate` | asserts total, not rate |

**Rule-ADRs**

| File | ADR | Fix |
|---|---|---|
| `src/order.ts:17` | ADR-0004, no DB in handlers | query moved to `OrderRepository` |

**Code smells**

| File | Smell | Fix |
|---|---|---|
| `src/pricing.ts:42` | duplicated code (6.4) | extracted `applyDiscount`, 2 call sites |

**Architecture**

| File | Issue | Fix |
|---|---|---|
| `src/ui/cart.ts:8` | presentation past controller (5.3) | data returned from `CartController` |

**Tests**

Report only, never fixed.

| File | Rule | Note |
|---|---|---|
| `test_order.py:30` | too many assertions (7.5) | 5 asserts, split |

**Found, not fixed**

| File | Issue | Why |
|---|---|---|
| `src/tax.ts:60` | feature envy (6.4) | fix changes behaviour |

**Spec fixes**

| AC | Test | Change |
|---|---|---|
| AC-3 | `test_discount_rate` | added rate assertion, user approved |

Close with three lines, nothing after them:

```
Changes  7 across 4 files
Commit   a1b2c3d
Tests    pytest tests/test_order.py tests/test_pricing.py
```
